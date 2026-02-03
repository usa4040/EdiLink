from datetime import datetime

from backend.models import Filer, FilerCode, Filing, HoldingDetail, Issuer


async def test_get_issuers_basic(client, db):
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
    response = await client.get("/api/issuers?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # ページネーション確認
    response_paged = await client.get("/api/issuers?limit=2&skip=1")
    assert response_paged.status_code == 200
    data_paged = response_paged.json()
    assert len(data_paged["items"]) == 2
    # 順序保証がない場合はセットで比較などが安全だが、実装次第。
    # ここでは件数チェックのみに留めるか、IDでソートされていることを期待するか。
    # 通常はID順や作成順になるはず。


async def test_get_issuers_search(client, db):
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
    response = await client.get("/api/issuers?search=Apple")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Apple Japan"

    # コード検索 "2002"
    response = await client.get("/api/issuers?search=2002")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Banana Corp"

    # EDINETコード検索 "E20003"
    response = await client.get("/api/issuers?search=E20003")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Cherry Inc"


async def test_get_issuers_empty(client):
    """
    データがない場合に空リストが返るか
    """
    response = await client.get("/api/issuers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_get_issuer_ownerships(client, db):
    """
    指定した銘柄を保有している投資家一覧が取得できるか
    """
    # 銘柄作成
    issuer = Issuer(edinet_code="E99999", name="Target Corp", sec_code="9999")
    db.add(issuer)
    db.flush()

    # 投資家A（保有あり）
    filer_a = Filer(edinet_code="E0000A", name="Investor A")
    db.add(filer_a)
    db.flush()
    # FilerCodeも必要
    db.add(FilerCode(filer_id=filer_a.id, edinet_code="E0000A", name="Investor A"))

    # 投資家B（保有あり）
    filer_b = Filer(edinet_code="E0000B", name="Investor B")
    db.add(filer_b)
    db.flush()
    db.add(FilerCode(filer_id=filer_b.id, edinet_code="E0000B", name="Investor B"))

    # 投資家C（別の銘柄を保有、今回は対象外）
    filer_c = Filer(edinet_code="E0000C", name="Investor C")
    db.add(filer_c)
    db.flush()
    db.add(FilerCode(filer_id=filer_c.id, edinet_code="E0000C", name="Investor C"))

    # 報告書作成 (A)
    filing_a = Filing(
        doc_id="DOC_A_01",
        filer_id=filer_a.id,
        issuer_id=issuer.id,
        submit_date=datetime(2025, 1, 1),
        doc_description="Report A",
    )
    db.add(filing_a)
    db.flush()
    db.add(HoldingDetail(filing_id=filing_a.id, shares_held=100, holding_ratio=5.0))

    # 報告書作成 (B) - 古い
    filing_b_old = Filing(
        doc_id="DOC_B_01",
        filer_id=filer_b.id,
        issuer_id=issuer.id,
        submit_date=datetime(2025, 1, 1),
        doc_description="Report B Old",
    )
    db.add(filing_b_old)
    db.flush()
    db.add(HoldingDetail(filing_id=filing_b_old.id, shares_held=200, holding_ratio=10.0))

    # 報告書作成 (B) - 最新
    filing_b_new = Filing(
        doc_id="DOC_B_02",
        filer_id=filer_b.id,
        issuer_id=issuer.id,
        submit_date=datetime(2025, 2, 1),
        doc_description="Report B New",
    )
    db.add(filing_b_new)
    db.flush()
    db.add(HoldingDetail(filing_id=filing_b_new.id, shares_held=250, holding_ratio=12.5))

    db.commit()

    # APIコール
    response = await client.get(f"/api/issuers/{issuer.id}/ownerships")
    assert response.status_code == 200
    data = response.json()

    # 構造確認
    assert "issuer" in data
    assert data["issuer"]["name"] == "Target Corp"
    assert "ownerships" in data
    assert len(data["ownerships"]) == 2  # AとBのみ

    # 内容確認 (Bは最新の12.5%が取得されるべき)
    ownerships = {d["filer_name"]: d for d in data["ownerships"]}

    assert "Investor A" in ownerships
    assert ownerships["Investor A"]["holding_ratio"] == 5.0

    assert "Investor B" in ownerships
    assert ownerships["Investor B"]["holding_ratio"] == 12.5
    assert ownerships["Investor B"]["shares_held"] == 250
