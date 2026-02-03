
"""
データベース（SQLite）内に特定のEDINETコード（例: E35239）が登録されているか確認するスクリプト。
提出者コードテーブル（FilerCode）や提出者テーブル（Filer）を検索し、登録状況や紐付けIDを表示します。
"""

import os
import sys

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.database import get_db_session
from backend.models import Filer, FilerCode


def check_filer_code(edinet_code="E35239"):
    print(f"Checking database for {edinet_code}...")

    with get_db_session() as db:
        # FilerCodeテーブル確認
        filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()

        if filer_code:
            print("[FOUND in FilerCode]")
            print(f"  ID: {filer_code.id}")
            print(f"  Name: {filer_code.name}")
            print(f"  FilerID: {filer_code.filer_id}")

            # 親Filer確認
            filer = db.query(Filer).filter(Filer.id == filer_code.filer_id).first()
            if filer:
                print("  [Parent Filer]")
                print(f"    ID: {filer.id}")
                print(f"    Name: {filer.name}")
                print(f"    Main EdinetCode: {filer.edinet_code}")
        else:
            print(f"[NOT FOUND] {edinet_code} is not in FilerCode table.")

        # Filerテーブル直接確認（稀なケース）
        filer_direct = db.query(Filer).filter(Filer.edinet_code == edinet_code).first()
        if filer_direct:
            print("[FOUND in Filer (Direct)]")
            print(f"  ID: {filer_direct.id}")
            print(f"  Name: {filer_direct.name}")

if __name__ == "__main__":
    check_filer_code()
