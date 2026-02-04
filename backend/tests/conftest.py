"""
非同期テスト設定（PostgreSQL対応）
"""

import os
import sys
from collections.abc import AsyncGenerator, Generator
from typing import Any

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.cache import init_cache
from backend.database import get_db
from backend.main import app
from backend.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def setup_cache() -> AsyncGenerator[None, None]:
    """テストセッション開始時にキャッシュを初期化"""
    await init_cache()
    yield


# テスト用の非同期データベースエンジン
# 環境変数から取得、またはデフォルトのPostgreSQL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://edinet:edinet@localhost:5432/edinet_test")

# 非同期エンジン（テスト用）
test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # テスト時は接続プールを使用しない
)

# 非同期セッションファクトリ
TestingSessionLocal = async_sessionmaker(
    test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """テストごとにクリーンな非同期DBセッションを提供"""
    # テーブル作成
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # セッション作成
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    # テーブル削除
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """FastAPIの非同期テストクライアントを提供。DBの依存性をオーバーライド"""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# 後方互換性のための同期版フィクスチャ（移行期間中）
@pytest.fixture(scope="function")
def sync_db() -> Generator[Session, None, None]:
    """同期版DBセッション（既存テストの互換性用）"""
    from backend.database import SyncSessionLocal, sync_engine
    from backend.models import Base as SyncBase

    SyncBase.metadata.create_all(bind=sync_engine)
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
        SyncBase.metadata.drop_all(bind=sync_engine)


@pytest_asyncio.fixture(scope="function")
async def sample_data(db: AsyncSession) -> dict[str, Any]:
    """基本的なサンプルデータを作成"""
    from datetime import UTC, datetime

    from backend.models import Filer, FilerCode, Filing, HoldingDetail, Issuer

    filer = Filer(edinet_code="E00000", name="テスト提出者", sec_code="90000")
    db.add(filer)
    await db.flush()

    filer_code = FilerCode(filer_id=filer.id, edinet_code="E00000", name="テスト提出者")
    db.add(filer_code)

    issuer = Issuer(edinet_code="E11111", name="テスト発行体", sec_code="10010")
    db.add(issuer)
    await db.flush()

    filing = Filing(
        doc_id="S_TEST_01",
        filer_id=filer.id,
        issuer_id=issuer.id,
        doc_description="大量保有報告書",
        submit_date=datetime.now(UTC),
        csv_flag=True,
    )
    db.add(filing)
    await db.flush()

    holding = HoldingDetail(filing_id=filing.id, shares_held=1000000, holding_ratio=5.50)
    db.add(holding)
    await db.commit()

    return {
        "filer": filer,
        "filer_code": filer_code,
        "issuer": issuer,
        "filing": filing,
        "holding": holding,
    }


@pytest.fixture(scope="function")
def sync_client(sync_db: Session) -> Generator[Any, None, None]:
    """同期版テストクライアント（既存テストの互換性用）"""
    from fastapi.testclient import TestClient

    def override_get_db() -> Generator[Any, None, None]:
        try:
            yield sync_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
