import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from secure import Secure
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend import crud, schemas
from backend.cache import init_cache
from backend.database import get_db

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_cache()
    yield


app = FastAPI(
    title="EDINET 大量保有報告書 API",
    description="大量保有報告書を閲覧・検索するためのAPI",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET"],  # Only GET for read-only API
    allow_headers=["Authorization", "Content-Type"],
)

secure_headers = Secure()


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response


# === グローバルエラーハンドラ ===


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """予期せぬ例外のハンドラ"""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "予期せぬエラーが発生しました。管理者に連絡してください。",
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """データベースエラーのハンドラ"""
    logger.error(
        f"Database error: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database error",
            "message": "データベース操作中にエラーが発生しました。",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーのハンドラ"""
    logger.warning(
        f"Validation error: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "message": "リクエストパラメータが不正です。",
            "details": exc.errors(),
        },
    )


@app.get("/")
async def root():
    return {"message": "EDINET 大量保有報告書 API", "version": "1.0.0"}


# === Filers (提出者) ===


@app.get("/api/filers")
@limiter.limit("100/minute")
@cache(expire=300)
async def get_filers(
    request: Request,
    skip: int = Query(0, ge=0, le=10000, description="スキップ数"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    search: str | None = Query(None, max_length=100, description="検索キーワード"),
    db: AsyncSession = Depends(get_db),
):
    """提出者一覧を取得（ページネーション対応）"""
    data = crud.get_filers(db, skip=skip, limit=limit, search=search)

    result = []
    for item in data["items"]:
        filer = item["filer"]
        result.append(
            schemas.FilerResponse(
                id=filer.id,
                edinet_code=filer.primary_edinet_code,
                name=filer.name,
                sec_code=filer.sec_code,
                created_at=filer.created_at,
                filing_count=item["filing_count"],
                issuer_count=item["issuer_count"],
                latest_filing_date=item["latest_filing_date"],
            )
        )

    return {"items": result, "total": data["total"], "skip": data["skip"], "limit": data["limit"]}


@app.get("/api/filers/{filer_id}", response_model=schemas.FilerResponse)
@limiter.limit("100/minute")
@cache(expire=600)
async def get_filer(request: Request, filer_id: int, db: AsyncSession = Depends(get_db)):
    """提出者詳細を取得"""
    filer = crud.get_filer_by_id(db, filer_id)
    if not filer:
        raise HTTPException(status_code=404, detail="Filer not found")

    stats = crud.get_filer_stats(db, filer.id)
    return schemas.FilerResponse(
        id=filer.id,
        edinet_code=filer.primary_edinet_code,
        name=filer.name,
        sec_code=filer.sec_code,
        created_at=filer.created_at,
        filing_count=stats["filing_count"],
        issuer_count=stats["issuer_count"],
        latest_filing_date=stats["latest_filing_date"],
    )


@app.post("/api/filers", response_model=schemas.FilerResponse)
@limiter.limit("10/minute")
async def create_filer(
    request: Request, filer: schemas.FilerCreate, db: AsyncSession = Depends(get_db)
):
    """新しい提出者を追加"""
    existing = crud.get_filer_by_edinet_code(db, filer.edinet_code)
    if existing:
        raise HTTPException(status_code=400, detail="Filer already exists")

    new_filer = crud.create_filer(db, filer.edinet_code, filer.name, filer.sec_code)
    return schemas.FilerResponse(
        id=new_filer.id,
        edinet_code=new_filer.primary_edinet_code,
        name=new_filer.name,
        sec_code=new_filer.sec_code,
        created_at=new_filer.created_at,
        filing_count=0,
        issuer_count=0,
        latest_filing_date=None,
    )


# === Issuers (発行体/銘柄) ===


@app.get("/api/filers/{filer_id}/issuers")
@limiter.limit("30/minute")
@cache(expire=300)
async def get_issuers_by_filer(
    request: Request,
    filer_id: int,
    skip: int = Query(0, ge=0, le=10000, description="スキップ数"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    search: str | None = Query(None, max_length=100, description="検索キーワード"),
    db: AsyncSession = Depends(get_db),
):
    """提出者が保有している銘柄一覧を取得（ページネーション対応）"""
    filer = crud.get_filer_by_id(db, filer_id)
    if not filer:
        raise HTTPException(status_code=404, detail="Filer not found")

    data = crud.get_issuers_by_filer(db, filer_id, skip=skip, limit=limit, search=search)

    result = []
    for item in data["items"]:
        issuer = item["issuer"]
        result.append(
            schemas.IssuerResponse(
                id=issuer.id,
                edinet_code=issuer.edinet_code,
                name=issuer.name or issuer.edinet_code,
                sec_code=issuer.sec_code,
                latest_filing_date=item["latest_filing_date"],
                latest_ratio=item.get("latest_ratio"),
                ratio_change=item.get("ratio_change"),
                filing_count=item["filing_count"],
            )
        )

    return {"items": result, "total": data["total"], "skip": data["skip"], "limit": data["limit"]}


@app.get("/api/issuers")
@limiter.limit("100/minute")
@cache(expire=300)
async def get_issuers(
    request: Request,
    skip: int = Query(0, ge=0, le=10000, description="スキップ数"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    search: str | None = Query(None, max_length=100, description="検索キーワード"),
    db: AsyncSession = Depends(get_db),
):
    """銘柄一覧を取得（ページネーション・検索対応）"""
    data = crud.get_issuers(db, skip=skip, limit=limit, search=search)

    result = []
    for issuer in data["items"]:
        result.append(
            schemas.IssuerResponse(
                id=issuer.id,
                edinet_code=issuer.edinet_code,
                name=issuer.name or issuer.edinet_code,
                sec_code=issuer.sec_code,
                # latest_filing_date等は一覧取得時は重くなるため含めない、もしくはNone
            )
        )

    return {"items": result, "total": data["total"], "skip": data["skip"], "limit": data["limit"]}


@app.get("/api/issuers/{issuer_id}", response_model=schemas.IssuerResponse)
@limiter.limit("100/minute")
@cache(expire=600)
async def get_issuer(request: Request, issuer_id: int, db: AsyncSession = Depends(get_db)):
    """銘柄詳細（基本情報）を取得"""
    issuer = crud.get_issuer_by_id(db, issuer_id)
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")
    # 詳細情報（latest_filing_dateなど）は今回は省略、必要ならget_filings等から取得
    return schemas.IssuerResponse(
        id=issuer.id,
        edinet_code=issuer.edinet_code,
        name=issuer.name or issuer.edinet_code,
        sec_code=issuer.sec_code,
    )


@app.get("/api/issuers/{issuer_id}/ownerships", response_model=schemas.IssuerOwnershipResponse)
@limiter.limit("50/minute")
@cache(expire=900)
async def get_issuer_ownerships(
    request: Request, issuer_id: int, db: AsyncSession = Depends(get_db)
):
    """銘柄を保有している投資家一覧を取得"""
    issuer = crud.get_issuer_by_id(db, issuer_id)
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")

    ownerships = crud.get_issuer_ownerships(db, issuer_id)

    return {
        "issuer": schemas.IssuerResponse(
            id=issuer.id,
            edinet_code=issuer.edinet_code,
            name=issuer.name or issuer.edinet_code,
            sec_code=issuer.sec_code,
        ),
        "ownerships": ownerships,
    }


# === Filings (報告書) ===


@app.get("/api/filers/{filer_id}/filings", response_model=list[schemas.FilingResponse])
@limiter.limit("50/minute")
@cache(expire=900)
async def get_filings_by_filer(
    request: Request, filer_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """提出者の報告書一覧を取得"""
    filer = crud.get_filer_by_id(db, filer_id)
    if not filer:
        raise HTTPException(status_code=404, detail="Filer not found")

    filings = crud.get_filings_by_filer(db, filer_id, limit)
    result = []
    for filing in filings:
        result.append(
            schemas.FilingResponse(
                id=filing.id,
                doc_id=filing.doc_id,
                filer_id=filing.filer_id,
                issuer_id=filing.issuer_id,
                doc_description=filing.doc_description,
                submit_date=filing.submit_date,
                parent_doc_id=filing.parent_doc_id,
                csv_flag=filing.csv_flag,
                xbrl_flag=filing.xbrl_flag,
                pdf_flag=filing.pdf_flag,
                issuer_name=filing.issuer.name if filing.issuer else None,
                issuer_edinet_code=filing.issuer.edinet_code if filing.issuer else None,
            )
        )
    return result


@app.get("/api/filers/{filer_id}/issuers/{issuer_id}/history")
@limiter.limit("50/minute")
@cache(expire=900)
async def get_issuer_history(
    request: Request, filer_id: int, issuer_id: int, db: AsyncSession = Depends(get_db)
):
    """銘柄の報告書履歴を取得"""
    from backend.models import HoldingDetail

    filer = crud.get_filer_by_id(db, filer_id)
    issuer = crud.get_issuer_by_id(db, issuer_id)

    if not filer:
        raise HTTPException(status_code=404, detail="Filer not found")
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")

    filings = crud.get_filings_by_issuer_and_filer(db, issuer_id, filer_id)

    # N+1問題解消: 全HoldingDetailを一括取得
    filing_ids = [f.id for f in filings]
    holdings = db.query(HoldingDetail).filter(HoldingDetail.filing_id.in_(filing_ids)).all()
    holding_map = {h.filing_id: h for h in holdings}

    history = []
    prev_ratio = None

    # 古い順に処理して差分を計算
    for filing in reversed(filings):
        # マップからHoldingDetailを取得（クエリ発行なし）
        holding = holding_map.get(filing.id)

        shares_held = holding.shares_held if holding else None
        holding_ratio = holding.holding_ratio if holding else None

        # 前回との差分を計算
        ratio_change = None
        if holding_ratio is not None and prev_ratio is not None:
            ratio_change = round(holding_ratio - prev_ratio, 2)

        history.append(
            {
                "doc_id": filing.doc_id,
                "submit_date": filing.submit_date,
                "doc_description": filing.doc_description,
                "shares_held": shares_held,
                "holding_ratio": holding_ratio,
                "ratio_change": ratio_change,
            }
        )

        if holding_ratio is not None:
            prev_ratio = holding_ratio

    # 新しい順に戻す
    history.reverse()

    return {
        "issuer": {
            "id": issuer.id,
            "edinet_code": issuer.edinet_code,
            "name": issuer.name or issuer.edinet_code,
            "sec_code": issuer.sec_code,
        },
        "filer": {"id": filer.id, "edinet_code": filer.primary_edinet_code, "name": filer.name},
        "history": history,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
