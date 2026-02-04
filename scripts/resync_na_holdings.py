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
import asyncio
from typing import Optional

from sqlalchemy import delete, or_, select

from backend.database import get_db_session
from backend.models import Filer, FilerCode, Filing, HoldingDetail


async def list_na_holdings(filer_edinet_code: Optional[str] = None):
    """N/Aの保有詳細レコードを一覧表示"""
    async with get_db_session() as db:
        stmt = (
            select(HoldingDetail, Filing, Filer)
            .join(Filing, HoldingDetail.filing_id == Filing.id)
            .join(Filer, Filing.filer_id == Filer.id)
            .where(or_(HoldingDetail.shares_held == None, HoldingDetail.holding_ratio == None))
        )

        if filer_edinet_code:
            filer_code_stmt = select(FilerCode).where(FilerCode.edinet_code == filer_edinet_code)
            filer_code = (await db.execute(filer_code_stmt)).scalar_one_or_none()
            if filer_code:
                stmt = stmt.where(Filing.filer_id == filer_code.filer_id)

        stmt = stmt.order_by(Filing.submit_date.desc())
        results = (await db.execute(stmt)).all()

        print(f"\n【N/Aのholding_detailsレコード: {len(results)}件】\n")
        for hd, filing, filer in results:
            print(f"  ID={hd.id}, FilingID={filing.id}, DocID={filing.doc_id}")
            print(f"    提出日: {filing.submit_date}, 提出者: {filer.name}")
            print(f"    株数: {hd.shares_held}, 比率: {hd.holding_ratio}")
            print()

        return results


async def delete_na_holdings(filer_edinet_code: Optional[str] = None, dry_run: bool = False):
    """N/Aの保有詳細レコードを削除"""
    async with get_db_session() as db:
        # 削除対象のIDを取得
        stmt = select(HoldingDetail.id).join(Filing, HoldingDetail.filing_id == Filing.id).where(
            (HoldingDetail.shares_held == None) & (HoldingDetail.holding_ratio == None)
        )

        if filer_edinet_code:
            filer_code_stmt = select(FilerCode).where(FilerCode.edinet_code == filer_edinet_code)
            filer_code = (await db.execute(filer_code_stmt)).scalar_one_or_none()
            if filer_code:
                stmt = stmt.where(Filing.filer_id == filer_code.filer_id)

        na_ids = (await db.execute(stmt)).scalars().all()

        print(f"\n削除対象のholding_details: {len(na_ids)}件")

        if dry_run:
            print("(dry-runモード: 実際の削除は行いません)")
            return len(na_ids)

        if na_ids:
            delete_stmt = delete(HoldingDetail).where(HoldingDetail.id.in_(na_ids))
            result = await db.execute(delete_stmt)
            await db.commit()
            deleted = result.rowcount
            print(f"削除完了: {deleted}件")
            return deleted

        return 0


async def async_main():
    parser = argparse.ArgumentParser(description="N/Aのholding_detailsを再取得")
    parser.add_argument("--filer", type=str, default=None, help="提出者EDINETコード（例: E04948）")
    parser.add_argument("--dry-run", action="store_true", help="削除対象の確認のみ（実際には削除しない）")
    parser.add_argument("--list", action="store_true", help="N/Aレコードを一覧表示のみ")

    args = parser.parse_args()

    if args.list:
        await list_na_holdings(args.filer)
    else:
        deleted = await delete_na_holdings(args.filer, args.dry_run)
        if deleted > 0 and not args.dry_run:
            print("\n次のコマンドで再取得してください:")
            if args.filer:
                print(f"  python backend/sync_edinet.py --sync-holdings --filer {args.filer}")
            else:
                print("  python backend/sync_edinet.py --sync-holdings")


if __name__ == "__main__":
    asyncio.run(async_main())
