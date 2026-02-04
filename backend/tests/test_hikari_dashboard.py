from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend import crud
from backend.models import Filer, Filing, HoldingDetail, Issuer


async def test_get_issuers_by_filer_includes_purpose(db: AsyncSession) -> None:
    # Prepare test data
    filer = Filer(edinet_code="E00001", name="Hikari Test", sec_code="9999")
    db.add(filer)
    await db.flush()

    issuer = Issuer(edinet_code="E11111", name="Target Corp", sec_code="1001")
    db.add(issuer)
    await db.flush()

    filing = Filing(
        doc_id="S_TEST_01",
        filer_id=filer.id,
        issuer_id=issuer.id,
        submit_date=datetime.now(UTC),
        doc_description="Report",
    )
    db.add(filing)
    await db.flush()

    expected_purpose = "Pure Investment"
    holding = HoldingDetail(
        filing_id=filing.id, shares_held=1000, holding_ratio=1.5, purpose=expected_purpose
    )
    db.add(holding)
    await db.commit()

    # Call the function under test
    result = await crud.get_issuers_by_filer(db, filer.id)

    # Verify result
    assert result["total"] == 1
    item = result["items"][0]

    # This assertion is expected to fail initially as 'latest_purpose' is not yet implemented
    assert "latest_purpose" in item
    assert item["latest_purpose"] == expected_purpose
