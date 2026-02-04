import asyncio
import os
import sys
from typing import Any

import pandas as pd
from sqlalchemy import select

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import async_engine, get_db_session
from backend.models import Base, Filer, FilerCode, Filing, HoldingDetail, Issuer


def clean_row(row: Any) -> dict[str, Any]:
    """Convert pandas NaN/NaT to None for database insertion"""
    clean: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            clean[key] = None
        else:
            clean[key] = value
    return clean

async def import_table(db, model, csv_path, date_columns=None):
    if not os.path.exists(csv_path):
        print(f"Skipping {csv_path} (not found)")
        return

    print(f"Importing {model.__tablename__} from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Handle date columns
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

    records = []
    for _, row in df.iterrows():
        data = clean_row(row)
        records.append(model(**data))

    if records:
        # Check if table is empty to decide whether to set IDs explicitly or handle conflicts
        # For simplicity in this task, we assume we want to load this exact data.
        # We merge records to handle potential existing IDs if we are updating,
        # but since we are importing a dump, we might want to just add them.
        # Using merge avoids primary key compilation errors if data exists.
        for record in records:
            await db.merge(record)
        await db.commit()
        print(f"Imported {len(records)} records into {model.__tablename__}")


async def async_main():
    # Note: metadata.create_all is typically synchronous and requires a sync engine.
    # For async, we should use a connection to run it.
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    import_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "import"
    )

    async with get_db_session() as db:
        # 1. Filers
        await import_table(
            db, Filer, os.path.join(import_dir, "filers.csv"), date_columns=["created_at", "updated_at"]
        )

        # 2. Issuers
        await import_table(
            db,
            Issuer,
            os.path.join(import_dir, "issuers.csv"),
            date_columns=["created_at", "updated_at"],
        )

        # 3. FilerCodes
        await import_table(
            db, FilerCode, os.path.join(import_dir, "filer_codes.csv"), date_columns=["created_at"]
        )

        # 4. Filings
        await import_table(
            db, Filing, os.path.join(import_dir, "filings.csv"), date_columns=["submit_date", "created_at"]
        )

        # 5. HoldingDetails
        await import_table(
            db, HoldingDetail, os.path.join(import_dir, "holding_details.csv"), date_columns=["created_at"]
        )

    print("Data import completed successfully.")


if __name__ == "__main__":
    asyncio.run(async_main())
