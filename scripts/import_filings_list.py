"""
CSVファイルをデータベースにインポートするスクリプト
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import select

from backend.database import async_engine, get_db_session
from backend.models import Base, Filer, Filing, Issuer


async def import_csv_to_db(csv_path: str):
    """CSVファイルからデータをDBにインポート"""

    # データベース初期化
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # CSV読み込み
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from CSV")

    async with get_db_session() as db:
        # 1. 提出者（Filer）を登録
        filer_codes = df['edinetCode'].unique()
        for code in filer_codes:
            f_stmt = select(Filer).where(Filer.edinet_code == code)
            existing = (await db.execute(f_stmt)).scalar_one_or_none()
            if not existing:
                row = df[df['edinetCode'] == code].iloc[0]
                filer = Filer(
                    edinet_code=code,
                    name=row.get('filerName', ''),
                    sec_code=str(row.get('secCode', '')) if pd.notna(row.get('secCode')) else None,
                    jcn=str(row.get('JCN', '')) if pd.notna(row.get('JCN')) else None
                )
                db.add(filer)
                print(f"Added Filer: {filer.name} ({code})")
        await db.flush()

        # 2. 発行体（Issuer）を登録
        issuer_codes = df["issuerEdinetCode"].dropna().unique()
        for code in issuer_codes:
            if not code or str(code) == "nan":
                continue
            i_stmt = select(Issuer).where(Issuer.edinet_code == code)
            existing = (await db.execute(i_stmt)).scalar_one_or_none()
            if not existing:
                new_issuer = Issuer(
                    edinet_code=code,
                    name=None,  # 後で取得
                    sec_code=None,
                )
                db.add(new_issuer)
                print(f"Added Issuer: {code}")
        await db.flush()

        # 3. 報告書（Filing）を登録
        for _, row in df.iterrows():
            doc_id = row['docID']
            fi_stmt = select(Filing).where(Filing.doc_id == doc_id)
            existing = (await db.execute(fi_stmt)).scalar_one_or_none()
            if existing:
                continue

            # Filerを取得
            f_get_stmt = select(Filer).where(Filer.edinet_code == row["edinetCode"])
            filer = (await db.execute(f_get_stmt)).scalar_one_or_none()

            # Issuerを取得
            issuer: Optional[Issuer] = None
            issuer_code = row.get("issuerEdinetCode")
            if pd.notna(issuer_code) and issuer_code:
                i_get_stmt = select(Issuer).where(Issuer.edinet_code == issuer_code)
                issuer = (await db.execute(i_get_stmt)).scalar_one_or_none()

            # 提出日時のパース
            submit_date = None
            if pd.notna(row.get('submitDateTime')):
                try:
                    submit_date = datetime.strptime(str(row['submitDateTime']), '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass

            filing = Filing(
                doc_id=doc_id,
                filer_id=filer.id if filer else None,
                issuer_id=issuer.id if issuer else None,
                doc_type=row.get('formCode'),
                doc_description=row.get('docDescription'),
                submit_date=submit_date,
                parent_doc_id=row.get('parentDocID') if pd.notna(row.get('parentDocID')) else None,
                csv_flag=bool(row.get('csvFlag', 0)),
                xbrl_flag=bool(row.get('xbrlFlag', 0)),
                pdf_flag=bool(row.get('pdfFlag', 0))
            )
            db.add(filing)

        print("Import completed!")


if __name__ == "__main__":
    csv_path = "hikari_filings_list.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    asyncio.run(import_csv_to_db(csv_path))
