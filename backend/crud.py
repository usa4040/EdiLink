from datetime import datetime
from typing import Sequence, TypedDict, cast

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from backend.models import Filer, FilerCode, Filing, HoldingDetail, Issuer


class FilerWithStats(TypedDict):
    filer: Filer
    filing_count: int
    issuer_count: int
    latest_filing_date: datetime | None


class FilerListResponse(TypedDict):
    items: Sequence[FilerWithStats]
    total: int
    skip: int
    limit: int


class FilerStats(TypedDict):
    filing_count: int
    issuer_count: int
    latest_filing_date: datetime | None


class IssuerWithStats(TypedDict):
    issuer: Issuer
    latest_filing_date: datetime | None
    filing_count: int
    latest_ratio: float | None
    latest_purpose: str | None
    ratio_change: float | None


class IssuerListResponse(TypedDict):
    items: Sequence[IssuerWithStats]
    total: int
    skip: int
    limit: int


class PaginatedIssuers(TypedDict):
    items: Sequence[Issuer]
    total: int
    skip: int
    limit: int


class OwnershipInfo(TypedDict):
    filer_id: int
    filer_name: str
    latest_submit_date: datetime | None
    shares_held: int | None
    holding_ratio: float | None
    purpose: str | None


async def get_filers(
    db: AsyncSession, skip: int = 0, limit: int = 50, search: str | None = None
) -> FilerListResponse:
    """提出者をページネーション付きで取得（統計情報も含む）"""
    # ベースクエリの構築
    base_stmt = select(Filer)

    # 検索フィルタ
    if search:
        base_stmt = base_stmt.where(Filer.name.ilike(f"%{search}%"))

    # 総数を取得
    count_stmt = select(func.count()).select_from(Filer)
    if search:
        count_stmt = count_stmt.where(Filer.name.ilike(f"%{search}%"))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # 統計情報をサブクエリで一括取得
    filing_stats = (
        select(
            Filing.filer_id,
            func.count(Filing.id).label("filing_count"),
            func.count(func.distinct(Filing.issuer_id)).label("issuer_count"),
            func.max(Filing.submit_date).label("latest_filing_date"),
        )
        .group_by(Filing.filer_id)
        .subquery()
    )

    # メインクエリ（統計情報をJOIN）
    stmt = (
        select(
            Filer,
            filing_stats.c.filing_count,
            filing_stats.c.issuer_count,
            filing_stats.c.latest_filing_date,
        )
        .options(selectinload(Filer.filer_codes))
        .select_from(Filer)
        .outerjoin(filing_stats, Filer.id == filing_stats.c.filer_id)
        .order_by(desc(filing_stats.c.issuer_count))
        .offset(skip)
        .limit(limit)
    )
    if search:
        stmt = stmt.where(Filer.name.ilike(f"%{search}%"))

    result = await db.execute(stmt)
    rows = result.all()

    filers: list[FilerWithStats] = []
    for filer, filing_count, issuer_count, latest_filing_date in rows:
        filers.append(
            {
                "filer": filer,
                "filing_count": filing_count or 0,
                "issuer_count": issuer_count or 0,
                "latest_filing_date": latest_filing_date,
            }
        )

    return {"items": filers, "total": total, "skip": skip, "limit": limit}


async def get_filer_by_id(db: AsyncSession, filer_id: int) -> Filer | None:
    """IDで提出者を取得 (filer_codesをEager Loading)"""
    stmt = select(Filer).where(Filer.id == filer_id).options(selectinload(Filer.filer_codes))
    result = await db.execute(stmt)
    return cast(Filer | None, result.scalar_one_or_none())


async def get_filer_by_edinet_code(db: AsyncSession, edinet_code: str) -> Filer | None:
    """EDINETコードで提出者を取得"""
    stmt = (
        select(FilerCode)
        .where(FilerCode.edinet_code == edinet_code)
        .options(joinedload(FilerCode.filer).selectinload(Filer.filer_codes))
    )
    result = await db.execute(stmt)
    filer_code = result.scalar_one_or_none()
    return cast(Filer | None, filer_code.filer if filer_code else None)


async def create_filer(
    db: AsyncSession, edinet_code: str, name: str, sec_code: str | None = None
) -> Filer:
    """新しい提出者を作成（FilerCodeも同時に作成）"""
    filer = Filer(edinet_code=edinet_code, name=name, sec_code=sec_code)
    db.add(filer)
    await db.flush()

    filer_code = FilerCode(filer_id=filer.id, edinet_code=edinet_code, name=name)
    db.add(filer_code)
    await db.flush()
    await db.refresh(filer, attribute_names=["filer_codes"])

    return filer


async def get_issuers_by_filer(
    db: AsyncSession, filer_id: int, skip: int = 0, limit: int = 50, search: str | None = None
) -> IssuerListResponse:
    """提出者が保有している発行体（銘柄）一覧をページネーション付きで取得"""
    # 各発行体について、最新の報告書情報を取得
    subquery = (
        select(
            Filing.issuer_id,
            func.max(Filing.submit_date).label("latest_date"),
            func.count(Filing.id).label("filing_count"),
        )
        .where(Filing.filer_id == filer_id)
        .where(Filing.issuer_id.isnot(None))
        .group_by(Filing.issuer_id)
        .subquery()
    )

    # ベースクエリ
    base_stmt = select(Issuer, subquery.c.latest_date, subquery.c.filing_count).join(
        subquery, Issuer.id == subquery.c.issuer_id
    )

    # 検索フィルタ
    if search:
        search_filter = (
            Issuer.name.ilike(f"%{search}%")
            | Issuer.sec_code.ilike(f"%{search}%")
            | Issuer.edinet_code.ilike(f"%{search}%")
        )
        base_stmt = base_stmt.where(search_filter)

    # 総数を取得
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # ページネーション適用
    stmt = base_stmt.order_by(desc(subquery.c.latest_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    # 各銘柄の最新保有比率と増減比を取得（バッチ処理）
    issuer_ids = [issuer.id for issuer, _, _ in rows]

    # 最新のFiling IDを取得するサブクエリ
    holdings_map = {}
    if issuer_ids:
        latest_filing_subq = (
            select(Filing.issuer_id, func.max(Filing.id).label("latest_filing_id"))
            .where(Filing.filer_id == filer_id)
            .where(Filing.issuer_id.in_(issuer_ids))
            .group_by(Filing.issuer_id)
            .subquery()
        )

        # 最新のHoldingDetailを取得
        holdings_stmt = select(
            latest_filing_subq.c.issuer_id,
            HoldingDetail.holding_ratio,
            HoldingDetail.purpose,
        ).join(HoldingDetail, HoldingDetail.filing_id == latest_filing_subq.c.latest_filing_id)
        holdings_result = await db.execute(holdings_stmt)
        latest_holdings = holdings_result.all()

        holdings_map = {
            issuer_id: {"ratio": ratio, "purpose": purpose}
            for issuer_id, ratio, purpose in latest_holdings
        }

    # 結果を構築
    issuer_data: list[IssuerWithStats] = []
    for issuer, latest_date, filing_count in rows:
        holding_info = holdings_map.get(issuer.id, {})
        latest_ratio = holding_info.get("ratio")
        latest_purpose = holding_info.get("purpose")

        issuer_data.append(
            {
                "issuer": issuer,
                "latest_filing_date": latest_date,
                "filing_count": filing_count,
                "latest_ratio": latest_ratio,
                "latest_purpose": latest_purpose,
                "ratio_change": None,  # 簡略化のため増減は省略（詳細ページで表示）
            }
        )

    return {"items": issuer_data, "total": total, "skip": skip, "limit": limit}


async def get_issuers(
    db: AsyncSession, skip: int = 0, limit: int = 50, search: str | None = None
) -> PaginatedIssuers:
    """銘柄一覧をページネーション付きで取得"""
    base_stmt = select(Issuer)

    if search:
        search_filter = (
            Issuer.name.ilike(f"%{search}%")
            | Issuer.sec_code.ilike(f"%{search}%")
            | Issuer.edinet_code.ilike(f"%{search}%")
        )
        base_stmt = base_stmt.where(search_filter)

    # 総数を取得
    count_stmt = select(func.count()).select_from(Issuer)
    if search:
        count_stmt = count_stmt.where(search_filter)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # ページネーション適用
    stmt = base_stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {"items": list(items), "total": total, "skip": skip, "limit": limit}


async def get_issuer_by_id(db: AsyncSession, issuer_id: int) -> Issuer | None:
    """IDで発行体を取得"""
    stmt = select(Issuer).where(Issuer.id == issuer_id)
    result = await db.execute(stmt)
    return cast(Issuer | None, result.scalar_one_or_none())


async def get_filings_by_issuer_and_filer(
    db: AsyncSession, issuer_id: int, filer_id: int
) -> Sequence[Filing]:
    """特定の発行体・提出者の報告書履歴を取得 (関連データをEager Loading)"""
    stmt = (
        select(Filing)
        .where(Filing.issuer_id == issuer_id)
        .where(Filing.filer_id == filer_id)
        .options(
            joinedload(Filing.filer),
            joinedload(Filing.issuer),
            selectinload(Filing.holding_details),
        )
        .order_by(desc(Filing.submit_date))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_filings_by_filer(db: AsyncSession, filer_id: int, limit: int = 100) -> Sequence[Filing]:
    """提出者のすべての報告書を取得 (issuerとholding_detailsをEager Loading)"""
    stmt = (
        select(Filing)
        .where(Filing.filer_id == filer_id)
        .options(joinedload(Filing.issuer), selectinload(Filing.holding_details))
        .order_by(desc(Filing.submit_date))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_filer_stats(db: AsyncSession, filer_id: int) -> FilerStats:
    """提出者の統計情報を取得"""
    filing_count_stmt = select(func.count(Filing.id)).where(Filing.filer_id == filer_id)
    filing_count_result = await db.execute(filing_count_stmt)
    filing_count = filing_count_result.scalar_one()

    issuer_count_stmt = (
        select(func.count(func.distinct(Filing.issuer_id)))
        .where(Filing.filer_id == filer_id)
        .where(Filing.issuer_id.isnot(None))
    )
    issuer_count_result = await db.execute(issuer_count_stmt)
    issuer_count = issuer_count_result.scalar_one()

    latest_filing_stmt = (
        select(Filing)
        .where(Filing.filer_id == filer_id)
        .order_by(desc(Filing.submit_date))
        .limit(1)
    )
    latest_filing_result = await db.execute(latest_filing_stmt)
    latest_filing = latest_filing_result.scalar_one_or_none()

    return {
        "filing_count": filing_count,
        "issuer_count": issuer_count,
        "latest_filing_date": latest_filing.submit_date if latest_filing else None,
    }


async def get_issuer_ownerships(db: AsyncSession, issuer_id: int) -> Sequence[OwnershipInfo]:
    """
    指定された銘柄を保有している投資家の最新状況を取得
    """
    # 各投資家ごとに、対象銘柄に対する最新のFiling IDを取得するサブクエリ
    latest_filing_subq = (
        select(
            Filing.filer_id,
            func.max(Filing.submit_date).label("latest_submit_date"),
            func.max(Filing.id).label("latest_filing_id"),
        )
        .where(Filing.issuer_id == issuer_id)
        .group_by(Filing.filer_id)
        .subquery()
    )

    # 最新Filingの情報とHoldingDetail、Filer情報を結合して取得
    stmt = (
        select(
            Filer.id.label("filer_id"),
            Filer.name.label("filer_name"),
            latest_filing_subq.c.latest_submit_date,
            HoldingDetail.shares_held,
            HoldingDetail.holding_ratio,
            HoldingDetail.purpose,
        )
        .join(latest_filing_subq, Filer.id == latest_filing_subq.c.filer_id)
        .join(HoldingDetail, HoldingDetail.filing_id == latest_filing_subq.c.latest_filing_id)
        .order_by(desc(HoldingDetail.holding_ratio))
    )

    result = await db.execute(stmt)
    rows = result.all()

    ownerships: list[OwnershipInfo] = []
    for row in rows:
        # Pydanticモデルではなく辞書で返す（呼び出し元で整形）
        ownerships.append(
            {
                "filer_id": row.filer_id,
                "filer_name": row.filer_name,
                "latest_submit_date": row.latest_submit_date,
                "shares_held": row.shares_held,
                "holding_ratio": row.holding_ratio,
                "purpose": row.purpose,
            }
        )

    return ownerships
