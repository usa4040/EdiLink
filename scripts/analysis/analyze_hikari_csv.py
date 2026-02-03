
"""
光通信の既存データCSV（hikari_filings_list.csv）を分析するスクリプト。
レコード総数や日付範囲、書類種別の内訳を集計して表示します。
"""

import os

import pandas as pd

# プロジェクトルートを取得して、exportsディレクトリ内のCSVを参照
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
csv_path = os.path.join(project_root, 'exports', 'hikari_filings_list.csv')

if not os.path.exists(csv_path):
    print(f"File not found: {csv_path}")
else:
    try:
        df = pd.read_csv(csv_path)
        print(f"Total records: {len(df)}")

        if 'submitDateTime' in df.columns:
            df['submitDateTime'] = pd.to_datetime(df['submitDateTime'])
            min_date = df['submitDateTime'].min()
            max_date = df['submitDateTime'].max()
            print(f"Date Range: {min_date} to {max_date}")

            # 書類種類ごとの件数
            if 'docDescription' in df.columns:
                print("\nDocument Types:")
                print(df['docDescription'].value_counts())
    except Exception as e:
        print(f"Error analyzing CSV: {e}")
