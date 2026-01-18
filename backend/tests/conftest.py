import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models import Base, Filer, FilerCode, Issuer, Filing, HoldingDetail
from backend.database import get_db
from backend.main import app

from sqlalchemy.pool import StaticPool

# テスト用のインメモリデータベース
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """テストごとにクリーンなDBセッションを提供"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """FastAPIのテストクライアントを提供。DBの依存性をオーバーライド"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def sample_data(db):
    """基本的なサンプルデータを作成"""
    filer = Filer(edinet_code="E00000", name="テスト提出者", sec_code="90000")
    db.add(filer)
    db.flush()
    
    filer_code = FilerCode(filer_id=filer.id, edinet_code="E00000", name="テスト提出者")
    db.add(filer_code)
    
    issuer = Issuer(edinet_code="E11111", name="テスト発行体", sec_code="10010")
    db.add(issuer)
    db.flush()
    
    filing = Filing(
        doc_id="S_TEST_01",
        filer_id=filer.id,
        issuer_id=issuer.id,
        doc_description="大量保有報告書",
        submit_date=datetime.now(),
        csv_flag=True
    )
    db.add(filing)
    db.flush()
    
    holding = HoldingDetail(
        filing_id=filing.id,
        shares_held=1000000,
        holding_ratio=5.50
    )
    db.add(holding)
    db.commit()
    
    return {
        "filer": filer,
        "filer_code": filer_code,
        "issuer": issuer,
        "filing": filing,
        "holding": holding
    }
