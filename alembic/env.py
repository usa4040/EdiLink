"""
Alembic環境設定ファイル（非同期PostgreSQL対応）

このファイルはAlembicのマイグレーション環境を設定します。
非同期SQLAlchemyを使用していますが、Alembicは同期的に動作するため、
同期的なデータベースURLに変換して使用します。
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from alembic import context

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLAlchemyモデルのインポート
from backend.models import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_sync_database_url() -> str:
    """
    環境変数DATABASE_URLから同期的なデータベースURLを取得します。

    asyncpgドライバーをpsycopg2（または標準postgresql）に変換します。

    Returns:
        str: 同期用のPostgreSQL接続URL
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://edinet:edinet@localhost:5432/edinet"
    )

    # asyncpg -> psycopg2 (または標準postgresql) に変換
    if "postgresql+asyncpg" in database_url:
        # psycopg2-binaryを使用
        database_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    elif database_url.startswith("postgresql://"):
        # すでに標準形式の場合はそのまま使用
        pass
    elif database_url.startswith("postgres://"):
        # Railway等、古い形式のURLを変換
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

    return database_url


def run_migrations_offline() -> None:
    """
    オフラインモードでマイグレーションを実行します。

    'offline' mode migrates the database without creating an Engine.
    This is useful when the database URL is not available at runtime,
    or when we want to generate SQL scripts instead of executing migrations.
    """
    url = get_sync_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLAlchemy 2.0 スタイルの型注釈をサポート
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    データベース接続を使用してマイグレーションを実行します。

    Args:
        connection: SQLAlchemyのデータベース接続
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # SQLAlchemy 2.0 スタイルの型注釈をサポート
        render_as_batch=True,
        # 型注釈を含める
        include_schemas=True,
        # カスタム型の比較を有効化
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    オンラインモードでマイグレーションを実行します。

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    # 同期的なデータベースURLを取得
    sync_database_url = get_sync_database_url()

    # 同期エンジンを作成
    connectable = create_engine(
        sync_database_url,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


# メインの実行ブロック
if context.is_offline_mode():
    print("Running migrations in offline mode...")
    run_migrations_offline()
else:
    print("Running migrations in online mode...")
    run_migrations_online()
