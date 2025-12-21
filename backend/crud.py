from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from backend.models import Filer, FilerCode, Issuer, Filing, HoldingDetail


def get_filers(db: Session) -> List[Filer]:
    """すべての提出者を取得"""
    return db.query(Filer).all()


def get_filer_by_id(db: Session, filer_id: int) -> Optional[Filer]:
    """IDで提出者を取得"""
    return db.query(Filer).filter(Filer.id == filer_id).first()


def get_filer_by_edinet_code(db: Session, edinet_code: str) -> Optional[Filer]:
    """EDINETコードで提出者を取得"""
    filer_code = db.query(FilerCode).filter(FilerCode.edinet_code == edinet_code).first()
    return filer_code.filer if filer_code else None


def create_filer(db: Session, edinet_code: str, name: str, sec_code: str = None) -> Filer:
    """新しい提出者を作成（FilerCodeも同時に作成）"""
    filer = Filer(name=name, sec_code=sec_code)
    db.add(filer)
    db.flush()
    
    filer_code = FilerCode(filer_id=filer.id, edinet_code=edinet_code, name=name)
    db.add(filer_code)
    db.commit()
    db.refresh(filer)
    return filer


def get_issuers_by_filer(db: Session, filer_id: int) -> List[dict]:
    """提出者が保有している発行体（銘柄）一覧を取得"""
    # 各発行体について、最新の報告書情報を取得
    subquery = (
        db.query(
            Filing.issuer_id,
            func.max(Filing.submit_date).label("latest_date"),
            func.count(Filing.id).label("filing_count")
        )
        .filter(Filing.filer_id == filer_id)
        .filter(Filing.issuer_id.isnot(None))
        .group_by(Filing.issuer_id)
        .subquery()
    )
    
    results = (
        db.query(Issuer, subquery.c.latest_date, subquery.c.filing_count)
        .join(subquery, Issuer.id == subquery.c.issuer_id)
        .order_by(desc(subquery.c.latest_date))
        .all()
    )
    
    # 各銘柄の最新保有比率と増減比を取得
    issuer_data = []
    for issuer, latest_date, filing_count in results:
        # この銘柄の最新2件のFilingを取得
        latest_filings = (
            db.query(Filing)
            .filter(Filing.filer_id == filer_id)
            .filter(Filing.issuer_id == issuer.id)
            .order_by(desc(Filing.submit_date))
            .limit(2)
            .all()
        )
        
        latest_ratio = None
        ratio_change = None
        
        if latest_filings:
            # 最新の報告書のHoldingDetailを取得
            latest_holding = (
                db.query(HoldingDetail)
                .filter(HoldingDetail.filing_id == latest_filings[0].id)
                .first()
            )
            if latest_holding and latest_holding.holding_ratio is not None:
                latest_ratio = latest_holding.holding_ratio
                
                # 2件目がある場合は増減比を計算
                if len(latest_filings) > 1:
                    prev_holding = (
                        db.query(HoldingDetail)
                        .filter(HoldingDetail.filing_id == latest_filings[1].id)
                        .first()
                    )
                    if prev_holding and prev_holding.holding_ratio is not None:
                        ratio_change = latest_ratio - prev_holding.holding_ratio
        
        issuer_data.append({
            "issuer": issuer,
            "latest_filing_date": latest_date,
            "filing_count": filing_count,
            "latest_ratio": latest_ratio,
            "ratio_change": ratio_change
        })
    
    return issuer_data


def get_issuer_by_id(db: Session, issuer_id: int) -> Optional[Issuer]:
    """IDで発行体を取得"""
    return db.query(Issuer).filter(Issuer.id == issuer_id).first()


def get_filings_by_issuer_and_filer(db: Session, issuer_id: int, filer_id: int) -> List[Filing]:
    """特定の発行体・提出者の報告書履歴を取得"""
    return (
        db.query(Filing)
        .filter(Filing.issuer_id == issuer_id)
        .filter(Filing.filer_id == filer_id)
        .order_by(desc(Filing.submit_date))
        .all()
    )


def get_filings_by_filer(db: Session, filer_id: int, limit: int = 100) -> List[Filing]:
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
        "latest_filing_date": latest_filing.submit_date if latest_filing else None
    }
