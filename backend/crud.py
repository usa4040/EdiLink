
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models import Filer, FilerCode, Filing, HoldingDetail, Issuer


def get_filers(db: Session, skip: int = 0, limit: int = 50, search: str = None) -> dict:
    """提出者をページネーション付きで取得（統計情報も含む）"""
    # ベースクエリ
    query = db.query(Filer)

    # 検索フィルタ
    if search:
        query = query.filter(Filer.name.ilike(f"%{search}%"))

    # 総数を取得
    total = query.count()

    # 統計情報をサブクエリで一括取得
    from sqlalchemy import desc, func

    # Filing統計をサブクエリ化
    filing_stats = (
        db.query(
            Filing.filer_id,
            func.count(Filing.id).label("filing_count"),
            func.count(func.distinct(Filing.issuer_id)).label("issuer_count"),
            func.max(Filing.submit_date).label("latest_filing_date"),
        )
        .group_by(Filing.filer_id)
        .subquery()
    )

    # メインクエリ（統計情報をJOIN）
    results = (
        query.outerjoin(filing_stats, Filer.id == filing_stats.c.filer_id)
        .add_columns(
            filing_stats.c.filing_count,
            filing_stats.c.issuer_count,
            filing_stats.c.latest_filing_date,
        )
        .order_by(desc(filing_stats.c.latest_filing_date))
        .offset(skip)
        .limit(limit)
        .all()
    )

    filers = []
    for filer, filing_count, issuer_count, latest_filing_date in results:
        filers.append(
            {
                "filer": filer,
                "filing_count": filing_count or 0,
                "issuer_count": issuer_count or 0,
                "latest_filing_date": latest_filing_date,
            }
        )

    return {"items": filers, "total": total, "skip": skip, "limit": limit}


def get_filer_by_id(db: Session, filer_id: int) -> Filer | None:
    """IDで提出者を取得"""
    return db.query(Filer).filter(Filer.id == filer_id).first()


def get_filer_by_edinet_code(db: Session, edinet_code: str) -> Filer | None:
    """EDINETコードで提出者を取得"""
    filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()
    return filer_code.filer if filer_code else None


def create_filer(db: Session, edinet_code: str, name: str, sec_code: str = None) -> Filer:
    """新しい提出者を作成（FilerCodeも同時に作成）"""
    filer = Filer(edinet_code=edinet_code, name=name, sec_code=sec_code)
    db.add(filer)
    db.flush()

    filer_code = FilerCode(filer_id=filer.id, edinet_code=edinet_code, name=name)
    db.add(filer_code)
    db.commit()
    db.refresh(filer)
    return filer


def get_issuers_by_filer(
    db: Session, filer_id: int, skip: int = 0, limit: int = 50, search: str = None
) -> dict:
    """提出者が保有している発行体（銘柄）一覧をページネーション付きで取得"""
    # 各発行体について、最新の報告書情報を取得
    subquery = (
        db.query(
            Filing.issuer_id,
            func.max(Filing.submit_date).label("latest_date"),
            func.count(Filing.id).label("filing_count"),
        )
        .filter(Filing.filer_id == filer_id)
        .filter(Filing.issuer_id.isnot(None))
        .group_by(Filing.issuer_id)
        .subquery()
    )

    # ベースクエリ
    base_query = db.query(Issuer, subquery.c.latest_date, subquery.c.filing_count).join(
        subquery, Issuer.id == subquery.c.issuer_id
    )

    # 検索フィルタ
    if search:
        base_query = base_query.filter(
            (Issuer.name.ilike(f"%{search}%"))
            | (Issuer.sec_code.ilike(f"%{search}%"))
            | (Issuer.edinet_code.ilike(f"%{search}%"))
        )

    # 総数を取得
    total = base_query.count()

    # ページネーション適用
    results = base_query.order_by(desc(subquery.c.latest_date)).offset(skip).limit(limit).all()

    # 各銘柄の最新保有比率と増減比を取得（バッチ処理）
    issuer_ids = [issuer.id for issuer, _, _ in results]

    # 最新2件のFilingをサブクエリで取得
    if issuer_ids:
        # 各issuerの最新のHoldingDetailを取得

        # 最新のFiling IDを取得するサブクエリ
        latest_filing_subq = (
            db.query(Filing.issuer_id, func.max(Filing.id).label("latest_filing_id"))
            .filter(Filing.filer_id == filer_id)
            .filter(Filing.issuer_id.in_(issuer_ids))
            .group_by(Filing.issuer_id)
            .subquery()
        )

        # 最新のHoldingDetailを取得
        latest_holdings = (
            db.query(
                latest_filing_subq.c.issuer_id, HoldingDetail.holding_ratio, HoldingDetail.purpose
            )
            .join(HoldingDetail, HoldingDetail.filing_id == latest_filing_subq.c.latest_filing_id)
            .all()
        )

        holdings_map = {
            issuer_id: {"ratio": ratio, "purpose": purpose}
            for issuer_id, ratio, purpose in latest_holdings
        }
    else:
        holdings_map = {}

    # 結果を構築
    issuer_data = []
    for issuer, latest_date, filing_count in results:
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


def get_issuers(db: Session, skip: int = 0, limit: int = 50, search: str = None) -> dict:
    """銘柄一覧をページネーション付きで取得"""
    query = db.query(Issuer)

    if search:
        query = query.filter(
            (Issuer.name.ilike(f"%{search}%"))
            | (Issuer.sec_code.ilike(f"%{search}%"))
            | (Issuer.edinet_code.ilike(f"%{search}%"))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"items": items, "total": total, "skip": skip, "limit": limit}


def get_issuer_by_id(db: Session, issuer_id: int) -> Issuer | None:
    """IDで発行体を取得"""
    return db.query(Issuer).filter(Issuer.id == issuer_id).first()


def get_filings_by_issuer_and_filer(db: Session, issuer_id: int, filer_id: int) -> list[Filing]:
    """特定の発行体・提出者の報告書履歴を取得"""
    return (
        db.query(Filing)
        .filter(Filing.issuer_id == issuer_id)
        .filter(Filing.filer_id == filer_id)
        .order_by(desc(Filing.submit_date))
        .all()
    )


def get_filings_by_filer(db: Session, filer_id: int, limit: int = 100) -> list[Filing]:
    """提出者のすべての報告書を取得"""
    return (
        db.query(Filing)
        .filter(Filing.filer_id == filer_id)
        .order_by(desc(Filing.submit_date))
        .limit(limit)
        .all()
    )


def get_filer_stats(db: Session, filer_id: int) -> dict:
    """提出者の統計情報を取得"""
    filing_count = db.query(func.count(Filing.id)).filter(Filing.filer_id == filer_id).scalar()
    issuer_count = (
        db.query(func.count(func.distinct(Filing.issuer_id)))
        .filter(Filing.filer_id == filer_id)
        .filter(Filing.issuer_id.isnot(None))
        .scalar()
    )
    latest_filing = (
        db.query(Filing)
        .filter(Filing.filer_id == filer_id)
        .order_by(desc(Filing.submit_date))
        .first()
    )

    return {
        "filing_count": filing_count,
        "issuer_count": issuer_count,
        "latest_filing_date": latest_filing.submit_date if latest_filing else None,
    }


def get_issuer_ownerships(db: Session, issuer_id: int) -> list[dict]:
    """
    指定された銘柄を保有している投資家の最新状況を取得
    """
    # 各投資家ごとに、対象銘柄に対する最新のFiling IDを取得するサブクエリ
    latest_filing_subq = (
        db.query(
            Filing.filer_id,
            func.max(Filing.submit_date).label("latest_submit_date"),
            func.max(Filing.id).label("latest_filing_id"),
        )
        .filter(Filing.issuer_id == issuer_id)
        .group_by(Filing.filer_id)
        .subquery()
    )

    # 最新Filingの情報とHoldingDetail、Filer情報を結合して取得
    results = (
        db.query(
            Filer.id.label("filer_id"),
            Filer.name.label("filer_name"),
            latest_filing_subq.c.latest_submit_date,
            HoldingDetail.shares_held,
            HoldingDetail.holding_ratio,
            HoldingDetail.purpose,
        )
        .join(latest_filing_subq, Filer.id == latest_filing_subq.c.filer_id)
        .join(HoldingDetail, HoldingDetail.filing_id == latest_filing_subq.c.latest_filing_id)
        .order_by(desc(HoldingDetail.holding_ratio))  # 保有比率の高い順
        .all()
    )

    ownerships = []
    for row in results:
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
