"""
データベースの全テーブルをCSVファイルにエクスポートするスクリプト
"""
import os
import sys

import pandas as pd
from sqlalchemy import inspect

# プロジェクトルートへのパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import sync_engine


def export_db_to_csv():
    """データベースの全テーブルをCSVにエクスポート"""

    # データベースエンジン取得
    engine = sync_engine

    # エクスポート先ディレクトリ
    export_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports"
    )
    os.makedirs(export_dir, exist_ok=True)
    print(f"Export directory: {export_dir}")

    # 全テーブル名を取得
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    print(f"Found tables: {table_names}")

    for table_name in table_names:
        print(f"Exporting table: {table_name}...")
        try:
            # pandasでテーブルを読み込み
            df = pd.read_sql_table(table_name, engine)

            # CSVファイルパス
            csv_path = os.path.join(export_dir, f"{table_name}.csv")

            # CSVに書き出し (UTF-8, ヘッダーあり, インデックスなし)
            df.to_csv(csv_path, index=False, encoding="utf-8")

            print(f"  -> Saved to {csv_path} ({len(df)} rows)")

        except Exception as e:
            print(f"  -> Error exporting table {table_name}: {e}")

    print("\n=== Export Complete ===")


if __name__ == "__main__":
    export_db_to_csv()
