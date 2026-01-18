
"""
指定した日付（デフォルト: 2026-01-15）の全EDINET提出書類から、
キーワード（光通信、東京エネシスなど）に一致するものを検索するデバッグ用スクリプト。
特定の書類が見つからない場合の原因調査に使用します。
"""

import requests
import os
import sys
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
API_KEY = os.getenv("API_KEY")
EDINET_API_BASE = "https://disclosure.edinet-fsa.go.jp/api/v2"

def check_filings_by_keywords(target_date_str="2026-01-15"):
    print(f"Checking ALL filings for {target_date_str}...")
    
    url = f"{EDINET_API_BASE}/documents.json"
    params = {
        "date": target_date_str,
        "type": 2,
        "Subscription-Key": API_KEY
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "results" in data:
                count = 0
                for doc in data["results"]:
                    filer_name = doc.get("filerName", "")
                    doc_desc = doc.get("docDescription", "")
                    sec_code = doc.get("secCode", "")
                    edinet_code = doc.get("edinetCode", "")
                    
                    # キーワードチェック
                    is_match = False
                    reason = []
                    
                    if "光通信" in filer_name:
                        is_match = True
                        reason.append("FilerName Match")
                    
                    if "東京エネシス" in doc_desc or "1945" in str(sec_code):
                        is_match = True
                        reason.append("Target Issue Match")
                        
                    if "E04948" == edinet_code:
                        is_match = True
                        reason.append("EdinetCode Match")
                    
                    if is_match:
                        print(f"\n[MATCH] {filer_name} ({edinet_code})")
                        print(f"  DocID: {doc.get('docID')}")
                        print(f"  Description: {doc_desc}")
                        print(f"  SecCode: {sec_code}")
                        print(f"  Ordinance: {doc.get('ordinanceCode')}")
                        print(f"  Reason: {', '.join(reason)}")
                        count += 1
                
                print(f"\nTotal matches found: {count}")
            else:
                print("No results field in response")
        else:
            print(f"API Error: {res.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_filings_by_keywords()
