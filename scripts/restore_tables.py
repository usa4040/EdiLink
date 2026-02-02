import os
import sys

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db_session
from backend.models import Base, Filer, FilerCode, Filing, HoldingDetail, Issuer, get_engine


def clean_row(row):
    """Convert pandas NaN/NaT to None for database insertion"""
    clean = {}
    for key, value in row.items():
        if pd.isna(value):
            clean[key] = None
        else:
            clean[key] = value
    return clean

def import_table(db, model, csv_path, date_columns=None):
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
            db.merge(record)
        db.commit()
        print(f"Imported {len(records)} records into {model.__tablename__}")

def main():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    import_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'import')

    with get_db_session() as db:
        # 1. Filers
        import_table(db, Filer, os.path.join(import_dir, 'filers.csv'), date_columns=['created_at', 'updated_at'])

        # 2. Issuers
        import_table(db, Issuer, os.path.join(import_dir, 'issuers.csv'), date_columns=['created_at', 'updated_at'])

        # 3. FilerCodes
        import_table(db, FilerCode, os.path.join(import_dir, 'filer_codes.csv'), date_columns=['created_at'])

        # 4. Filings
        import_table(db, Filing, os.path.join(import_dir, 'filings.csv'), date_columns=['submit_date', 'created_at'])

        # 5. HoldingDetails
        import_table(db, HoldingDetail, os.path.join(import_dir, 'holding_details.csv'), date_columns=['created_at'])

    print("Data import completed successfully.")

if __name__ == "__main__":
    main()
