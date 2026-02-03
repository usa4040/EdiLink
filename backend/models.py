"""
SQLAlchemy 2.0スタイルのデータベースモデル
非同期PostgreSQL対応
"""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 2.0のDeclarativeBase"""

    pass


class Filer(Base):
    """大量保有報告書の提出者（光通信など）- 集約ルート"""

    __tablename__ = "filers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edinet_code: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )  # 代表的なEDINETコード（DBスキーマ互換）
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 株式会社光通信
    sec_code: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 94350
    jcn: Mapped[str | None] = mapped_column(String(13), nullable=True)  # 法人番号
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # リレーション
    filer_codes: Mapped[list["FilerCode"]] = relationship(
        back_populates="filer", cascade="all, delete-orphan"
    )
    filings: Mapped[list["Filing"]] = relationship(back_populates="filer")

    @property
    def primary_edinet_code(self) -> str | None:
        """代表的なEDINETコードを返す"""
        if self.filer_codes:
            return self.filer_codes[0].edinet_code
        return None

    @property
    def edinet_codes(self) -> list[str]:
        """すべてのEDINETコードをリストで返す"""
        return [fc.edinet_code for fc in self.filer_codes]


class FilerCode(Base):
    """Filerが持つEDINETコード（1つのFilerが複数のコードを持てる）"""

    __tablename__ = "filer_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filer_id: Mapped[int] = mapped_column(ForeignKey("filers.id"), nullable=False)
    edinet_code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )  # E04948
    name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # このコードでの提出者名（異なる場合）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    filer: Mapped["Filer"] = relationship(back_populates="filer_codes")


class Issuer(Base):
    """報告書の対象となる発行体（保有されている企業）"""

    __tablename__ = "issuers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edinet_code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )  # 発行体のEDINETコード
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 発行体名（銘柄名）
    sec_code: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 証券コード
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    filings: Mapped[list["Filing"]] = relationship(back_populates="issuer")


class Filing(Base):
    """個々の大量保有報告書"""

    __tablename__ = "filings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doc_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # S100XBWO
    filer_id: Mapped[int] = mapped_column(ForeignKey("filers.id"), nullable=False)
    issuer_id: Mapped[int | None] = mapped_column(ForeignKey("issuers.id"), nullable=True)
    doc_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 大量保有報告書/変更報告書
    doc_description: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 詳細な説明
    submit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    parent_doc_id: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 変更元の報告書ID
    csv_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    xbrl_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    pdf_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    filer: Mapped["Filer"] = relationship(back_populates="filings")
    issuer: Mapped[Optional["Issuer"]] = relationship(back_populates="filings")
    holding_details: Mapped[list["HoldingDetail"]] = relationship(back_populates="filing")


class HoldingDetail(Base):
    """報告書から抽出した保有詳細データ"""

    __tablename__ = "holding_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filing_id: Mapped[int] = mapped_column(ForeignKey("filings.id"), nullable=False)
    shares_held: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 保有株数
    holding_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)  # 保有比率（%）
    purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 保有目的
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    filing: Mapped["Filing"] = relationship(back_populates="holding_details")
