"""
CSVファイルをデータベースにインポートするスクリプト
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from backend.models import Base, Filer, Issuer, Filing, get_engine
from backend.database import get_db_session


def import_csv_to_db(csv_path: str):
    """CSVファイルからデータをDBにインポート"""
    
    # データベース初期化
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    # CSV読み込み
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from CSV")
    
    with get_db_session() as db:
        # 1. 提出者（Filer）を登録
        filer_codes = df['edinetCode'].unique()
        for code in filer_codes:
            existing = db.query(Filer).filter(Filer.edinet_code == code).first()
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
        db.flush()
        
        # 2. 発行体（Issuer）を登録
        issuer_codes = df['issuerEdinetCode'].dropna().unique()
        for code in issuer_codes:
            if not code or str(code) == 'nan':
                continue
            existing = db.query(Issuer).filter(Issuer.edinet_code == code).first()
            if not existing:
                issuer = Issuer(
                    edinet_code=code,
                    name=None,  # 後で取得
                    sec_code=None
                )
                db.add(issuer)
                print(f"Added Issuer: {code}")
        db.flush()
        
        # 3. 報告書（Filing）を登録
        for _, row in df.iterrows():
            doc_id = row['docID']
            existing = db.query(Filing).filter(Filing.doc_id == doc_id).first()
            if existing:
                continue
            
            # Filerを取得
            filer = db.query(Filer).filter(Filer.edinet_code == row['edinetCode']).first()
            
            # Issuerを取得
            issuer = None
            issuer_code = row.get('issuerEdinetCode')
            if pd.notna(issuer_code) and issuer_code:
                issuer = db.query(Issuer).filter(Issuer.edinet_code == issuer_code).first()
            
            # 提出日時のパース
            submit_date = None
            if pd.notna(row.get('submitDateTime')):
                try:
                    submit_date = datetime.strptime(str(row['submitDateTime']), '%Y-%m-%d %H:%M:%S')
                except:
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
        
        print(f"Import completed!")


if __name__ == "__main__":
    csv_path = "hikari_filings_list.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    import_csv_to_db(csv_path)
