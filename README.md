# EdiLink (EDINET Filing Data Management System)

EDINET（金融商品取引法に基づく有価証券報告書等の開示書類に関する電子開示システム）から提出書類データを取得・分析・管理するためのシステムです。

## プロジェクト構成

- `backend/`: FastAPIを使用したバックエンドサーバー
- `frontend/`: Next.jsを使用したフロントエンドアプリケーション
- `scripts/`: データ取得・分析・メンテナンス用の各種ユーティリティスクリプト
- `data/`: SQLite データベースファイル
- `exports/`: CSV 出力ファイル

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/usa4040/EdiLink.git
cd EdiLink
```

### 2. バックエンド（Python）の設定
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化 (Windows)
.\venv\Scripts\activate
# (Mac/Linux: source venv/bin/activate)

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集して API_KEY を設定してください
```

### 3. フロントエンド（Node.js）の設定
```bash
cd frontend
npm install
npm run dev
```

### 4. データベースの初期化
初回実行時は `backend/database.py` または `backened/main.py` を通じてテーブルが作成されます。

## スクリプトの実行方法
詳細については [scripts/README.md](./scripts/README.md) を参照してください。

例：
```bash
python scripts/export/export_filer_csv.py E04948
```

## CI/CD
GitHub Actions を使用して、プルリクエスト作成時に自動的にテストとリンターが実行されます。
