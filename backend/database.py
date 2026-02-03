"""
データベース接続設定（非同期PostgreSQL対応）
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 環境変数からデータベースURLを取得（デフォルトはPostgreSQL）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://edinet:edinet@localhost:5432/edinet")

# 非同期エンジンの作成
async_engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "0") == "1",  # デバッグ時のみSQLログ出力
    future=True,
)

# 非同期セッションファクトリ
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPIの依存性注入用

    Yields:
        AsyncSession: 非同期データベースセッション
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session():
    """
    スクリプト用の非同期コンテキストマネージャ

    Usage:
        async with get_db_session() as db:
            result = await db.execute(select(Filer))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 後方互換性のための同期版（スクリプト移行用）
# 移行完了後に削除予定
from contextlib import contextmanager
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

# SQLite用の同期エンジン（データ移行時のみ使用）
_sqlite_url = os.getenv("SQLITE_URL", "sqlite:///data/edinet.db")
sync_engine = create_engine(_sqlite_url, connect_args={"check_same_thread": False})
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


@contextmanager
def get_sync_db_session():
    """
    スクリプト用の同期コンテキストマネージャ

    Usage:
        with get_sync_db_session() as db:
            result = db.execute(select(Filer))
    """
    session: Session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
