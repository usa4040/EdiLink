
"""
直近の提出書類データ（CSVではなくDB経由）を読み込み、
提出日、書類種別、対象銘柄名などを分かりやすく表示・解説するスクリプト。
新しく取得されたデータの中身を簡易確認するために使用します。
"""

import os
import sys
from datetime import datetime, timedelta

# パス設定
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.database import get_db_session
from backend.models import Filing


async def explain_recent_filings(days=35):
    print(f"Analyzing filings from the last {days} days...")

    async with get_db_session() as db:
        # 直近のデータを取得
        cutoff = datetime.now() - timedelta(days=days)

        stmt = (
            select(Filing)
            .where(Filing.submit_date >= cutoff)
            .order_by(Filing.submit_date.desc())
            .options(joinedload(Filing.filer), joinedload(Filing.issuer))
        )
        result = await db.execute(stmt)
        filings = result.scalars().all()

        print(f"Found {len(filings)} filings.")

        for f in filings:
            # 提出者名（今回のコンテキストでは光通信関連と仮定しているが、念のため確認）
            filer = f.filer

            # 対象発行体（銘柄）
            issuer_name = "Unknown"
            if f.issuer:
                issuer_name = f.issuer.name or f.issuer.edinet_code

            # 光通信（E04948/E35239）関連のみ詳細表示
            # モデル上 filer.edinet_code はメインコード(E04948)になるので名前で判断などが確実
            if filer and "光通信" in filer.name:
                print(f"\n[Date: {f.submit_date}] DocID: {f.doc_id}")
                print(f"  Type: {f.doc_description}")
                print(f"  Target Issuer: {issuer_name}")
                # csv_flagがあれば簡易的に中身についての言及も可能だが今回は概要のみ


if __name__ == "__main__":
    asyncio.run(explain_recent_filings())
