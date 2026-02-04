
"""
親会社IDに基づいて、関連する全ての提出者コード（例: E04948とE35239）のデータをまとめてCSV出力するツール。
同一法人として管理されている複数のEDINETコードの提出書類を統合して確認するために使用します。
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta

# パス設定
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import asyncio

from sqlalchemy import select

from backend.database import get_db_session
from backend.models import Filer, FilerCode, Filing


async def export_filer_group_csv(edinet_code, output_file=None):
    if not output_file:
        # デフォルトの出力先を exports/ ディレクトリに設定
        output_file = os.path.join(project_root, "exports", f"{edinet_code}_group_filings.csv")

    async with get_db_session() as db:
        # Filer特定 (E04948から親IDを特定)
        filer_code_stmt = select(FilerCode).where(FilerCode.edinet_code == edinet_code)
        start_code = (await db.execute(filer_code_stmt)).scalar_one_or_none()
        if not start_code:
            print(f"Filer not found for code: {edinet_code}")
            return

        filer_id = start_code.filer_id
        filer_stmt = select(Filer).where(Filer.id == filer_id)
        filer = (await db.execute(filer_stmt)).scalar_one_or_none()
        if not filer:
            print(f"Filer not found for ID: {filer_id}")
            return

        print(f"Exporting ALL filings for filer: {filer.name} (ID: {filer_id})...")

        # このFiler IDに紐づく全書類を取得
        filings_stmt = (
            select(Filing).where(Filing.filer_id == filer_id).order_by(Filing.submit_date.desc())
        )
        result = await db.execute(filings_stmt)
        filings = result.scalars().all()

        if not filings:
            print("No filings found.")
            return

        # ディレクトリの作成を保証
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # CSV書き出し
        with open(output_file, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            header = [
                "doc_id", "submit_date", "doc_type", "doc_description",
                "filer_code_used", "ordinance"
            ]
            writer.writerow(header)

            for filing in filings:
                # 提出時点で使用されたコードはFilerCodeテーブルから逆引きできないか、
                # あるいは簡易的に表示（ここでは詳細スキップ）
                writer.writerow([
                    filing.doc_id,
                    filing.submit_date,
                    filing.doc_type,
                    filing.doc_description,
                    "---", # 今のモデル構造だと提出時の具体的なEDINETコードまでは保持していない可能性あり
                    "-"    # ordinanceもFilingモデルにない場合は省略
                ])

        print(f"Exported {len(filings)} records to {output_file}")

        # 直近30日の件数表示
        recent_count = 0
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)

        print(f"\n--- Recent Filings (Since {cutoff.strftime('%Y-%m-%d')}) ---")
        for filing in filings:
            if filing.submit_date and filing.submit_date >= cutoff:
                print(f"{filing.submit_date}: {filing.doc_description} ({filing.doc_id})")
                recent_count += 1

        print(f"\nTotal recent filings found: {recent_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export filings for a filer group to CSV")
    parser.add_argument("edinet_code", type=str, help="Main EDINET Code (e.g., E04948)")
    parser.add_argument("--out", type=str, help="Output CSV filename")

    args = parser.parse_args()

    asyncio.run(export_filer_group_csv(args.edinet_code, args.out))
