"""
EDINET APIから取得したデータを直接DBに保存する統合スクリプト
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import contextlib
import time
from datetime import datetime, timedelta
from typing import TypedDict

import requests
from dotenv import load_dotenv
from tqdm import tqdm

from backend.database import sync_engine
from backend.database import SyncSessionLocal
from backend.models import Base, Filer, FilerCode, Filing, Issuer

# .envの読み込み
load_dotenv()
API_KEY = os.getenv("API_KEY")

# EDINET API設定
EDINET_API_BASE = "https://disclosure.edinet-fsa.go.jp/api/v2"


def get_documents_by_date(target_date: datetime) -> dict | None:
    """指定した日の書類一覧を取得"""
    url = f"{EDINET_API_BASE}/documents.json"
    params: dict[str, str | int | None] = {
        "date": target_date.strftime("%Y-%m-%d"),
        "type": 2,  # 2: メタデータのみ
        "Subscription-Key": API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            result: dict = response.json()
            return result
    except Exception as e:
        print(f"Error fetching {target_date}: {e}")
    return None


def sync_documents(filer_edinet_code: str | None = None, days: int = 365, use_cache: bool = True):
    """
    EDINET APIから書類一覧を取得してDBに保存

    Args:
        filer_edinet_code: 特定の提出者に絞る場合のEDINETコード（例: "E04948"）
        days: 過去何日分を同期するか
        use_cache: キャッシュを使用するか（キャッシュがあればAPIを叩かない）
    """
    if not API_KEY:
        print("Error: API_KEY not found in .env file.")
        print("Please set API_KEY in .env file.")
        return

    # データベース初期化
    Base.metadata.create_all(bind=sync_engine)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(
        f"Syncing documents from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}..."
    )
    if filer_edinet_code:
        print(f"Filtering by filer: {filer_edinet_code}")

    # 日付リスト作成
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    # キャッシュディレクトリ
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    new_filings = 0
    new_filers = 0
    new_issuers = 0
    processed_doc_ids = set()  # セッション内での重複を追跡

    with SyncSessionLocal() as db:
        for d in tqdm(date_list, desc="Fetching documents"):
            # キャッシュファイルチェック
            cache_file = os.path.join(cache_dir, f"list_{d.strftime('%Y-%m-%d')}.json")

            if use_cache and os.path.exists(cache_file):
                import json

                with open(cache_file, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = get_documents_by_date(d)
                if data and use_cache:
                    import json

                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                time.sleep(1)  # API制限対策（1秒間隔）

            if not data or "results" not in data:
                continue

            for doc in data["results"]:
                # 大量保有報告書系のみ対象（ordinanceCode: 060）
                if doc.get("ordinanceCode") != "060":
                    continue

                # 提出者フィルタ
                edinet_code = doc.get("edinetCode")
                if filer_edinet_code and edinet_code != filer_edinet_code:
                    continue

                doc_id = doc.get("docID")
                if not doc_id:
                    continue

                # 既存チェック（DB + セッション内重複）
                if doc_id in processed_doc_ids:
                    continue
                existing = db.query(Filing).filter(Filing.doc_id == doc_id).first()
                if existing:
                    processed_doc_ids.add(doc_id)
                    continue

                # 処理開始時にセットに追加
                processed_doc_ids.add(doc_id)

                # 1. 提出者（Filer）の登録/取得
                # EDINETコードからFilerCodeを検索
                filer_code = (
                    db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()
                )

                if filer_code:
                    filer = filer_code.filer
                else:
                    # 新規Filerを作成
                    filer = Filer(
                        edinet_code=edinet_code,  # DBスキーマ必須フィールド
                        name=doc.get("filerName", ""),
                        sec_code=str(doc.get("secCode", "")) if doc.get("secCode") else None,
                        jcn=str(doc.get("JCN", "")) if doc.get("JCN") else None,
                    )
                    db.add(filer)
                    db.flush()

                    # FilerCodeを作成
                    filer_code = FilerCode(
                        filer_id=filer.id, edinet_code=edinet_code, name=doc.get("filerName", "")
                    )
                    db.add(filer_code)
                    db.flush()
                    new_filers += 1

                # 2. 発行体（Issuer）の登録/取得
                issuer = None
                issuer_code = doc.get("issuerEdinetCode")
                if issuer_code:
                    issuer = db.query(Issuer).filter(Issuer.edinet_code == issuer_code).first()
                    if not issuer:
                        issuer = Issuer(
                            edinet_code=issuer_code,
                            name=None,  # 後でsync_issuer_namesで更新
                            sec_code=None,
                        )
                        db.add(issuer)
                        db.flush()
                        new_issuers += 1

                # 3. 報告書（Filing）の登録
                submit_date = None
                if doc.get("submitDateTime"):
                    with contextlib.suppress(Exception):
                        submit_date = datetime.strptime(doc["submitDateTime"], "%Y-%m-%d %H:%M")

                filing = Filing(
                    doc_id=doc_id,
                    filer_id=filer.id,
                    issuer_id=issuer.id if issuer else None,
                    doc_type=doc.get("formCode"),
                    doc_description=doc.get("docDescription"),
                    submit_date=submit_date,
                    parent_doc_id=doc.get("parentDocID") if doc.get("parentDocID") else None,
                    csv_flag=doc.get("csvFlag") == "1",
                    xbrl_flag=doc.get("xbrlFlag") == "1",
                    pdf_flag=doc.get("pdfFlag") == "1",
                )
                db.add(filing)
                new_filings += 1

        db.commit()

    print("\n=== Sync Complete ===")
    print(f"New Filers: {new_filers}")
    print(f"New Issuers: {new_issuers}")
    print(f"New Filings: {new_filings}")


def sync_issuer_names(csv_path: str | None = None):
    """
    EDINETコードリストから銘柄名を更新
    """
    import pandas as pd

    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "EdinetcodeDlInfo.csv")

    if not os.path.exists(csv_path):
        print(f"Error: EDINETコードリストが見つかりません: {csv_path}")
        print("EDINETからダウンロードしてプロジェクトルートに配置してください。")
        return

    # CSV読み込み（Shift-JIS / cp932）
    df = pd.read_csv(csv_path, encoding="cp932", skiprows=1)

    # カラム名を正規化
    df.columns = df.columns.str.replace("　", "").str.replace("Ａ-Ｚ", "")

    # カラム特定
    edinet_col = [c for c in df.columns if "EDINET" in c or "コード" in c][0]
    name_col = [c for c in df.columns if "提出者名" in c or "名称" in c][0]
    sec_code_col = (
        [c for c in df.columns if "証券コード" in c][0]
        if any("証券コード" in c for c in df.columns)
        else None
    )

    # 辞書作成
    edinet_to_info = {}
    for _, row in df.iterrows():
        code = str(row[edinet_col]).strip()
        if code and code != "nan":
            name = str(row[name_col]).strip() if pd.notna(row[name_col]) else None
            sec_code = (
                str(row[sec_code_col]).strip()
                if sec_code_col and pd.notna(row[sec_code_col])
                else None
            )
            edinet_to_info[code] = {"name": name, "sec_code": sec_code}

    print(f"Loaded {len(edinet_to_info)} EDINET codes from CSV")

    # DBのIssuerを更新
    with SyncSessionLocal() as db:
        issuers = db.query(Issuer).all()
        updated = 0

        for issuer in issuers:
            if issuer.edinet_code in edinet_to_info:
                info = edinet_to_info[issuer.edinet_code]
                if issuer.name != info["name"]:
                    issuer.name = info["name"]
                    if info["sec_code"]:
                        issuer.sec_code = info["sec_code"]
                    updated += 1

        db.commit()
        print(f"Updated {updated} issuers with names")


def download_document_csv(doc_id: str) -> bytes | None:
    """
    EDINET APIから報告書のCSVデータをダウンロード
    """
    url = f"{EDINET_API_BASE}/documents/{doc_id}"
    params = {
        "type": 5,  # 5: CSV
        "Subscription-Key": API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error downloading CSV for {doc_id}: {e}")
    return None


class HoldingDataResult(TypedDict):
    """保有データの型定義"""

    shares_held: int | None
    holding_ratio: float | None
    purpose: str | None


def extract_holding_data_from_csv(csv_content: bytes) -> HoldingDataResult:
    """
    CSVデータから保有株数・保有比率を抽出

    EDINETのXBRL→CSV変換データ（UTF-16、タブ区切り）を解析
    """
    import io
    import zipfile

    import pandas as pd

    result: HoldingDataResult = {
        "shares_held": None,
        "holding_ratio": None,
        "purpose": None,
    }

    try:
        # CSVはZIP形式で提供される
        with zipfile.ZipFile(io.BytesIO(csv_content)) as zf:
            # ZIPの中のCSVファイルを探す
            csv_files = [f for f in zf.namelist() if f.endswith(".csv")]

            for csv_file in csv_files:
                try:
                    with zf.open(csv_file) as f:
                        content = f.read()

                        # EDINETのCSVはUTF-16でタブ区切り
                        try:
                            df = pd.read_csv(
                                io.BytesIO(content),
                                encoding="utf-16",
                                sep="\t",
                                on_bad_lines="skip",
                            )
                        except Exception:
                            try:
                                df = pd.read_csv(
                                    io.BytesIO(content), encoding="cp932", on_bad_lines="skip"
                                )
                            except Exception:
                                continue

                        # EDINETのCSVは「項目名」「値」という列構成
                        if "項目名" in df.columns and "値" in df.columns:
                            # 株券等保有割合を探す（最大の値を取得）
                            ratio_mask = df["項目名"].str.contains(
                                "株券等保有割合", na=False
                            ) & ~df["項目名"].str.contains("直前|欄外|増減", na=False)
                            ratio_rows = df[ratio_mask]
                            if len(ratio_rows) > 0:
                                for val in ratio_rows["値"]:
                                    try:
                                        ratio = float(
                                            str(val).replace("%", "").replace(",", "").strip()
                                        )
                                        # 保有割合は0-1の範囲で格納されている場合は100倍する
                                        if 0 < ratio <= 1:
                                            ratio = ratio * 100  # パーセンテージに変換
                                        if 0 < ratio <= 100 and (
                                            result["holding_ratio"] is None
                                            or ratio > result["holding_ratio"]
                                        ):
                                            result["holding_ratio"] = ratio
                                    except Exception:
                                        continue

                            # 保有株券等の数（総数）を探す（最大の値を取得）
                            shares_mask = df["項目名"].str.contains(
                                "保有株券等の数（総数）", na=False
                            ) & ~df["項目名"].str.contains("欄外", na=False)
                            shares_rows = df[shares_mask]
                            if len(shares_rows) > 0:
                                for val in shares_rows["値"]:
                                    try:
                                        shares = int(
                                            str(val).replace(",", "").replace("株", "").strip()
                                        )
                                        if shares > 0 and (
                                            result["shares_held"] is None
                                            or shares > result["shares_held"]
                                        ):
                                            result["shares_held"] = shares
                                    except Exception:
                                        continue

                            # 保有目的を探す
                            purpose_mask = df["項目名"].str.contains("保有の目的", na=False) & ~df[
                                "項目名"
                            ].str.contains("欄外", na=False)
                            purpose_rows = df[purpose_mask]
                            if len(purpose_rows) > 0:
                                for val in purpose_rows["値"]:
                                    if pd.notna(val) and str(val) != "－" and len(str(val)) > 2:
                                        result["purpose"] = str(val)[:500]
                                        break

                        if result["holding_ratio"] or result["shares_held"]:
                            break
                except Exception:
                    continue
    except Exception as e:
        print(f"Error extracting CSV data: {e}")

    return result


def sync_holding_details(
    filer_edinet_code: str | None = None, limit: int | None = None, year: int | None = None
):
    """
    報告書からCSVをダウンロードして保有詳細を取得・保存

    Args:
        filer_edinet_code: 特定の提出者に絞る場合のEDINETコード
        limit: 処理する報告書の最大数（テスト用）
        year: 特定の年に絞る場合の年（例: 2025）
    """
    from sqlalchemy import extract

    from backend.models import HoldingDetail

    if not API_KEY:
        print("Error: API_KEY not found in .env file.")
        return

    with SyncSessionLocal() as db:
        # CSVフラグがあり、まだHoldingDetailがないFilingを取得
        query = (
            db.query(Filing)
            .filter(Filing.csv_flag == True)
            .outerjoin(HoldingDetail)
            .filter(HoldingDetail.id == None)
        )

        if filer_edinet_code:
            filer_code = (
                db.query(FilerCode).filter(FilerCode.edinet_code == filer_edinet_code).first()
            )
            if filer_code:
                query = query.filter(Filing.filer_id == filer_code.filer_id)

        # 年フィルタ
        if year:
            query = query.filter(extract("year", Filing.submit_date) == year)
            print(f"Filtering by year: {year}")

        filings = query.order_by(Filing.submit_date.desc()).all()

        if limit:
            filings = filings[:limit]

        print(f"Processing {len(filings)} filings for holding details...")

        success_count = 0
        error_count = 0

        for filing in tqdm(filings, desc="Downloading CSVs"):
            csv_content = download_document_csv(filing.doc_id)

            if not csv_content:
                error_count += 1
                continue

            data = extract_holding_data_from_csv(csv_content)

            # HoldingDetailを作成（データが取れなくても記録を残す）
            holding = HoldingDetail(
                filing_id=filing.id,
                shares_held=data["shares_held"],
                holding_ratio=data["holding_ratio"],
                purpose=data["purpose"],
            )
            db.add(holding)

            if data["holding_ratio"] or data["shares_held"]:
                success_count += 1
            else:
                error_count += 1

            time.sleep(0.5)  # API制限対策（0.5秒間隔）

        db.commit()

        print("\n=== Holding Details Sync Complete ===")
        print(f"Successfully extracted: {success_count}")
        print(f"Failed/Empty: {error_count}")


def main():
    parser = argparse.ArgumentParser(description="EDINET データ同期ツール")
    parser.add_argument(
        "--days", type=int, default=365, help="過去何日分を同期するか（デフォルト: 365）"
    )
    parser.add_argument(
        "--filer", type=str, default=None, help="特定の提出者EDINETコードでフィルタ（例: E04948）"
    )
    parser.add_argument("--no-cache", action="store_true", help="キャッシュを使用しない")
    parser.add_argument("--update-names", action="store_true", help="銘柄名の更新のみ実行")
    parser.add_argument("--sync-holdings", action="store_true", help="保有詳細データを取得")
    parser.add_argument(
        "--limit", type=int, default=None, help="処理する報告書の最大数（テスト用）"
    )
    parser.add_argument("--year", type=int, default=None, help="特定の年に絞る（例: 2025）")

    args = parser.parse_args()

    if args.update_names:
        sync_issuer_names()
    elif args.sync_holdings:
        sync_holding_details(filer_edinet_code=args.filer, limit=args.limit, year=args.year)
    else:
        sync_documents(filer_edinet_code=args.filer, days=args.days, use_cache=not args.no_cache)
        # 銘柄名も更新
        sync_issuer_names()


if __name__ == "__main__":
    main()
