"""
SQLiteからPostgreSQLへのデータ移行スクリプト

Usage:
    python scripts/migrate_sqlite_to_postgres.py

環境変数:
    SQLITE_URL: SQLiteデータベースURL（デフォルト: sqlite:///data/edinet.db）
    DATABASE_URL: PostgreSQLデータベースURL（デフォルト: postgresql+asyncpg://edinet:edinet@localhost:5432/edinet）
"""

import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# プロジェクトルートをPythonパスに追加
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import AsyncSessionLocal, sync_engine
from backend.models import Base, Filer, FilerCode, Issuer, Filing, HoldingDetail


# 環境変数
SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///data/edinet.db")
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://edinet:edinet@localhost:5432/edinet"
)

# 移行済みを記録するファイル
MIGRATION_MARKER = ".migration_completed"


def get_sqlite_connection() -> sqlite3.Connection:
    """SQLite接続を取得"""
    # URLからファイルパスを抽出
    if SQLITE_URL.startswith("sqlite:///"):
        db_path = SQLITE_URL.replace("sqlite:///", "")
    else:
        db_path = SQLITE_URL.replace("sqlite://", "")
    
    # 絶対パスの場合はそのまま、相対パスの場合は調整
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
    
    return sqlite3.connect(db_path)


def parse_datetime(value: Any) -> datetime:
    """SQLiteのdatetime文字列をPython datetimeに変換"""
    if value is None:
        return None
    if isinstance(value, datetime):
        # タイムゾーンがない場合はUTCを設定
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        # ISOフォーマット文字列をパース
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None
    return None


async def check_migration_needed() -> bool:
    """移行が必要かどうかをチェック"""
    # PostgreSQLに既存データがあるかチェック
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Filer).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing is not None:
            print("ℹ️  PostgreSQLに既存データがあります。移行をスキップします。")
            return False
    
    # SQLiteファイルが存在するかチェック
    if SQLITE_URL.startswith("sqlite:///"):
        db_path = SQLITE_URL.replace("sqlite:///", "")
    else:
        db_path = SQLITE_URL.replace("sqlite://", "")
    
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
    
    if not os.path.exists(db_path):
        print(f"ℹ️  SQLiteファイルが見つかりません: {db_path}")
        print("ℹ️  初期データなしで開始します。")
        return False
    
    return True


async def migrate_filers(sqlite_cursor: sqlite3.Cursor, session: AsyncSession) -> None:
    """Filersテーブルの移行"""
    print("🔄 Filersテーブルの移行を開始...")
    
    sqlite_cursor.execute("SELECT id, edinet_code, name, sec_code, jcn, created_at, updated_at FROM filers")
    rows = sqlite_cursor.fetchall()
    
    filers = []
    for row in rows:
        filer = Filer(
            id=row[0],
            edinet_code=row[1],
            name=row[2],
            sec_code=row[3],
            jcn=row[4],
            created_at=parse_datetime(row[5]),
            updated_at=parse_datetime(row[6]),
        )
        filers.append(filer)
    
    if filers:
        session.add_all(filers)
        await session.flush()
        print(f"✅ {len(filers)}件のFilerを移行しました")
    else:
        print("ℹ️  移行するFilerデータがありません")


async def migrate_filer_codes(sqlite_cursor: sqlite3.Cursor, session: AsyncSession) -> None:
    """FilerCodesテーブルの移行"""
    print("🔄 FilerCodesテーブルの移行を開始...")
    
    sqlite_cursor.execute("SELECT id, filer_id, edinet_code, name, created_at FROM filer_codes")
    rows = sqlite_cursor.fetchall()
    
    filer_codes = []
    for row in rows:
        fc = FilerCode(
            id=row[0],
            filer_id=row[1],
            edinet_code=row[2],
            name=row[3],
            created_at=parse_datetime(row[4]),
        )
        filer_codes.append(fc)
    
    if filer_codes:
        session.add_all(filer_codes)
        await session.flush()
        print(f"✅ {len(filer_codes)}件のFilerCodeを移行しました")
    else:
        print("ℹ️  移行するFilerCodeデータがありません")


async def migrate_issuers(sqlite_cursor: sqlite3.Cursor, session: AsyncSession) -> None:
    """Issuersテーブルの移行"""
    print("🔄 Issuersテーブルの移行を開始...")
    
    sqlite_cursor.execute("SELECT id, edinet_code, name, sec_code, created_at, updated_at FROM issuers")
    rows = sqlite_cursor.fetchall()
    
    issuers = []
    for row in rows:
        issuer = Issuer(
            id=row[0],
            edinet_code=row[1],
            name=row[2],
            sec_code=row[3],
            created_at=parse_datetime(row[4]),
            updated_at=parse_datetime(row[5]),
        )
        issuers.append(issuer)
    
    if issuers:
        session.add_all(issuers)
        await session.flush()
        print(f"✅ {len(issuers)}件のIssuerを移行しました")
    else:
        print("ℹ️  移行するIssuerデータがありません")


async def migrate_filings(sqlite_cursor: sqlite3.Cursor, session: AsyncSession) -> None:
    """Filingsテーブルの移行"""
    print("🔄 Filingsテーブルの移行を開始...")
    
    sqlite_cursor.execute("""
        SELECT id, doc_id, filer_id, issuer_id, doc_type, doc_description, 
               submit_date, parent_doc_id, csv_flag, xbrl_flag, pdf_flag, created_at 
        FROM filings
    """)
    rows = sqlite_cursor.fetchall()
    
    filings = []
    for row in rows:
        filing = Filing(
            id=row[0],
            doc_id=row[1],
            filer_id=row[2],
            issuer_id=row[3],
            doc_type=row[4],
            doc_description=row[5],
            submit_date=parse_datetime(row[6]),
            parent_doc_id=row[7],
            csv_flag=bool(row[8]),
            xbrl_flag=bool(row[9]),
            pdf_flag=bool(row[10]),
            created_at=parse_datetime(row[11]),
        )
        filings.append(filing)
    
    if filings:
        session.add_all(filings)
        await session.flush()
        print(f"✅ {len(filings)}件のFilingを移行しました")
    else:
        print("ℹ️  移行するFilingデータがありません")


async def migrate_holding_details(sqlite_cursor: sqlite3.Cursor, session: AsyncSession) -> None:
    """HoldingDetailsテーブルの移行"""
    print("🔄 HoldingDetailsテーブルの移行を開始...")
    
    sqlite_cursor.execute("""
        SELECT id, filing_id, shares_held, holding_ratio, purpose, created_at 
        FROM holding_details
    """)
    rows = sqlite_cursor.fetchall()
    
    details = []
    for row in rows:
        detail = HoldingDetail(
            id=row[0],
            filing_id=row[1],
            shares_held=row[2],
            holding_ratio=row[3],
            purpose=row[4],
            created_at=parse_datetime(row[5]),
        )
        details.append(detail)
    
    if details:
        session.add_all(details)
        await session.flush()
        print(f"✅ {len(details)}件のHoldingDetailを移行しました")
    else:
        print("ℹ️  移行するHoldingDetailデータがありません")


async def verify_migration(sqlite_cursor: sqlite3.Cursor) -> Tuple[bool, str]:
    """移行の検証"""
    print("🔍 移行データの検証を開始...")
    
    # SQLiteのレコード数を取得
    sqlite_counts = {}
    tables = ["filers", "filer_codes", "issuers", "filings", "holding_details"]
    
    for table in tables:
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_counts[table] = sqlite_cursor.fetchone()[0]
    
    # PostgreSQLのレコード数を取得
    async with AsyncSessionLocal() as session:
        pg_counts = {}
        
        result = await session.execute(select(Filer))
        pg_counts["filers"] = len(result.scalars().all())
        
        result = await session.execute(select(FilerCode))
        pg_counts["filer_codes"] = len(result.scalars().all())
        
        result = await session.execute(select(Issuer))
        pg_counts["issuers"] = len(result.scalars().all())
        
        result = await session.execute(select(Filing))
        pg_counts["filings"] = len(result.scalars().all())
        
        result = await session.execute(select(HoldingDetail))
        pg_counts["holding_details"] = len(result.scalars().all())
    
    # 比較
    all_match = True
    discrepancies = []
    
    for table in tables:
        if sqlite_counts[table] != pg_counts[table]:
            all_match = False
            discrepancies.append(
                f"  - {table}: SQLite={sqlite_counts[table]}, PostgreSQL={pg_counts[table]}"
            )
    
    if all_match:
        return True, f"✅ すべてのテーブルでレコード数が一致しました"
    else:
        return False, "❌ レコード数の不一致:\n" + "\n".join(discrepancies)


async def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 SQLiteからPostgreSQLへのデータ移行を開始")
    print("=" * 60)
    print(f"SQLite: {SQLITE_URL}")
    print(f"PostgreSQL: {POSTGRES_URL}")
    print("=" * 60)
    
    # 移行が必要かチェック
    if not await check_migration_needed():
        print("\n⏭️  移行をスキップして終了します")
        return
    
    # SQLite接続
    print("\n📂 SQLiteに接続中...")
    try:
        sqlite_conn = get_sqlite_connection()
        sqlite_cursor = sqlite_conn.cursor()
        print("✅ SQLite接続成功")
    except Exception as e:
        print(f"❌ SQLite接続エラー: {e}")
        return
    
    try:
        # PostgreSQLへの移行
        print("\n📝 PostgreSQLへのデータ移行を開始...")
        
        async with AsyncSessionLocal() as session:
            try:
                # 各テーブルの移行
                await migrate_filers(sqlite_cursor, session)
                await migrate_filer_codes(sqlite_cursor, session)
                await migrate_issuers(sqlite_cursor, session)
                await migrate_filings(sqlite_cursor, session)
                await migrate_holding_details(sqlite_cursor, session)
                
                # コミット
                await session.commit()
                print("\n✅ すべてのデータ移行が完了し、コミットしました")
                
            except Exception as e:
                await session.rollback()
                print(f"\n❌ 移行エラー: {e}")
                raise
        
        # 検証
        print("\n" + "=" * 60)
        success, message = await verify_migration(sqlite_cursor)
        print(message)
        print("=" * 60)
        
        if success:
            print("\n🎉 データ移行が正常に完了しました！")
        else:
            print("\n⚠️  移行は完了しましたが、検証で不一致が見つかりました")
        
    except Exception as e:
        print(f"\n❌ 移行処理でエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        sqlite_conn.close()
        print("\n📂 SQLite接続を閉じました")


if __name__ == "__main__":
    asyncio.run(main())
