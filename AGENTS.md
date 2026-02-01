# AGENTS.md - AIコーディングエージェント向けガイドライン

このファイルは、EdiLinkリポジトリで作業するAIエージェント向けのガイドラインです。

## プロジェクト概要

EdiLinkは、日本のEDINET（電子開示システム）の開示データを管理するフルスタックアプリケーションです。

**技術スタック:**
- バックエンド: Python 3.12, FastAPI, SQLAlchemy (SQLite), pytest
- フロントエンド: Next.js 16, React 19, TypeScript 5, Tailwind CSS 4

---

## ビルド・テスト・Lintコマンド

### バックエンド (Python)

```bash
# すべてのテストを実行
pytest

# 単一のテストファイルを実行
pytest backend/tests/test_api.py -v

# 特定のテストを実行
pytest backend/tests/test_api.py::test_get_filers -v

# カバレッジ付きで実行
pytest --cov=backend

# 型チェック実行
mypy backend/

# ローカルサーバーを起動
uvicorn backend.main:app --reload --port 8000
```

### フロントエンド (Next.js)

```bash
cd frontend

# 開発サーバー
npm run dev

# 本番ビルド
npm run build

# ESLint実行
npm run lint

# テスト実行
npm test

# ウォッチモードでテスト
npm run test:watch

# 本番サーバー起動
npm run start
```

---

## コーディングスタイルガイドライン

### Python (バックエンド)

**フォーマット:**
- フォーマッターは未設定 (black/ruff未使用)
- 既存のコードパターンに従う
- インデントは4スペース

**命名規則:**
- 関数/変数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_CASE`
- データベースモデル: PascalCase (例: `Filer`, `HoldingDetail`)

**インポート:**
- 標準ライブラリ → サードパーティ → ローカルの順序
- 絶対インポートを使用: `from backend.models import Filer`
- スクリプト用にプロジェクトルートをsys.pathに追加

**型:**
- APIリクエスト/レスポンスには `schemas.py` のPydanticモデルを使用
- データベースには `models.py` のSQLAlchemyモデルを使用
- 型ヒントは必須（mypyによる静的型チェック）
- Optional型は `| None` パターンを使用: `def func(x: str | None = None)`
- Eager Loadingには `selectinload()` / `joinedload()` を使用

**ドキュメント:**
- 日本語のコメントも可（ターゲットユーザーが日本人）
- モデルクラスの目的を説明するdocstringを使用

**エラーハンドリング:**
- APIエラーにはFastAPIの `HTTPException` を使用
- 適切なHTTPステータスコードを返す (404, 400等)

### TypeScript/JavaScript (フロントエンド)

**フォーマット:**
- Prettierは未設定 - 既存のパターンに従う
- インデントは2スペース
- 文字列はダブルクォート

**命名規則:**
- コンポーネント: `PascalCase` (例: `Sidebar`, `MainContent`)
- 関数/変数: `camelCase` (例: `fetchFilers`, `isCollapsed`)
- 型/インターフェース: `PascalCase` (例: `Filer`, `PaginatedResponse`)
- ファイル名: コンポーネントはPascalCase、ユーティリティはcamelCase

**インポート:**
- プロジェクトインポートには `@/` パスエイリアスを使用
- インポートをグループ化: React/Next → コンポーネント → ユーティリティ
- 例: `import { Sidebar } from "@/app/components/Sidebar";`

**TypeScript:**
- 厳格モード有効
- データ構造にはインターフェースを定義
- 関数には適切な戻りり値の型を指定
- `any` は避ける - 型が不明な場合は `unknown` を使用

**React:**
- フックを使用した関数コンポーネント
- クライアントコンポーネントには "use client" ディレクティブ
- Next.js App Routerパターンを使用
- 子コンポーネントに渡すイベントハンドラには `useCallback` を優先

**Tailwind CSS:**
- Tailwind v4はCSSベースの設定 (tailwind.config.jsなし)
- カスタムテーマは `src/app/globals.css` に定義
- モバイルファーストのレスポンシブデザイン (`sm:`, `lg:` プレフィックスを使用)
- 任意の値は控えめに使用

**エラーハンドリング:**
- 非同期処理にはtry/catchを使用
- 日本語でユーザーフレンドリーなエラーメッセージを表示
- コンポーネントでエラー状態を使用

---

## セキュリティとパフォーマンス

### セキュリティ

**レート制限:**
- すべてのAPIエンドポイントにレート制限を適用
- slowapiによる自動的な制限（100/30/50/10 req/min）

**入力バリデーション:**
- Pydanticモデルによる厳格なバリデーション
- Queryパラメータの範囲制限（ge, le, max_length）

**セキュリティヘッダー:**
- secureパッケージによる自動追加
- X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

### パフォーマンス

**データベース最適化:**
- Eager Loading（selectinload/joinedload）でN+1問題を解消
- ページネーションによる大規模データの効率的取得

---

## テストガイドライン

### Pythonテスト (pytest)

- テストは `backend/tests/` に配置
- `conftest.py` のフィクスチャを使用:
  - `db`: テストごとにクリーンなインメモリSQLite
  - `client`: DBオーバーライド付きFastAPI TestClient
  - `sample_data`: 事前に設定されたテストデータ

**テストの実行:**
```bash
# すべてのテスト
pytest

# 特定のファイル
pytest backend/tests/test_api.py

# 特定のテスト（詳細出力付き）
pytest backend/tests/test_crud.py::test_create_filer -v
```

### フロントエンドテスト

- **Vitest**を使用（Viteベースの高速テストランナー）
- **@testing-library/react**でコンポーネントテスト
- テストは `frontend/src/test/` に配置
- テスト実行: `npm test`
- ウォッチモード: `npm run test:watch`
- E2Eテストには将来的にPlaywrightを検討

---

## プロジェクト構造

```
/Users/home/project/EdiLink/
├── backend/           # FastAPI Pythonバックエンド
│   ├── main.py        # APIルート
│   ├── models.py      # SQLAlchemyモデル
│   ├── schemas.py     # Pydanticスキーマ
│   ├── crud.py        # データベース操作
│   ├── database.py    # DB接続
│   └── tests/         # pytestテストスイート
├── frontend/          # Next.jsフロントエンド
│   ├── src/app/       # App Routerページ
│   ├── components/    # Reactコンポーネント
│   └── context/       # Reactコンテキスト
├── scripts/           # ユーティリティスクリプト
├── docs/              # ドキュメント
│   ├── api-reference.md    # API仕様書
│   └── architecture.md     # アーキテクチャ図
└── data/              # SQLiteデータベース
```

---

## 一般的なタスク

**新しいAPIエンドポイントを追加:**
1. `backend/main.py` にルートを追加
2. 必要に応じて `backend/schemas.py` にスキーマを追加
3. 必要に応じて `backend/crud.py` にCRUD関数を追加
4. `backend/tests/test_api.py` にテストを追加

**新しいページを追加:**
1. `frontend/src/app/[route]/page.tsx` にページを作成
2. インタラクティブが必要な場合は "use client" を使用
3. 既存のコンポーネントパターンに従う
4. Tailwindでスタイリング

**データ同期を実行:**
```bash
python backend/sync_edinet.py
```

**ドキュメントを確認:**
- API仕様: `docs/api-reference.md`
- アーキテクチャ: `docs/architecture.md`
- 貢献ガイド: `CONTRIBUTING.md`

---

## 環境

- フロントエンドにはNode.js 20+が必要
- バックエンドにはPython 3.12+が必要
- SQLiteデータベースは `data/edinet.db` に保存
- バックエンドはポート8000で実行
- フロントエンドはポート3000で実行
