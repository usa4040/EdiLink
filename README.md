# EdiLink

[![CI](https://github.com/usa4040/EdiLink/actions/workflows/ci.yml/badge.svg)](https://github.com/usa4040/EdiLink/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)

日本のEDINET（電子開示システム）から大量保有報告書データを収集・管理・可視化するフルスタックアプリケーションです。

## 機能

- 📊 **提出者（投資家）一覧** - ページネーション・検索対応
- 📈 **保有銘柄追跡** - 保有比率の推移を可視化
- 📑 **報告書履歴** - 過去の報告書を時系列で閲覧
- 🔍 **銘柄別検索** - 発行体（企業）ごとの保有状況確認
- 📥 **EDINET連携** - API経由でデータ自動同期

## スクリーンショット

<!-- ここにスクリーンショットを追加してください -->
<!-- ![ダッシュボード](./docs/screenshots/dashboard.png) -->

## クイックスタート

### 必要条件

- Python 3.12+
- Node.js 20+
- EDINET APIキー（オプション）

### インストール

```bash
# 1. リポジトリをクローン
git clone https://github.com/usa4040/EdiLink.git
cd EdiLink

# 2. バックエンドセットアップ
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# 3. フロントエンドセットアップ
cd frontend
npm install
```

### 実行

```bash
# ターミナル1: バックエンド
uvicorn backend.main:app --reload

# ターミナル2: フロントエンド
cd frontend
npm run dev
```

アクセス: http://localhost:3000

## 技術スタック

### バックエンド
- **Python 3.12** - メイン言語
- **FastAPI** - Webフレームワーク
- **SQLAlchemy 2.0** - ORM
- **SQLite** - データベース
- **pytest** - テスト
- **ruff** / **mypy** - 静的解析

### フロントエンド
- **Next.js 16** - Reactフレームワーク
- **React 19** - UIライブラリ
- **TypeScript 5** - 型安全
- **Tailwind CSS 4** - スタイリング
- **Vitest** - テスト

## ドキュメント

- [APIリファレンス](./docs/api-reference.md)
- [開発者ガイド](./CONTRIBUTING.md)
- [アーキテクチャ](./docs/architecture.md)

## プロジェクト構成

```
EdiLink/
├── backend/           # FastAPIバックエンド
│   ├── main.py        # APIエンドポイント
│   ├── models.py      # SQLAlchemyモデル
│   ├── crud.py        # データベース操作
│   └── tests/         # テスト
├── frontend/          # Next.jsフロントエンド
│   ├── src/app/       # アプリケーションページ
│   └── src/test/      # テスト
├── scripts/           # ユーティリティスクリプト
│   ├── export/        # CSV出力
│   └── analysis/      # 分析ツール
└── data/              # SQLiteデータベース
```

## 開発ワークフロー

```bash
# コードチェック
ruff check backend/
mypy backend/

# テスト実行
pytest backend/tests/
cd frontend && npm test

# 開発サーバー起動
uvicorn backend.main:app --reload
cd frontend && npm run dev
```

## データ同期

EDINETから最新データを取得:

```bash
python backend/sync_edinet.py --days 30
```

## CI/CD

GitHub Actions で自動チェック:
- ✅ ruff (lint)
- ✅ ruff format (format)
- ✅ mypy (type check)
- ✅ pytest (backend tests)
- ✅ npm test (frontend tests)

## ライセンス

MIT License
