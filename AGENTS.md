# AGENTS.md - AIコーディングエージェント向けガイドライン

EdiLinkリポジトリで作業するAIエージェント向けのガイドラインです。

## プロジェクト概要

**EdiLink**は、日本のEDINET（電子開示システム）の開示データを管理するフルスタックアプリケーションです。

- **バックエンド**: Python 3.12, FastAPI, SQLAlchemy 2.0 (Async), Alembic, pytest
- **フロントエンド**: Next.js 16 (App Router), React 19, TypeScript 5, Tailwind CSS 4, Vitest
- **データベース**: PostgreSQL (本番/Docker), SQLite (ローカル開発)
- **インフラ**: Docker Compose

---

## 開発環境セットアップ & 起動

### 1. Docker Compose (推奨)

PostgreSQLとRedisを含む完全な環境を起動します。

```bash
docker-compose up -d
```

### 2. ローカル開発 (SQLite)

Dockerを使用せず、軽量なSQLite構成で起動します。

#### バックエンド (Python)

```bash
# 依存関係インストール
pip install -r requirements.txt

# ローカルサーバー起動 (キャッシュ無効化、非同期SQLite使用)
export DATABASE_URL=sqlite+aiosqlite:///./data/edinet.db
export CI=true
uvicorn backend.main:app --reload --port 8000
```

#### フロントエンド (Next.js)

```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

---

## テスト・Lint・型チェック

### バックエンド

```bash
# テスト実行
pytest
pytest backend/tests/test_api.py -v

# Lint & フォーマットチェック
ruff check backend/
ruff format --check backend/

# 型チェック
mypy backend/
```

### フロントエンド

```bash
cd frontend

# テスト実行
npm test
npm test -- src/test/Sidebar.test.tsx

# Lint & 型チェック
npm run lint
npm run typecheck
```

---

## プロジェクト構造

```
/Users/home/project/EdiLink/
├── backend/           # FastAPIアプリケーション
│   ├── main.py        # エントリーポイント
│   ├── models.py      # SQLAlchemyモデル定義
│   ├── schemas.py     # Pydanticデータスキーマ
│   ├── crud.py        # DB操作ロジック
│   ├── database.py    # DB接続設定
│   ├── sync_edinet.py # データ同期バッチ処理
│   └── tests/         # pytestテスト
├── frontend/          # Next.jsアプリケーション
│   ├── src/app/       # App Routerページ
│   ├── src/components/# UIコンポーネント
│   └── src/test/      # Vitestテスト
├── scripts/           # 運用・分析スクリプト
│   ├── analysis/      # データ分析・検証用
│   ├── export/        # CSV出力用
│   └── maintenance/   # データメンテナンス用
├── data/              # SQLiteデータベース (edinet.db)
└── alembic/           # DBマイグレーション設定
```

---

## コーディングスタイルガイドライン

### Python (バックエンド)

- **フォーマット**: `ruff` 準拠。インデントは4スペース。
- **型ヒント**: 必須。`mypy`でチェック。
  - APIスキーマ: `schemas.py` (Pydantic)
  - DBモデル: `models.py` (SQLAlchemy 2.0 DeclarativeBase)
  - Optional型: `str | None` 形式を使用。
- **データベース**: 非同期セッション (`AsyncSession`) を使用。
  - N+1問題回避のため `selectinload()` や `joinedload()` を明示的に使用。
- **インポート**: 絶対インポートを使用 (`from backend.models import ...`)。
- **バッチ実行**: `python -m backend.sync_edinet` のようにモジュールとして実行。

### TypeScript/JavaScript (フロントエンド)

- **フォーマット**: Prettier/ESLint準拠。インデントは2スペース。
- **コンポーネント**: 関数コンポーネント + Hooks。
  - クライアント機能が必要な場合はファイルの先頭に `"use client"`。
- **命名規則**: コンポーネント `PascalCase`, 関数 `camelCase`。
- **インポート**: `@/` エイリアスを使用 (`import ... from "@/components/..."`)。
- **Tailwind CSS**: v4を使用。`className` にユーティリティクラスを記述。
  - カスタムスタイルは `src/app/globals.css`。

---

## エージェント向け運用ルール

1. **ファイルパス**: 常に絶対パスを使用してください。
2. **既存コードの尊重**: 既存のファイルを読む際は、まず `read` ツールで内容とスタイルを確認してから編集してください。
3. **テスト駆動**: 修正や機能追加の際は、関連するテストを実行（または追加）して動作を検証してください。
4. **エラーハンドリング**:
   - Backend: 想定されるエラーは `HTTPException` で適切なステータスコードを返してください。
   - Frontend: ユーザーに分かりやすい日本語のエラーメッセージを表示してください。

## AIエージェントの振る舞い設定 (Jules等向け)

このリポジトリで作業するAIエージェント（Jules等）は、以下の言語設定を遵守してください。

1. **Pull Request (PR) 作成時**:
   - **タイトル**: 日本語で簡潔に記述してください（例: `fix(api): ユーザー取得ロジックの修正`）。
   - **説明文 (Body)**: 変更内容、目的、検証結果を**日本語**で記述してください。
   - **要約**: 自動生成される要約も可能な限り日本語にしてください。

2. **コミュニケーション**:
   - Issueへのコメントや提案は**日本語**で行ってください。

## PRレビュープロトコル (Self-Review含む)

コードを変更またはレビューする際は以下を確認してください：

- [ ] **安全性**: SQLインジェクション、XSS、機密情報の漏洩がないか。
- [ ] **パフォーマンス**: N+1問題、不要な再レンダリングがないか。
- [ ] **整合性**: 型定義と実装が一致しているか。
- [ ] **テスト**: 変更箇所をカバーするテストが存在し、パスしているか。
