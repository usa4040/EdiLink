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
import pathlib

# --- 設定 ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
EDINET_CODE_HIKARI = "E04948"  # 光通信
DOC_TYPE_LARGE_HOLDING = "010" # 大量保有報告書

# API制限対策の待機時間（秒）
SLEEP_TIME = 0.5 

# キャッシュディレクトリ
CACHE_DIR = pathlib.Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_documents_by_date(target_date):
    """指定した日の書類一覧を取得し、キャッシュに保存する"""
    date_str = target_date.strftime("%Y-%m-%d")
    cache_path = CACHE_DIR / f"list_{date_str}.json"
    
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
    params = {
        "date": date_str,
        "type": 2,
        "Subscription-Key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("metadata", {}).get("status") == "200":
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                return data
            else:
                print(f"\nAPI Error on {date_str}: {data.get('metadata', {}).get('message')}")
        else:
            print(f"\nHTTP Error {response.status_code} on {date_str}")
    except Exception as e:
        print(f"\nRequest Error on {date_str}: {e}")
    
    return None

def download_document_csv(doc_id):
    """書類取得API(type=5: CSV)でデータを取得する"""
    url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
    params = {
        "type": 5, # CSV形式
        "Subscription-Key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"\nDownload Error for {doc_id}: {e}")
    return None

def parse_holding_csv(content):
    """CSVデータから保有株数と比率を抽出する"""
    # 大量保有報告書のCSVは複数のファイルが入ったZIP形式で返ってくる
    # その中の特定のファイルを解析する必要がある
    try:
        z = zipfile.ZipFile(io.BytesIO(content))
        # CSVファイルを探す
        for name in z.namelist():
            if name.endswith(".csv"):
                with z.open(name) as f:
                    df = pd.read_csv(f, encoding="utf-8")
                    # カラム名や項目名は様式によって異なるが、一般的に以下のキーワードを探す
                    # 保有株券等の数 (TotalNumberOfSharesHeld)
                    # 株券等保有割合 (ShareholdingRatio)
                    
                    # 簡易的な抽出ロジック（実際のCSV構造に合わせる必要がある）
                    shares = None
                    ratio = None
                    
                    # CSVの中身を走査
                    for _, row in df.iterrows():
                        row_str = str(row.values)
                        if "保有株券等の数" in row_str or "株券等保有割合" in row_str:
                            # このあたりのロジックは実際のCSVをみて調整
                            pass
        return "N/A", "N/A"
    except:
        return "Error", "Error"

def main():
    if not API_KEY:
        print("Error: API_KEY not found in .env file.")
        return

    # 1. 5年分のスキャン
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    print(f"Starting Scan: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"API interval: {SLEEP_TIME}s")

    all_hikari_docs = []
    
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        # 土日は開示がほぼないのでスキップ（任意だがリクエスト節約になる）
        # if current_date.weekday() < 5: 
        date_list.append(current_date)
        current_date += timedelta(days=1)

    for d in tqdm(reversed(date_list), total=len(date_list), desc="Scanning EDINET"):
        res = get_documents_by_date(d)
        if res and "results" in res:
            for doc in res["results"]:
                # 提出者が光通信 (E04948)
                if doc.get("edinetCode") == EDINET_CODE_HIKARI:
                    # docDescriptionに「大量保有報告書」または「変更報告書」が含まれるもの
                    desc = doc.get("docDescription", "")
                    if "大量保有報告書" in desc or "変更報告書" in desc:
                        all_hikari_docs.append(doc)
        
        # 連続リクエストによる制限を避ける
        time.sleep(SLEEP_TIME)

    if not all_hikari_docs:
        print("\nNo matching documents found in the last 5 years.")
        return

    print(f"\nFound {len(all_hikari_docs)} filings. Saving the list to CSV...")
    
    # リストの作成
    df_list = pd.DataFrame(all_hikari_docs)
    df_list['submitDateTime'] = pd.to_datetime(df_list['submitDateTime'])
    df_list = df_list.sort_values(['secCode', 'submitDateTime'], ascending=[True, False])
    
    # 保存
    output_path = "hikari_filings_list.csv"
    df_list.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"List saved to {output_path}")

    print("\nNext step would be to download each document and extract numerical data.")
    print("This requires one API call per document.")
    print(f"Total documents to download: {len(all_hikari_docs)}")

if __name__ == "__main__":
    main()
