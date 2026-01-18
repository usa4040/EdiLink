
"""
直近の提出書類データ（CSVではなくDB経由）を読み込み、
提出日、書類種別、対象銘柄名などを分かりやすく表示・解説するスクリプト。
新しく取得されたデータの中身を簡易確認するために使用します。
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# パス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import FilerCode, Filing, Issuer, get_engine
from backend.database import get_db_session

def explain_recent_filings(days=35):
    print(f"Analyzing filings from the last {days} days...")
    
    with get_db_session() as db:
        # 直近のデータを取得
        cutoff = datetime.now() - timedelta(days=days)
        
        filings = db.query(Filing).filter(
            Filing.submit_date >= cutoff
        ).order_by(Filing.submit_date.desc()).all()
        
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
            if "光通信" in filer.name:
                 print(f"\n[Date: {f.submit_date}] DocID: {f.doc_id}")
                 print(f"  Type: {f.doc_description}")
                 print(f"  Target Issuer: {issuer_name}")
                 # csv_flagがあれば簡易的に中身についての言及も可能だが今回は概要のみ
                 
if __name__ == "__main__":
    explain_recent_filings()
