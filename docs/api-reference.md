# APIリファレンス

## 概要

EdiLink APIは、EDINET（電子開示システム）の大量保有報告書データを提供するRESTful APIです。

**ベースURL:** `http://localhost:8000`

**OpenAPI (Swagger UI):** http://localhost:8000/docs

## エンドポイント一覧

### 提出者（Filer）API

#### GET /api/filers
提出者一覧を取得します。

**パラメータ:**

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|-----------|------|
| skip | integer | No | 0 | スキップ数（0-10000） |
| limit | integer | No | 50 | 取得件数（1-100） |
| search | string | No | - | 提出者名で検索（最大100文字） |

**レスポンス:**

```json
{
  "items": [
    {
      "id": 1,
      "edinet_code": "E04948",
      "name": "株式会社光通信",
      "sec_code": "94350",
      "filing_count": 150,
      "issuer_count": 45,
      "latest_filing_date": "2026-01-15"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

**ステータスコード:**
- 200: 成功
- 429: レート制限超過（100リクエスト/分）

---

#### GET /api/filers/{filer_id}
提出者の詳細情報を取得します。

**パスパラメータ:**

| パラメータ | 型 | 説明 |
|-----------|------|------|
| filer_id | integer | 提出者ID |

**レスポンス:**

```json
{
  "id": 1,
  "edinet_code": "E04948",
  "name": "株式会社光通信",
  "sec_code": "94350",
  "filing_count": 150,
  "issuer_count": 45,
  "latest_filing_date": "2026-01-15"
}
```

**ステータスコード:**
- 200: 成功
- 404: 提出者が存在しない
- 429: レート制限超過（100リクエスト/分）

---

#### POST /api/filers
新しい提出者を追加します。

**リクエストボディ:**

```json
{
  "edinet_code": "E12345",
  "name": "株式会社サンプル",
  "sec_code": "12345"
}
```

**レスポンス:**

```json
{
  "id": 101,
  "edinet_code": "E12345",
  "name": "株式会社サンプル",
  "sec_code": "12345",
  "filing_count": 0,
  "issuer_count": 0,
  "latest_filing_date": null
}
```

**ステータスコード:**
- 200: 成功
- 400: 既に存在する提出者
- 429: レート制限超過（10リクエスト/分）

---

#### GET /api/filers/{filer_id}/issuers
提出者が保有している銘柄一覧を取得します。

**パラメータ:**

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|-----------|------|
| filer_id | integer | Yes | - | 提出者ID |
| skip | integer | No | 0 | スキップ数 |
| limit | integer | No | 50 | 取得件数 |
| search | string | No | - | 銘柄名で検索 |

**ステータスコード:**
- 200: 成功
- 404: 提出者が存在しない
- 429: レート制限超過（30リクエスト/分）

---

#### GET /api/filers/{filer_id}/filings
提出者の報告書一覧を取得します。

**ステータスコード:**
- 429: レート制限超過（50リクエスト/分）

---

#### GET /api/filers/{filer_id}/issuers/{issuer_id}/history
特定の銘柄の報告書履歴を取得します。

**ステータスコード:**
- 429: レート制限超過（50リクエスト/分）

---

### 発行体（Issuer）API

#### GET /api/issuers
銘柄一覧を取得します。

**パラメータ:**

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|-----------|------|
| skip | integer | No | 0 | スキップ数 |
| limit | integer | No | 50 | 取得件数 |
| search | string | No | - | 銘柄名で検索 |

**レスポンス:**

```json
{
  "items": [
    {
      "id": 1,
      "edinet_code": "E11111",
      "name": "株式会社サンプル発行体",
      "sec_code": "10010"
    }
  ],
  "total": 500,
  "skip": 0,
  "limit": 50
}
```

**ステータスコード:**
- 200: 成功
- 429: レート制限超過（100リクエスト/分）

---

#### GET /api/issuers/{issuer_id}
銘柄の詳細情報を取得します。

**ステータスコード:**
- 429: レート制限超過（100リクエスト/分）

---

#### GET /api/issuers/{issuer_id}/ownerships
銘柄を保有している投資家一覧を取得します。

**ステータスコード:**
- 429: レート制限超過（50リクエスト/分）

---

## レート制限

| エンドポイント | 制限 |
|--------------|------|
| /api/filers/* | 100/分 |
| /api/issuers/* | 100/分 |
| /api/filers/*/issuers | 30/分 |
| /api/issuers/*/ownerships | 50/分 |
| POST /api/filers | 10/分 |

制限を超えた場合、HTTP 429 (Too Many Requests) が返されます。

## エラーレスポンス

```json
{
  "detail": "エラーメッセージ"
}
```

## セキュリティヘッダー

すべてのレスポンスに以下のセキュリティヘッダーが含まれます:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
