"""
N/A（保有株数・保有比率が取得できていない）のholding_detailsを削除し、再取得するスクリプト

使用方法:
    python scripts/resync_na_holdings.py --filer E04948
    python scripts/resync_na_holdings.py --filer E04948 --dry-run  # 削除対象の確認のみ
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse

from backend.database import get_db_session
from backend.models import Filer, FilerCode, Filing, HoldingDetail


def list_na_holdings(filer_edinet_code: str = None):
    """N/Aの保有詳細レコードを一覧表示"""
    with get_db_session() as db:
        query = db.query(HoldingDetail, Filing, Filer).join(
            Filing, HoldingDetail.filing_id == Filing.id
        ).join(
            Filer, Filing.filer_id == Filer.id
        ).filter(
            (HoldingDetail.shares_held == None) | (HoldingDetail.holding_ratio == None)
        )

        if filer_edinet_code:
            filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == filer_edinet_code).first()
            if filer_code:
                query = query.filter(Filing.filer_id == filer_code.filer_id)

        results = query.order_by(Filing.submit_date.desc()).all()

        print(f"\n【N/Aのholding_detailsレコード: {len(results)}件】\n")
        for hd, filing, filer in results:
            print(f"  ID={hd.id}, FilingID={filing.id}, DocID={filing.doc_id}")
            print(f"    提出日: {filing.submit_date}, 提出者: {filer.name}")
            print(f"    株数: {hd.shares_held}, 比率: {hd.holding_ratio}")
            print()

        return results


def delete_na_holdings(filer_edinet_code: str = None, dry_run: bool = False):
    """N/Aの保有詳細レコードを削除"""
    with get_db_session() as db:
        # 削除対象のIDを取得
        query = db.query(HoldingDetail.id).join(
            Filing, HoldingDetail.filing_id == Filing.id
        ).filter(
            (HoldingDetail.shares_held == None) & (HoldingDetail.holding_ratio == None)
        )

        if filer_edinet_code:
            filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == filer_edinet_code).first()
            if filer_code:
                query = query.filter(Filing.filer_id == filer_code.filer_id)

        na_ids = [row[0] for row in query.all()]

        print(f"\n削除対象のholding_details: {len(na_ids)}件")

        if dry_run:
            print("(dry-runモード: 実際の削除は行いません)")
            return len(na_ids)

        if na_ids:
            deleted = db.query(HoldingDetail).filter(HoldingDetail.id.in_(na_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"削除完了: {deleted}件")
            return deleted

        return 0


def main():
    parser = argparse.ArgumentParser(description="N/Aのholding_detailsを再取得")
    parser.add_argument("--filer", type=str, default=None, help="提出者EDINETコード（例: E04948）")
    parser.add_argument("--dry-run", action="store_true", help="削除対象の確認のみ（実際には削除しない）")
    parser.add_argument("--list", action="store_true", help="N/Aレコードを一覧表示のみ")

    args = parser.parse_args()

    if args.list:
        list_na_holdings(args.filer)
    else:
        deleted = delete_na_holdings(args.filer, args.dry_run)
        if deleted > 0 and not args.dry_run:
            print("\n次のコマンドで再取得してください:")
            if args.filer:
                print(f"  python backend/sync_edinet.py --sync-holdings --filer {args.filer}")
            else:
                print("  python backend/sync_edinet.py --sync-holdings")


if __name__ == "__main__":
    main()
