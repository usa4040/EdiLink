"""
非同期テスト設定（PostgreSQL対応）
"""

import os
import sys

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import get_db
from backend.main import app
from backend.models import Base

# テスト用の非同期データベースエンジン
# 環境変数から取得、またはデフォルトのPostgreSQL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://edinet:edinet@localhost:5432/edinet_test"
)

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
async def db():
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
async def client(db):
    """FastAPIの非同期テストクライアントを提供。DBの依存性をオーバーライド"""

    async def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# 後方互換性のための同期版フィクスチャ（移行期間中）
@pytest.fixture(scope="function")
def sync_db():
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


@pytest.fixture(scope="function")
def sync_client(sync_db):
    """同期版テストクライアント（既存テストの互換性用）"""
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield sync_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
