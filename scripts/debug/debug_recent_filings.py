
"""
EDINET APIを直接呼び出して、特定提出者の最近の提出書類を確認するデバッグ用スクリプト。
データベースやフィルタリングの影響を受けずに、APIから返される生のデータ状況（Ordinance Codeなど）を調査します。
"""

import requests
import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env読み込み
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(project_root, ".env"))
API_KEY = os.getenv("API_KEY")
EDINET_API_BASE = "https://disclosure.edinet-fsa.go.jp/api/v2"

def check_recent_filings(filer_code="E04948", target_date_str=None, days=40):
    print(f"Checking filings for {filer_code}...")
    
    if target_date_str:
        # 特定の日付のみチェック
        start_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        end_date = start_date
    else:
        # 期間チェック
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
    
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    found_count = 0
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"{EDINET_API_BASE}/documents.json"
        params = {
            "date": date_str,
            "type": 2,
            "Subscription-Key": API_KEY
        }
        
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "results" in data:
                    for doc in data["results"]:
                        # 提出者チェック
                        if doc.get("edinetCode") == filer_code:
                            print(f"[{date_str}] Found: {doc.get('docDescription')} (DocID: {doc.get('docID')})")
                            print(f"    Ordinance: {doc.get('ordinanceCode')}, Form: {doc.get('formCode')}")
                            found_count += 1
            else:
                print(f"[{date_str}] API Status: {res.status_code}")
        except Exception as e:
            print(f"[{date_str}] Error: {e}")
            
        current_date += timedelta(days=1)
        time.sleep(0.5) # Be gentle
        
    print(f"Total filings found: {found_count}")

if __name__ == "__main__":
    # 引数があれば特定日付チェック、なければ期間チェック
    if len(sys.argv) > 1:
        check_recent_filings(target_date_str=sys.argv[1])
    else:
        check_recent_filings()
