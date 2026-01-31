# 貢献ガイドライン

EdiLink プロジェクトへの貢献に興味を持っていただきありがとうございます！

## 開発環境のセットアップ

### 前提条件

- Python 3.12+
- Node.js 20+
- Git

### セットアップ手順

```bash
# 1. リポジトリをフォークしてクローン
git clone https://github.com/usa4040/EdiLink.git
cd EdiLink

# 2. バックエンドセットアップ
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# 3. フロントエンドセットアップ
cd frontend
npm install
cd ..
```

## 開発ワークフロー

### 1. ブランチの作成

```bash
git checkout -b feature/your-feature-name
# または
git checkout -b fix/your-bug-fix
```

### 2. 変更の実施

コードを編集し、テストを追加してください。

### 3. コードチェック

```bash
# バックエンドチェック
ruff check backend/
ruff format backend/
mypy backend/
pytest backend/tests/

# フロントエンドチェック
cd frontend
npm run lint
npm test
```

### 4. コミット

```bash
git add .
git commit -m "feat: 変更内容の要約

詳細な説明（必要に応じて）

Closes #123"
```

**コミットメッセージ規約:**

- `feat:` 新機能
- `fix:` バグ修正
- `perf:` パフォーマンス改善
- `refactor:` リファクタリング
- `test:` テスト追加・修正
- `docs:` ドキュメント更新
- `ci:` CI/CD設定変更

### 5. プッシュとPR作成

```bash
git push origin feature/your-feature-name
```

GitHubでプルリクエストを作成してください。

## プルリクエストのガイドライン

### PR作成前のチェックリスト

- [ ] テストが追加されている（または既存テストが通る）
- [ ] ruffチェックが通る
- [ ] mypyチェックが通る
- [ ] コミットメッセージが規約に従っている
- [ ] 関連するIssueがリンクされている（`Closes #123`）

### PRテンプレート

```markdown
## 概要
変更内容の簡潔な説明

## 変更内容
- 変更1
- 変更2

## 関連Issue
Closes #123

## チェックリスト
- [ ] テスト通過
- [ ] ruff/mypyチェック通過
```

## コーディング規約

### Python

**インポート順序:**
```python
# 1. 標準ライブラリ
import os
from datetime import datetime

# 2. サードパーティ
from fastapi import FastAPI
from sqlalchemy import Column

# 3. ローカル
from backend.models import Filer
```

**型ヒント:**
```python
def get_filer_by_id(db: Session, filer_id: int) -> Filer | None:
    ...
```

**命名規則:**
- 関数・変数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_CASE`

### TypeScript

**命名規則:**
- 関数・変数: `camelCase`
- クラス・インターフェース: `PascalCase`
- ファイル名: コンポーネントは`PascalCase`、その他は`camelCase`

## テスト

### バックエンドテスト

```bash
# すべてのテスト
pytest

# 特定のテストファイル
pytest backend/tests/test_api.py

# カバレッジ付き
pytest --cov=backend
```

### フロントエンドテスト

```bash
cd frontend
npm test
npm run test:coverage
```

## 質問・サポート

質問や問題がある場合は、GitHub Issuesを作成してください。

## 行動規範

- 他の貢献者を尊重してください
- 建設的なフィードバックを心がけてください
- ハラスメントや差別的な行為は許容されません
