from datetime import datetime

from backend import crud
from backend.models import Filer, Filing, HoldingDetail, Issuer


def test_get_issuers_by_filer_includes_purpose(db):
    # Prepare test data
    filer = Filer(edinet_code="E00001", name="Hikari Test", sec_code="9999")
    db.add(filer)
    db.flush()

    issuer = Issuer(edinet_code="E11111", name="Target Corp", sec_code="1001")
    db.add(issuer)
    db.flush()

    filing = Filing(
        doc_id="S_TEST_01",
        filer_id=filer.id,
        issuer_id=issuer.id,
        submit_date=datetime.now(),
        doc_description="Report",
    )
    db.add(filing)
    db.flush()

    expected_purpose = "Pure Investment"
    holding = HoldingDetail(
        filing_id=filing.id, shares_held=1000, holding_ratio=1.5, purpose=expected_purpose
    )
    db.add(holding)
    db.commit()

    # Call the function under test
    result = crud.get_issuers_by_filer(db, filer.id)

    # Verify the result
    assert result["total"] == 1
    item = result["items"][0]

    # This assertion is expected to fail initially as 'latest_purpose' is not yet implemented
    assert "latest_purpose" in item
    assert item["latest_purpose"] == expected_purpose
