"""
EDINETコードリストを使用してIssuerの名前と証券コードを更新するスクリプト
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from backend.database import get_db_session
from backend.models import Issuer


def update_issuer_names(csv_path: str):
    """EDINETコードリストからIssuerの名前を更新"""

    # CSV読み込み（Shift-JIS / cp932）
    # 1行目はダウンロード日時なのでスキップ
    df = pd.read_csv(csv_path, encoding="cp932", skiprows=1)

    # カラム名を正規化（全角→半角）
    df.columns = df.columns.str.replace("　", "").str.replace("Ａ-Ｚ", "")

    # EDINETコードカラムを特定
    edinet_col = [c for c in df.columns if "EDINET" in c or "コード" in c][0]
    name_col = [c for c in df.columns if "提出者名" in c or "名称" in c][0]
    sec_code_col = (
        [c for c in df.columns if "証券コード" in c][0]
        if any("証券コード" in c for c in df.columns)
        else None
    )

    print(f"Using columns: EDINET={edinet_col}, Name={name_col}, SecCode={sec_code_col}")
    print(f"Total records in CSV: {len(df)}")

    # EDINETコードをキーにした辞書を作成
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
    with get_db_session() as db:
        issuers = db.query(Issuer).all()
        updated_count = 0

        for issuer in issuers:
            if issuer.edinet_code in edinet_to_info:
                info = edinet_to_info[issuer.edinet_code]
                old_name = issuer.name
                issuer.name = info["name"]
                if info["sec_code"]:
                    issuer.sec_code = info["sec_code"]
                updated_count += 1
                print(f"Updated: {issuer.edinet_code} -> {info['name']} (was: {old_name})")
            else:
                print(f"Not found in CSV: {issuer.edinet_code}")

        print(f"\nTotal issuers updated: {updated_count}/{len(issuers)}")


if __name__ == "__main__":
    csv_path = "EdinetcodeDlInfo.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    update_issuer_names(csv_path)
