"""
株式会社光通信の保有銘柄と保有比率を確認するスクリプト
"""
import os
import sqlite3

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'edinet.db')
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports', 'hikari_holdings.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("【光通信の保有銘柄と保有比率】\n")
    f.write("=" * 100 + "\n\n")

    # 光通信が提出した報告書における保有銘柄と保有比率
    cursor.execute("""
        SELECT
            f.submit_date,
            f.doc_id,
            f.doc_type,
            f.doc_description,
            i.name as issuer_name,
            i.edinet_code as issuer_edinet,
            i.sec_code as issuer_sec_code,
            hd.shares_held,
            hd.holding_ratio,
            hd.purpose
        FROM filings f
        JOIN filers fl ON f.filer_id = fl.id
        LEFT JOIN issuers i ON f.issuer_id = i.id
        LEFT JOIN holding_details hd ON f.id = hd.filing_id
        WHERE fl.name LIKE '%光通信%'
        ORDER BY f.submit_date DESC
        LIMIT 50
    """)
    results = cursor.fetchall()

    f.write(f"検索結果: {len(results)} 件（最新50件）\n\n")

    for row in results:
        submit_date, doc_id, doc_type, doc_desc, issuer_name, issuer_edinet, issuer_sec, shares, ratio, purpose = row
        f.write(f"提出日: {submit_date}\n")
        f.write(f"  Doc ID: {doc_id}\n")
        f.write(f"  書類: {doc_type} - {doc_desc}\n")
        f.write(f"  発行体（銘柄）: {issuer_name} ({issuer_edinet}, 証券コード: {issuer_sec})\n")
        f.write(f"  保有株数: {shares:,} 株\n" if shares else "  保有株数: N/A\n")
        f.write(f"  保有比率: {ratio}%\n" if ratio else "  保有比率: N/A\n")
        if purpose:
            f.write(f"  保有目的: {purpose[:100]}...\n" if len(str(purpose)) > 100 else f"  保有目的: {purpose}\n")
        f.write("\n")

    # 銘柄別の保有状況サマリー
    f.write("\n" + "=" * 100 + "\n")
    f.write("【銘柄別 最新保有状況サマリー】\n")
    f.write("=" * 100 + "\n\n")

    cursor.execute("""
        SELECT
            i.name as issuer_name,
            i.sec_code,
            hd.shares_held,
            hd.holding_ratio,
            f.submit_date,
            f.doc_description
        FROM (
            SELECT issuer_id, MAX(submit_date) as max_date
            FROM filings
            WHERE filer_id = 1 AND issuer_id IS NOT NULL
            GROUP BY issuer_id
        ) latest
        JOIN filings f ON f.issuer_id = latest.issuer_id AND f.submit_date = latest.max_date AND f.filer_id = 1
        JOIN issuers i ON f.issuer_id = i.id
        LEFT JOIN holding_details hd ON f.id = hd.filing_id
        WHERE hd.holding_ratio IS NOT NULL
        ORDER BY hd.holding_ratio DESC
    """)
    summary = cursor.fetchall()

    f.write(f"銘柄数: {len(summary)} 件\n\n")
    f.write(f"{'銘柄名':<30} {'証券コード':<10} {'保有株数':>15} {'保有比率':>10} {'最終報告日':<12}\n")
    f.write("-" * 100 + "\n")

    for row in summary:
        issuer_name, sec_code, shares, ratio, submit_date, doc_desc = row
        name = (issuer_name[:27] + "...") if issuer_name and len(issuer_name) > 30 else (issuer_name or "N/A")
        shares_str = f"{shares:,}" if shares else "N/A"
        ratio_str = f"{ratio:.2f}%" if ratio else "N/A"
        date_str = str(submit_date)[:10] if submit_date else "N/A"
        f.write(f"{name:<30} {sec_code or 'N/A':<10} {shares_str:>15} {ratio_str:>10} {date_str:<12}\n")

    f.write("\n" + "=" * 100 + "\n")
    f.write("検索完了\n")

conn.close()
print(f"結果を保存しました: {output_path}")
