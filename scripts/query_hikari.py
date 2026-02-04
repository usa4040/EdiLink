"""
株式会社光通信と光通信株式会社のデータを検索するスクリプト
結果をファイルに保存
"""
import os
import sqlite3

# データベースパス
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'edinet.db')

output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports', 'hikari_query_result.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"データベースパス: {db_path}\n")
    f.write("=" * 80 + "\n")

    # 「光通信」を含む会社を filersテーブルから検索
    f.write("\n【1. filersテーブル - 光通信を含む会社】\n")
    cursor.execute("""
        SELECT id, edinet_code, name, sec_code, jcn
        FROM filers
        WHERE name LIKE '%光通信%'
        ORDER BY name
    """)
    filer_results = cursor.fetchall()
    f.write(f"検索結果: {len(filer_results)} 件\n")
    for row in filer_results:
        f.write(f"  ID={row[0]}, EDINET={row[1]}, 名前={row[2]}, 証券={row[3]}, JCN={row[4]}\n")

    # 「光通信」を含む会社を issuersテーブルから検索
    f.write("\n【2. issuersテーブル - 光通信を含む会社】\n")
    cursor.execute("""
        SELECT id, edinet_code, name, sec_code
        FROM issuers
        WHERE name LIKE '%光通信%'
        ORDER BY name
    """)
    issuer_results = cursor.fetchall()
    f.write(f"検索結果: {len(issuer_results)} 件\n")
    for row in issuer_results:
        f.write(f"  ID={row[0]}, EDINET={row[1]}, 名前={row[2]}, 証券={row[3]}\n")

    # 「株式会社光通信」と「光通信株式会社」を明確に比較
    f.write("\n【3. 株式会社光通信 vs 光通信株式会社 の比較】\n")

    for name in ["株式会社光通信", "光通信株式会社"]:
        f.write(f"\n--- '{name}' ---\n")

        # filersテーブル
        cursor.execute("SELECT id, edinet_code, sec_code, jcn FROM filers WHERE name = ?", (name,))
        filer = cursor.fetchone()
        if filer:
            f.write(f"  filers: ID={filer[0]}, EDINET={filer[1]}, 証券={filer[2]}, JCN={filer[3]}\n")
            cursor.execute("SELECT COUNT(*) FROM filings WHERE filer_id = ?", (filer[0],))
            count = cursor.fetchone()[0]
            f.write(f"  提出書類数: {count}\n")
        else:
            f.write("  filers: なし\n")

        # issuersテーブル
        cursor.execute("SELECT id, edinet_code, sec_code FROM issuers WHERE name = ?", (name,))
        issuer = cursor.fetchone()
        if issuer:
            f.write(f"  issuers: ID={issuer[0]}, EDINET={issuer[1]}, 証券={issuer[2]}\n")
            cursor.execute("SELECT COUNT(*) FROM filings WHERE issuer_id = ?", (issuer[0],))
            count = cursor.fetchone()[0]
            f.write(f"  関連書類数: {count}\n")
        else:
            f.write("  issuers: なし\n")

    # filer_codesテーブル
    f.write("\n【4. filer_codesテーブル】\n")
    cursor.execute("""
        SELECT id, filer_id, edinet_code, name
        FROM filer_codes WHERE name LIKE '%光通信%'
    """)
    codes = cursor.fetchall()
    f.write(f"検索結果: {len(codes)} 件\n")
    for row in codes:
        f.write(f"  ID={row[0]}, FilerID={row[1]}, EDINET={row[2]}, 名前={row[3]}\n")

    # 最新の提出書類を表示（filers経由）
    f.write("\n【5. 最新の提出書類 - filers経由（上位20件）】\n")
    cursor.execute("""
        SELECT f.submit_date, f.doc_id, f.doc_type, f.doc_description, fl.name, fl.edinet_code
        FROM filings f
        JOIN filers fl ON f.filer_id = fl.id
        WHERE fl.name LIKE '%光通信%'
        ORDER BY f.submit_date DESC
        LIMIT 20
    """)
    filings = cursor.fetchall()
    f.write(f"検索結果: {len(filings)} 件\n")
    for row in filings:
        f.write(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} ({row[5]})\n")

    # 最新の提出書類を表示（issuers経由）
    f.write("\n【6. 最新の提出書類 - issuers経由（上位20件）】\n")
    cursor.execute("""
        SELECT f.submit_date, f.doc_id, f.doc_type, f.doc_description, i.name, i.edinet_code
        FROM filings f
        JOIN issuers i ON f.issuer_id = i.id
        WHERE i.name LIKE '%光通信%'
        ORDER BY f.submit_date DESC
        LIMIT 20
    """)
    issuer_filings = cursor.fetchall()
    f.write(f"検索結果: {len(issuer_filings)} 件\n")
    for row in issuer_filings:
        f.write(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} ({row[5]})\n")

    # holding_detailsテーブル
    f.write("\n【7. holding_details - 光通信関連の保有情報（上位20件）】\n")
    cursor.execute("""
        SELECT hd.id, hd.filing_id, hd.shares_held, hd.holding_ratio, hd.purpose, fl.name, fl.edinet_code
        FROM holding_details hd
        JOIN filings f ON hd.filing_id = f.id
        JOIN filers fl ON f.filer_id = fl.id
        WHERE fl.name LIKE '%光通信%'
        ORDER BY hd.id DESC
        LIMIT 20
    """)
    holdings = cursor.fetchall()
    f.write(f"検索結果: {len(holdings)} 件\n")
    for row in holdings:
        f.write(f"  ID={row[0]}, FilingID={row[1]}, 株式数={row[2]}, 保有比率={row[3]}, 目的={row[4]}, 会社={row[5]} ({row[6]})\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("検索完了\n")

conn.close()
print(f"結果を保存しました: {output_path}")
