from backend import crud

def test_create_filer_crud(db):
    """CRUD経由で提出者が新モデル（FilerCode）も含めて正しく作成されるか"""
    filer = crud.create_filer(db, edinet_code="E99999", name="新規提出者", sec_code="12345")
    
    assert filer.name == "新規提出者"
    assert len(filer.filer_codes) == 1
    assert filer.filer_codes[0].edinet_code == "E99999"
    assert filer.primary_edinet_code == "E99999"

def test_get_filer_by_edinet_code(db, sample_data):
    """EDINETコード検索が統合後のモデルで正しく機能するか"""
    # 既存のコードで検索
    filer = crud.get_filer_by_edinet_code(db, "E00000")
    assert filer is not None
    assert filer.name == "テスト提出者"
    
    # 存在しないコード
    assert crud.get_filer_by_edinet_code(db, "EXXXXX") is None

def test_get_filer_stats(db, sample_data):
    """統計情報（報告書数、銘柄数）が正しく計算されるか"""
    filer_id = sample_data["filer"].id
    stats = crud.get_filer_stats(db, filer_id)
    
    assert stats["filing_count"] == 1
    assert stats["issuer_count"] == 1
    assert stats["latest_filing_date"] is not None
