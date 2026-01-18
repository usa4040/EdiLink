# ユーティリティスクリプト一覧

本ディレクトリには、プロジェクトの運用、データ分析、デバッグに使用する各種スクリプトが統合されています。

## ディレクトリ構造とスクリプト概要

### [analysis/](./analysis/) - データ分析・調査用
- `analyze_hikari_csv.py`: `exports/` 内のCSVデータを読み込み、基本統計や書類種別の内訳を表示します。
- `explain_recent.py`: データベースから直近の提出書類を取得し、内容を分かりやすく要約・解説します。

### [export/](./export/) - データ出力用
- `export_filer_csv.py`: 指定した EDINET コード（提出者）の書類データを `exports/` に CSV 出力します。
- `export_group_csv.py`: 特定の法人グループ（同一 FilerID）に関連する全書類を統合して `exports/` に CSV 出力します。

### [maintenance/](./maintenance/) - データベース管理・保守用
- `add_investors.py`: リストアップされた機関投資家（EDINETコードと名前）をデータベースに一括登録します。
- `check_db_code.py`: 特定の EDINET コードがデータベースに正しく登録されているか、紐付け状況を確認します。

### [debug/](./debug/) - デバッグ・API直接調査用
- `debug_jan15_filing.py`: 特定の日付の全提出書類からキーワードに一致するものを検索し、APIの生の応答内容を確認します。
- `debug_recent_filings.py`: 特定の提出者の最近の書類をAPIから直接取得し、DB登録時のフィルタリング前の状態を確認します。

## 実行方法

全てのスクリプトは、プロジェクトルートを `PYTHONPATH` に含めるよう設計されています。各ディレクトリに移動して実行、またはルートからパスを指定して実行してください。

例:
```bash
python scripts/export/export_filer_csv.py E04948
```

## 注意事項
- 全てのスクリプトは、プロジェクトルートにある `.env` ファイルおよび `data/edinet.db` を参照します。
- `debug/` 配下のスクリプトを実行するには API キーの設定が必要です。
