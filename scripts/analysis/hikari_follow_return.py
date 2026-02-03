"""
光通信フォロー投資リターン分析スクリプト

光通信が大量保有報告書を提出した銘柄について、
提出日翌営業日の始値で成行買いし、現在まで保有した場合のリターンを計算する。

使用方法:
    python scripts/analysis/hikari_follow_return.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from tqdm import tqdm


def get_db_path():
    """データベースパスを取得"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'edinet.db')


def get_hikari_bulk_reports():
    """
    光通信の大量保有報告書（新規）を取得
    doc_type = '010000' のみ対象
    """
    conn = sqlite3.connect(get_db_path())

    query = """
        SELECT 
            f.id as filing_id,
            f.submit_date,
            f.doc_id,
            i.name as issuer_name,
            i.sec_code,
            i.edinet_code as issuer_edinet,
            hd.shares_held,
            hd.holding_ratio
        FROM filings f
        JOIN filers fl ON f.filer_id = fl.id
        LEFT JOIN issuers i ON f.issuer_id = i.id
        LEFT JOIN holding_details hd ON f.id = hd.filing_id
        WHERE fl.name LIKE '%光通信%'
        AND f.doc_type = '010000'  -- 大量保有報告書（新規）のみ
        AND i.sec_code IS NOT NULL
        AND i.sec_code != ''
        ORDER BY f.submit_date ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def format_ticker(sec_code: str) -> str:
    """
    証券コードをyfinanceのティッカー形式に変換
    例: '94350' -> '9435.T'
    """
    # 証券コードを4桁にする（末尾の0を除去）
    code = str(sec_code).strip()
    if len(code) == 5 and code.endswith('0'):
        code = code[:4]
    return f"{code}.T"


def get_next_business_day(date: datetime) -> datetime:
    """翌営業日を取得（土日をスキップ）"""
    next_day = date + timedelta(days=1)
    while next_day.weekday() >= 5:  # 土曜=5, 日曜=6
        next_day += timedelta(days=1)
    return next_day


def get_stock_prices(ticker: str, start_date: datetime, end_date: datetime = None):
    """
    指定期間の株価データを取得
    """
    if end_date is None:
        end_date = datetime.now()

    try:
        stock = yf.Ticker(ticker)
        # 開始日から少し前のデータも取得（翌営業日調整のため）
        hist = stock.history(start=start_date - timedelta(days=7), end=end_date + timedelta(days=1))
        return hist
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_open_price_after_date(hist: pd.DataFrame, target_date: datetime) -> tuple:
    """
    指定日以降の最初の始値を取得
    Returns: (価格, 実際の取得日)
    """
    if hist is None or hist.empty:
        return None, None

    # target_date以降のデータをフィルタ
    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    target = pd.Timestamp(target_date.date())

    future_data = hist[hist.index >= target]

    if future_data.empty:
        return None, None

    first_row = future_data.iloc[0]
    return first_row['Open'], future_data.index[0]


def get_current_price(hist: pd.DataFrame) -> tuple:
    """
    最新の終値を取得
    Returns: (価格, 日付)
    """
    if hist is None or hist.empty:
        return None, None

    last_row = hist.iloc[-1]
    return last_row['Close'], hist.index[-1]


def calculate_returns(reports_df: pd.DataFrame) -> pd.DataFrame:
    """
    各銘柄のリターンを計算
    """
    results = []

    # 重複を除去（同じ銘柄の最初の報告のみ）
    unique_reports = reports_df.drop_duplicates(subset=['sec_code'], keep='first')

    print(f"\n{len(unique_reports)}銘柄の株価を取得中...")

    for _, row in tqdm(unique_reports.iterrows(), total=len(unique_reports), desc="Processing"):
        ticker = format_ticker(row['sec_code'])
        submit_date = pd.to_datetime(row['submit_date'])
        next_biz_day = get_next_business_day(submit_date)

        # 株価データ取得
        hist = get_stock_prices(ticker, next_biz_day)

        if hist is None or hist.empty:
            results.append({
                'submit_date': submit_date,
                'issuer_name': row['issuer_name'],
                'sec_code': row['sec_code'],
                'ticker': ticker,
                'holding_ratio': row['holding_ratio'],
                'buy_date': None,
                'buy_price': None,
                'current_date': None,
                'current_price': None,
                'return_pct': None,
                'status': '株価取得失敗'
            })
            continue

        buy_price, buy_date = get_open_price_after_date(hist, next_biz_day)
        current_price, current_date = get_current_price(hist)

        if buy_price is None or current_price is None:
            results.append({
                'submit_date': submit_date,
                'issuer_name': row['issuer_name'],
                'sec_code': row['sec_code'],
                'ticker': ticker,
                'holding_ratio': row['holding_ratio'],
                'buy_date': buy_date,
                'buy_price': buy_price,
                'current_date': current_date,
                'current_price': current_price,
                'return_pct': None,
                'status': '価格データ不完全'
            })
            continue

        return_pct = (current_price - buy_price) / buy_price * 100

        results.append({
            'submit_date': submit_date,
            'issuer_name': row['issuer_name'],
            'sec_code': row['sec_code'],
            'ticker': ticker,
            'holding_ratio': row['holding_ratio'],
            'buy_date': buy_date,
            'buy_price': round(buy_price, 1),
            'current_date': current_date,
            'current_price': round(current_price, 1),
            'return_pct': round(return_pct, 2),
            'status': 'OK'
        })

    return pd.DataFrame(results)


def generate_summary(df: pd.DataFrame) -> str:
    """サマリーレポートを生成"""
    ok_df = df[df['status'] == 'OK']

    if ok_df.empty:
        return "有効なデータがありません。"

    total_count = len(ok_df)
    win_count = len(ok_df[ok_df['return_pct'] > 0])
    lose_count = len(ok_df[ok_df['return_pct'] < 0])
    even_count = len(ok_df[ok_df['return_pct'] == 0])

    win_rate = win_count / total_count * 100
    avg_return = ok_df['return_pct'].mean()
    median_return = ok_df['return_pct'].median()
    max_return = ok_df['return_pct'].max()
    min_return = ok_df['return_pct'].min()
    std_return = ok_df['return_pct'].std()

    # ベスト・ワースト銘柄
    best = ok_df.loc[ok_df['return_pct'].idxmax()]
    worst = ok_df.loc[ok_df['return_pct'].idxmin()]

    summary = f"""
================================================================================
  光通信フォロー投資リターン分析レポート
  生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

【概要】
  対象: 光通信の大量保有報告書（新規）提出銘柄
  戦略: 提出日翌営業日の始値で成行買い → 現在まで保有

【パフォーマンスサマリー】
  分析銘柄数:    {total_count} 銘柄
  勝ち:          {win_count} 銘柄 ({win_rate:.1f}%)
  負け:          {lose_count} 銘柄
  変わらず:      {even_count} 銘柄

  平均リターン:  {avg_return:+.2f}%
  中央値:        {median_return:+.2f}%
  標準偏差:      {std_return:.2f}%
  最大リターン:  {max_return:+.2f}%
  最小リターン:  {min_return:+.2f}%

【ベスト銘柄】
  {best['issuer_name']} ({best['sec_code']})
  報告書提出日: {best['submit_date'].strftime('%Y-%m-%d')}
  買値: {best['buy_price']:,.0f}円 → 現在値: {best['current_price']:,.0f}円
  リターン: {best['return_pct']:+.2f}%

【ワースト銘柄】
  {worst['issuer_name']} ({worst['sec_code']})
  報告書提出日: {worst['submit_date'].strftime('%Y-%m-%d')}
  買値: {worst['buy_price']:,.0f}円 → 現在値: {worst['current_price']:,.0f}円
  リターン: {worst['return_pct']:+.2f}%

【注意事項】
  - 手数料・税金は考慮していません
  - 上場廃止銘柄は除外されています
  - 株式分割・併合の調整はyfinanceに依存しています

================================================================================
"""
    return summary


def main():
    print("=" * 60)
    print("光通信フォロー投資リターン分析")
    print("=" * 60)

    # データ取得
    print("\n1. 大量保有報告書を取得中...")
    reports_df = get_hikari_bulk_reports()
    print(f"   取得件数: {len(reports_df)}件")

    if reports_df.empty:
        print("エラー: 大量保有報告書が見つかりません。")
        return

    # リターン計算
    print("\n2. リターン計算中...")
    results_df = calculate_returns(reports_df)

    # 出力ディレクトリ
    exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports')
    os.makedirs(exports_dir, exist_ok=True)

    # CSV出力
    csv_path = os.path.join(exports_dir, 'hikari_follow_returns.csv')
    results_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n3. CSV出力: {csv_path}")

    # サマリー出力
    summary = generate_summary(results_df)
    summary_path = os.path.join(exports_dir, 'hikari_follow_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"   サマリー出力: {summary_path}")

    # コンソール出力
    print(summary)

    print("\n完了!")


if __name__ == "__main__":
    main()
