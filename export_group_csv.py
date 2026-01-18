
"""
親会社IDに基づいて、関連する全ての提出者コード（例: E04948とE35239）のデータをまとめてCSV出力するツール。
同一法人として管理されている複数のEDINETコードの提出書類を統合して確認するために使用します。
"""

import sys
import os
import csv
import argparse
from datetime import datetime

# パス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import FilerCode, Filing, Filer, get_engine
from backend.database import get_db_session

def export_filer_group_csv(edinet_code, output_file=None):
    if not output_file:
        output_file = f"{edinet_code}_group_filings.csv"

    with get_db_session() as db:
        # Filer特定 (E04948から親IDを特定)
        start_code = db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()
        if not start_code:
            print(f"Filer not found for code: {edinet_code}")
            return

        filer_id = start_code.filer_id
        filer = db.query(Filer).filter(Filer.id == filer_id).first()
        
        print(f"Exporting ALL filings for filer: {filer.name} (ID: {filer_id})...")

        # このFiler IDに紐づく全書類を取得
        filings = db.query(Filing).filter(
            Filing.filer_id == filer_id
        ).order_by(Filing.submit_date.desc()).all()

        if not filings:
            print("No filings found.")
            return

        # CSV書き出し
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
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
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # 簡易的に30日以内
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=30)
        
        print(f"\n--- Recent Filings (Since {cutoff.strftime('%Y-%m-%d')}) ---")
        for f in filings:
            if f.submit_date >= cutoff:
                print(f"{f.submit_date}: {f.doc_description} ({f.doc_id})")
                recent_count += 1
        
        print(f"\nTotal recent filings found: {recent_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export filings for a filer group to CSV")
    parser.add_argument("edinet_code", type=str, help="Main EDINET Code (e.g., E04948)")
    parser.add_argument("--out", type=str, help="Output CSV filename")
    
    args = parser.parse_args()
    
    export_filer_group_csv(args.edinet_code, args.out)
