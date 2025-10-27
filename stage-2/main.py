import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, engine, get_db_session
from models import Country, Meta
from schemas import CountryOut, StatusOut, RefreshResponse
from services import refresh_all, ExternalAPIError

# create tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Country Currency & Exchange API", version="1.0.0")


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    # keep detail if it's already our structured error
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    message = (
        "Country not found"
        if exc.status_code == 404
        else (
            "Validation failed" if exc.status_code == 400 else "Internal server error"
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": message},
    )


@app.get("/status", response_model=StatusOut)
async def get_status(db: Session = Depends(get_db_session)):
    total = db.query(Country).count()
    meta = db.get(Meta, "last_refreshed_at")
    last_ts: Optional[datetime] = None
    if meta and meta.value:
        try:
            last_ts = datetime.fromisoformat(meta.value)
        except Exception:
            last_ts = None
    return StatusOut(total_countries=total, last_refreshed_at=last_ts)


@app.post("/countries/refresh", response_model=RefreshResponse)
async def refresh_countries(db: Session = Depends(get_db_session)):
    timeout = int(os.getenv("HTTP_TIMEOUT", "20"))
    try:
        inserted, updated, total, last_ts = await refresh_all(
            db, timeout_seconds=timeout
        )
    except ExternalAPIError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {e.source}",
            },
        )
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})

    return RefreshResponse(
        message="Refresh complete",
        total_countries=total,
        last_refreshed_at=last_ts,
    )


@app.get("/countries", response_model=List[CountryOut])
async def list_countries(
    region: Optional[str] = Query(default=None),
    currency: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(default=None, description="Supported: gdp_desc"),
    db: Session = Depends(get_db_session),
):
    q = db.query(Country)

    if region:
        q = q.filter(func.lower(Country.region) == region.lower())
    if currency:
        q = q.filter(func.upper(Country.currency_code) == currency.upper())

    if sort is None:
        q = q.order_by(Country.name.asc())
    elif sort == "gdp_desc":
        # MySQL doesn't support NULLS LAST syntax; default DESC places NULLs last
        q = q.order_by(Country.estimated_gdp.desc(), Country.name.asc())
    elif sort == "gdp_asc":
        # MySQL default ASC places NULLs first; no explicit NULLS FIRST needed
        q = q.order_by(Country.estimated_gdp.asc(), Country.name.asc())
    else:
        raise HTTPException(
            status_code=400,
            detail={"error": "Validation failed", "details": {"sort": "unsupported"}},
        )

    rows = q.all()

    return [
        CountryOut(
            id=r.id,
            name=r.name,
            capital=r.capital,
            region=r.region,
            population=r.population,
            currency_code=r.currency_code,
            exchange_rate=r.exchange_rate,
            estimated_gdp=r.estimated_gdp,
            flag_url=r.flag_url,
            last_refreshed_at=r.last_refreshed_at,
        )
        for r in rows
    ]


@app.get("/countries/{name}", response_model=CountryOut)
async def get_country(name: str, db: Session = Depends(get_db_session)):
    row = db.query(Country).filter(Country.name_ci == name.lower()).first()
    if not row:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})

    return CountryOut(
        id=row.id,
        name=row.name,
        capital=row.capital,
        region=row.region,
        population=row.population,
        currency_code=row.currency_code,
        exchange_rate=row.exchange_rate,
        estimated_gdp=row.estimated_gdp,
        flag_url=row.flag_url,
        last_refreshed_at=row.last_refreshed_at,
    )


@app.delete("/countries/{name}")
async def delete_country(name: str, db: Session = Depends(get_db_session)):
    row = db.query(Country).filter(Country.name_ci == name.lower()).first()
    if not row:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})

    db.delete(row)
    db.commit()
    return {"message": "Deleted"}


@app.get("/countries/image")
async def get_summary_image():
    path = os.path.join(os.path.dirname(__file__), "cache", "summary.png")
    if not os.path.exists(path):
        return JSONResponse(
            status_code=404, content={"error": "Summary image not found"}
        )
    return FileResponse(path, media_type="image/png")
