def test_read_root(client):
    """ルートエンドポイントが正しく応答するか"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"

def test_get_filers(client, sample_data):
    """提出者一覧が正しく取得できるか"""
    response = client.get("/api/filers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "テスト提出者"
    assert data[0]["edinet_code"] == "E00000"

def test_get_issuer_history(client, sample_data):
    """銘柄の履歴がHoldingDetailを含めて正しく取得できるか"""
    filer_id = sample_data["filer"].id
    issuer_id = sample_data["issuer"].id
    
    response = client.get(f"/api/filers/{filer_id}/issuers/{issuer_id}/history")
    assert response.status_code == 200
    data = response.json()
    
    # 基本情報
    assert data["issuer"]["name"] == "テスト発行体"
    assert data["filer"]["name"] == "テスト提出者"
    assert data["filer"]["edinet_code"] == "E00000"
    
    # 履歴データ
    assert len(data["history"]) == 1
    history_entry = data["history"][0]
    assert history_entry["doc_id"] == "S_TEST_01"
    assert history_entry["shares_held"] == 1000000
    assert history_entry["holding_ratio"] == 5.50

def test_get_non_existent_filer(client):
    """存在しない提出者の場合に404を返すか"""
    response = client.get("/api/filers/9999")
    assert response.status_code == 404
