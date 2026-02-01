from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# === Pagination ===
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, le=10000, description="スキップ数")
    limit: int = Field(50, ge=1, le=100, description="取得件数")

    model_config = ConfigDict(json_schema_extra={"example": {"skip": 0, "limit": 50}})


# === Filer ===
class FilerBase(BaseModel):
    edinet_code: str
    name: str
    sec_code: str | None = None


class FilerCreate(FilerBase):
    pass


class FilerResponse(FilerBase):
    id: int
    created_at: datetime
    filing_count: int | None = None
    issuer_count: int | None = None
    latest_filing_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# === Issuer ===
class IssuerBase(BaseModel):
    edinet_code: str
    name: str | None = None
    sec_code: str | None = None


class IssuerResponse(IssuerBase):
    id: int
    latest_filing_date: datetime | None = None
    latest_ratio: float | None = None
    latest_purpose: str | None = None
    ratio_change: float | None = None
    filing_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


# === Filing ===
class FilingBase(BaseModel):
    doc_id: str
    doc_description: str | None = None
    submit_date: datetime | None = None


class FilingResponse(FilingBase):
    id: int
    filer_id: int
    issuer_id: int | None = None
    parent_doc_id: str | None = None
    csv_flag: bool
    xbrl_flag: bool
    pdf_flag: bool

    # リレーション
    issuer_name: str | None = None
    issuer_edinet_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


# === HoldingDetail ===
class HoldingDetailBase(BaseModel):
    shares_held: int | None = None
    holding_ratio: float | None = None
    purpose: str | None = None


class HoldingDetailResponse(HoldingDetailBase):
    id: int
    filing_id: int

    model_config = ConfigDict(from_attributes=True)


# === History (銘柄の履歴) ===
class FilingHistoryItem(BaseModel):
    doc_id: str
    submit_date: datetime | None = None
    doc_description: str | None = None
    shares_held: int | None = None
    holding_ratio: float | None = None
    ratio_change: float | None = None  # 前回との差分

    model_config = ConfigDict(from_attributes=True)


class IssuerHistoryResponse(BaseModel):
    issuer: IssuerResponse
    filer: FilerResponse
    history: list[FilingHistoryItem]


class OwnershipItem(BaseModel):
    filer_id: int
    filer_name: str
    latest_submit_date: datetime | None = None
    shares_held: int | None = None
    holding_ratio: float | None = None
    purpose: str | None = None

    model_config = ConfigDict(from_attributes=True)


class IssuerOwnershipResponse(BaseModel):
    issuer: IssuerResponse
    ownerships: list[OwnershipItem]
