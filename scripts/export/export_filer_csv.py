
"""
データベース内の提出書類データを、特定の提出者EDINETコードに基づいてCSV出力するツール。
指定したコード（例: E04948）に紐づくデータを抽出し、hikari_latest.csvなどを作成します。
"""

import argparse
import csv
import os
import sys

# パス設定
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.database import get_db_session
from backend.models import FilerCode, Filing


def export_filer_csv(edinet_code, output_file=None):
    if not output_file:
        # デフォルトの出力先を exports/ ディレクトリに設定
        output_file = os.path.join(project_root, "exports", f"{edinet_code}_filings.csv")

    with get_db_session() as db:
        # Filer特定
        filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()
        if not filer_code:
            print(f"Filer not found for code: {edinet_code}")
            return

        print(f"Exporting filings for {filer_code.name} ({edinet_code})...")

        # 書類取得
        filings = db.query(Filing).filter(
            Filing.filer_id == filer_code.filer_id
        ).order_by(Filing.submit_date.desc()).all()

        if not filings:
            print("No filings found.")
            return

        # ディレクトリの作成を保証
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # CSV書き出し
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            header = [
                "doc_id", "submit_date", "doc_type", "doc_description",
                "xbrl_flag", "pdf_flag", "csv_flag"
            ]
            writer.writerow(header)

            for filing in filings:
                writer.writerow([
                    filing.doc_id,
                    filing.submit_date,
                    filing.doc_type,
                    filing.doc_description,
                    filing.xbrl_flag,
                    filing.pdf_flag,
                    filing.csv_flag
                ])

        print(f"Exported {len(filings)} records to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export filings for a filer to CSV")
    parser.add_argument("edinet_code", type=str, help="EDINET Code (e.g., E04948)")
    parser.add_argument("--out", type=str, help="Output CSV filename")

    args = parser.parse_args()

    export_filer_csv(args.edinet_code, args.out)
