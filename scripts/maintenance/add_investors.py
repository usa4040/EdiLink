import os
import sqlite3

# プロジェクトルートを取得
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 追加したい機関投資家（EDINETコード, 名前）
INVESTORS = [
    ('E11852', 'エフィッシモ キャピタル マネージメント'),
    ('E27325', '株式会社ストラテジックキャピタル'),
    ('E24231', '株式会社レノ'),
    ('E35393', '株式会社シティインデックスイレブンス'),
    ('E08827', 'ダルトン・インベストメンツ'),
    ('E09183', 'タイヨウ・ファンド・マネッジメント'),
]

def main():
    db_path = os.path.join(PROJECT_ROOT, 'data', 'edinet.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    added = []

    for edinet_code, name in INVESTORS:
        # 既存チェック（filer_codesテーブル）
        cur.execute('SELECT id FROM filer_codes WHERE edinet_code = ?', (edinet_code,))
        if cur.fetchone():
            print(f'既存: {name} ({edinet_code})')
            continue

        # 既存チェック（filersテーブル - 古いスキーマ対応）
        cur.execute('SELECT id FROM filers WHERE edinet_code = ?', (edinet_code,))
        if cur.fetchone():
            print(f'既存: {name} ({edinet_code})')
            continue

        # Filer登録（edinet_codeカラムも含む）
        cur.execute(
            'INSERT INTO filers (edinet_code, name, created_at, updated_at) VALUES (?, ?, datetime("now"), datetime("now"))',
            (edinet_code, name)
        )
        filer_id = cur.lastrowid

        # FilerCode登録
        cur.execute(
            'INSERT INTO filer_codes (filer_id, edinet_code, name, created_at) VALUES (?, ?, ?, datetime("now"))',
            (filer_id, edinet_code, name)
        )

        added.append(name)
        print(f'追加: {name} ({edinet_code})')

    conn.commit()
    conn.close()
    print(f'\n=== {len(added)}件の機関投資家を追加しました ===')

if __name__ == '__main__':
    main()
