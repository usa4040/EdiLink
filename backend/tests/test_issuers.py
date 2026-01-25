from backend.models import Issuer

def test_get_issuers_basic(client, db):
    """
    銘柄一覧が正しく取得できるか（ページネーション含む）
    """
    # テストデータ追加
    issuers = [
        Issuer(edinet_code="E10001", name="株式会社A", sec_code="1001"),
        Issuer(edinet_code="E10002", name="株式会社B", sec_code="1002"),
        Issuer(edinet_code="E10003", name="株式会社C", sec_code="1003"),
    ]
    db.add_all(issuers)
    db.commit()

    # 全件取得
    response = client.get("/api/issuers?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    
    # ページネーション確認
    response_paged = client.get("/api/issuers?limit=2&skip=1")
    assert response_paged.status_code == 200
    data_paged = response_paged.json()
    assert len(data_paged["items"]) == 2
    # 順序保証がない場合はセットで比較などが安全だが、実装次第。
    # ここでは件数チェックのみに留めるか、IDでソートされていることを期待するか。
    # 通常はID順や作成順になるはず。

def test_get_issuers_search(client, db):
    """
    銘柄名やコードで検索できるか
    """
    issuers = [
        Issuer(edinet_code="E20001", name="Apple Japan", sec_code="2001"),
        Issuer(edinet_code="E20002", name="Banana Corp", sec_code="2002"),
        Issuer(edinet_code="E20003", name="Cherry Inc", sec_code="2003"),
    ]
    db.add_all(issuers)
    db.commit()

    # 名前検索 "Apple"
    response = client.get("/api/issuers?search=Apple")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Apple Japan"

    # コード検索 "2002"
    response = client.get("/api/issuers?search=2002")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Banana Corp"
    
    # EDINETコード検索 "E20003"
    response = client.get("/api/issuers?search=E20003")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Cherry Inc"

def test_get_issuers_empty(client):
    """
    データがない場合に空リストが返るか
    """
    response = client.get("/api/issuers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
