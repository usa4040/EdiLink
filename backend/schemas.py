from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# === Filer ===
class FilerBase(BaseModel):
    edinet_code: str
    name: str
    sec_code: Optional[str] = None


class FilerCreate(FilerBase):
    pass


class FilerResponse(FilerBase):
    id: int
    created_at: datetime
    filing_count: Optional[int] = None
    issuer_count: Optional[int] = None
    latest_filing_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# === Issuer ===
class IssuerBase(BaseModel):
    edinet_code: str
    name: Optional[str] = None
    sec_code: Optional[str] = None


class IssuerResponse(IssuerBase):
    id: int
    latest_filing_date: Optional[datetime] = None
    latest_ratio: Optional[float] = None
    latest_purpose: Optional[str] = None
    ratio_change: Optional[float] = None
    filing_count: Optional[int] = None

    class Config:
        from_attributes = True


# === Filing ===
class FilingBase(BaseModel):
    doc_id: str
    doc_description: Optional[str] = None
    submit_date: Optional[datetime] = None


class FilingResponse(FilingBase):
    id: int
    filer_id: int
    issuer_id: Optional[int] = None
    parent_doc_id: Optional[str] = None
    csv_flag: bool
    xbrl_flag: bool
    pdf_flag: bool
    
    # リレーション
    issuer_name: Optional[str] = None
    issuer_edinet_code: Optional[str] = None

    class Config:
        from_attributes = True


# === HoldingDetail ===
class HoldingDetailBase(BaseModel):
    shares_held: Optional[int] = None
    holding_ratio: Optional[float] = None
    purpose: Optional[str] = None


class HoldingDetailResponse(HoldingDetailBase):
    id: int
    filing_id: int

    class Config:
        from_attributes = True


# === History (銘柄の履歴) ===
class FilingHistoryItem(BaseModel):
    doc_id: str
    submit_date: Optional[datetime] = None
    doc_description: Optional[str] = None
    shares_held: Optional[int] = None
    holding_ratio: Optional[float] = None
    ratio_change: Optional[float] = None  # 前回との差分

    class Config:
        from_attributes = True


class IssuerHistoryResponse(BaseModel):
    issuer: IssuerResponse
    filer: FilerResponse
    history: List[FilingHistoryItem]
