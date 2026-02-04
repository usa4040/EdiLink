
"""
データベース（SQLite）内に特定のEDINETコード（例: E35239）が登録されているか確認するスクリプト。
提出者コードテーブル（FilerCode）や提出者テーブル（Filer）を検索し、登録状況や紐付けIDを表示します。
"""

import os
import sys

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import asyncio

from sqlalchemy import select

from backend.database import get_db_session
from backend.models import Filer, FilerCode


async def check_filer_code(edinet_code="E35239"):
    print(f"Checking database for {edinet_code}...")

    async with get_db_session() as db:
        # FilerCodeテーブル確認
        fc_stmt = select(FilerCode).where(FilerCode.edinet_code == edinet_code)
        filer_code = (await db.execute(fc_stmt)).scalar_one_or_none()

        if filer_code:
            print("[FOUND in FilerCode]")
            print(f"  ID: {filer_code.id}")
            print(f"  Name: {filer_code.name}")
            print(f"  FilerID: {filer_code.filer_id}")

            # 親Filer確認
            f_stmt = select(Filer).where(Filer.id == filer_code.filer_id)
            filer = (await db.execute(f_stmt)).scalar_one_or_none()
            if filer:
                print("  [Parent Filer]")
                print(f"    ID: {filer.id}")
                print(f"    Name: {filer.name}")
                print(f"    Main EdinetCode: {filer.edinet_code}")
        else:
            print(f"[NOT FOUND] {edinet_code} is not in FilerCode table.")

        # Filerテーブル直接確認（稀なケース）
        fd_stmt = select(Filer).where(Filer.edinet_code == edinet_code)
        filer_direct = (await db.execute(fd_stmt)).scalar_one_or_none()
        if filer_direct:
            print("[FOUND in Filer (Direct)]")
            print(f"  ID: {filer_direct.id}")
            print(f"  Name: {filer_direct.name}")

if __name__ == "__main__":
    asyncio.run(check_filer_code())
