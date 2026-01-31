from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Filer(Base):
    """大量保有報告書の提出者（光通信など）- 集約ルート"""

    __tablename__ = "filers"

    id = Column(Integer, primary_key=True, index=True)
    edinet_code = Column(
        String, nullable=False, index=True
    )  # 代表的なEDINETコード（DBスキーマ互換）
    name = Column(String, nullable=False)  # 株式会社光通信
    sec_code = Column(String, nullable=True)  # 94350（代表的な証券コード）
    jcn = Column(String, nullable=True)  # 法人番号
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    filer_codes = relationship("FilerCode", back_populates="filer", cascade="all, delete-orphan")
    filings = relationship("Filing", back_populates="filer")

    @property
    def primary_edinet_code(self):
        """代表的なEDINETコードを返す"""
        if self.filer_codes:
            return self.filer_codes[0].edinet_code
        return None

    @property
    def edinet_codes(self):
        """すべてのEDINETコードをリストで返す"""
        return [fc.edinet_code for fc in self.filer_codes]


class FilerCode(Base):
    """Filerが持つEDINETコード（1つのFilerが複数のコードを持てる）"""

    __tablename__ = "filer_codes"

    id = Column(Integer, primary_key=True, index=True)
    filer_id = Column(Integer, ForeignKey("filers.id"), nullable=False)
    edinet_code = Column(String, unique=True, nullable=False, index=True)  # E04948
    name = Column(String, nullable=True)  # このコードでの提出者名（異なる場合）
    created_at = Column(DateTime, default=datetime.utcnow)

    filer = relationship("Filer", back_populates="filer_codes")


class Issuer(Base):
    """報告書の対象となる発行体（保有されている企業）"""

    __tablename__ = "issuers"

    id = Column(Integer, primary_key=True, index=True)
    edinet_code = Column(String, unique=True, nullable=False, index=True)  # 発行体のEDINETコード
    name = Column(String, nullable=True)  # 発行体名（銘柄名）
    sec_code = Column(String, nullable=True)  # 証券コード
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    filings = relationship("Filing", back_populates="issuer")


class Filing(Base):
    """個々の大量保有報告書"""

    __tablename__ = "filings"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, nullable=False, index=True)  # S100XBWO
    filer_id = Column(Integer, ForeignKey("filers.id"), nullable=False)
    issuer_id = Column(Integer, ForeignKey("issuers.id"), nullable=True)
    doc_type = Column(String, nullable=True)  # 大量保有報告書/変更報告書
    doc_description = Column(String, nullable=True)  # 詳細な説明
    submit_date = Column(DateTime, nullable=True)
    parent_doc_id = Column(String, nullable=True)  # 変更元の報告書ID
    csv_flag = Column(Boolean, default=False)
    xbrl_flag = Column(Boolean, default=False)
    pdf_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    filer = relationship("Filer", back_populates="filings")
    issuer = relationship("Issuer", back_populates="filings")
    holding_details = relationship("HoldingDetail", back_populates="filing")


class HoldingDetail(Base):
    """報告書から抽出した保有詳細データ"""

    __tablename__ = "holding_details"

    id = Column(Integer, primary_key=True, index=True)
    filing_id = Column(Integer, ForeignKey("filings.id"), nullable=False)
    shares_held = Column(Integer, nullable=True)  # 保有株数
    holding_ratio = Column(Float, nullable=True)  # 保有比率（%）
    purpose = Column(String, nullable=True)  # 保有目的
    created_at = Column(DateTime, default=datetime.utcnow)

    filing = relationship("Filing", back_populates="holding_details")


import os


# データベース接続用のエンジン作成関数
def get_engine(db_path: str = "data/edinet.db"):
    # ディレクトリが存在しない場合は作成
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path: str = "data/edinet.db"):
    """データベースとテーブルを初期化"""
    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
    return engine
