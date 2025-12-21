import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm
import time
import zipfile
import io

# .envの読み込み
load_dotenv()
API_KEY = os.getenv("API_KEY")
EDINET_CODE_HIKARI = "E04948"  # 光通信
DOC_TYPE_LARGE_HOLDING = "010" # 大量保有報告書

def get_documents_by_date(target_date):
    """指定した日の書類一覧を取得する"""
    url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
    params = {
        "date": target_date.strftime("%Y-%m-%d"),
        "type": 2,
        "Subscription-Key": API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {target_date}: {e}")
    return None

def main():
    if not API_KEY:
        print("Error: API_KEY not found in .env file.")
        return

    # 1. 過去5年分の書類一覧をスキャン
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    print(f"Scanning from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    all_hikari_docs = []
    
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    # 日付リストを逆順（最新から）にしてスキャン
    # 完全に最新の状態を知るには全スキャンが必要だが、効率化のため一旦リスト化
    for d in tqdm(reversed(date_list), total=len(date_list), desc="Searching documents"):
        res = get_documents_by_date(d)
        if res and "results" in res:
            for doc in res["results"]:
                # 提出者が光通信 (E04948) かチェック
                # 大量保有報告書 (010) のみ抽出
                if doc.get("edinetCode") == EDINET_CODE_HIKARI:
                    # docID, filerName, docDescription, submitDateTime, secCode
                    all_hikari_docs.append(doc)
        
        # API制限の考慮（適宜調整）
        time.sleep(0.1)

    if not all_hikari_docs:
        print("No documents found for Hikari Tsushin (E04948) in the last 5 years.")
        return

    df_docs = pd.DataFrame(all_hikari_docs)
    df_docs['submitDateTime'] = pd.to_datetime(df_docs['submitDateTime'])
    
    # 提出日時順に並び替え
    df_docs = df_docs.sort_values(['secCode', 'submitDateTime'], ascending=[True, False])

    print(f"\nFound {len(df_docs)} filings. Preparing history...")

    # ヒストリカルデータの出力イメージ:
    # 証券コード | 銘柄名 | 提出日 | 保有株数 | 保有比率 | 増減 | docID
    # -------------------------------------------------------------
    # 1234     | ○○株  | 2025-01 | 100万株 | 10.0%  | +2.0% | S...
    # 1234     | ○○株  | 2024-06 |  80万株 |  8.0%  |  新規 | S...
    
    results = []
    # ここで各docIDに対して「書類取得API」を呼び出し、CSV/XBRLから数値を抽出する
    # ※ 本番実行時は、tqdm等で進捗を表示しながら処理します
    for index, row in df_docs.iterrows():
        results.append({
            "SecCode": row.get('secCode', 'N/A'),
            "Issuer": row.get('issuerName', 'Unknown'),
            "Date": row['submitDateTime'].strftime('%Y-%m-%d'),
            "Holdings": "Pending Extraction...", # ここに抽出した数値を入れます
            "Ratio": "Pending Extraction...",    # ここに抽出した数値を入れます
            "DocID": row['docID']
        })

    print("\n--- Holdings History (Example Structure) ---")
    print(pd.DataFrame(results).head(10).to_string(index=False))
    
    pd.DataFrame(results).to_csv("hikari_holdings_history.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
