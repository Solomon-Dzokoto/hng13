import os
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Country, Meta


COUNTRIES_URL = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
EXCHANGE_URL = "https://open.er-api.com/v6/latest/USD"


class ExternalAPIError(Exception):
    def __init__(self, source: str, message: str):
        self.source = source
        self.message = message
        super().__init__(message)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _ensure_cache_dir() -> str:
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _load_font(size: int) -> Optional[ImageFont.FreeTypeFont]:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return None


def _format_number(n: Optional[float]) -> str:
    if n is None:
        return "-"
    try:
        return f"{n:,.2f}"
    except Exception:
        return str(n)


async def fetch_external_data(
    timeout_seconds: int = 20,
) -> Tuple[List[dict], Dict[str, float]]:
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            countries_task = client.get(COUNTRIES_URL)
            exchange_task = client.get(EXCHANGE_URL)
            countries_resp, exchange_resp = await asyncio.gather(
                countries_task, exchange_task
            )
    except Exception as exc:
        raise ExternalAPIError("network", f"{exc}")

    if countries_resp.status_code != 200:
        raise ExternalAPIError("RestCountries", f"HTTP {countries_resp.status_code}")
    if exchange_resp.status_code != 200:
        raise ExternalAPIError("OpenERAPI", f"HTTP {exchange_resp.status_code}")

    try:
        countries_json = countries_resp.json()
    except Exception as exc:
        raise ExternalAPIError("RestCountries", f"Invalid JSON: {exc}")

    try:
        exchange_json = exchange_resp.json()
        rates = exchange_json.get("rates", {})
        rates_map = {k.upper(): float(v) for k, v in rates.items()}
    except Exception as exc:
        raise ExternalAPIError("OpenERAPI", f"Invalid JSON: {exc}")

    return countries_json, rates_map


def _compute_estimated_gdp(
    population: Optional[int], exchange_rate: Optional[float]
) -> Optional[float]:
    if population is None:
        return None
    if exchange_rate is None:
        return None
    multiplier = random.randint(1000, 2000)
    try:
        return float(population) * float(multiplier) / float(exchange_rate)
    except Exception:
        return None


def upsert_countries(
    db: Session,
    countries_json: List[dict],
    rates_map: Dict[str, float],
) -> Tuple[int, int, int]:
    now = _now_utc()
    inserted = 0
    updated = 0
    total = 0

    for item in countries_json:
        name = item.get("name")
        population = item.get("population")
        if not name or population is None:
            continue  # skip invalid

        name_ci = name.lower()
        capital = item.get("capital")
        region = item.get("region")
        flag_url = item.get("flag")

        currency_code: Optional[str] = None
        exchange_rate: Optional[float] = None
        estimated_gdp: Optional[float] = None

        currencies = item.get("currencies") or []
        if len(currencies) == 0:
            currency_code = None
            exchange_rate = None
            try:
                estimated_gdp = 0.0
            except Exception:
                estimated_gdp = 0.0
        else:
            first = currencies[0] or {}
            code = first.get("code")
            currency_code = code.upper() if isinstance(code, str) else None
            if currency_code and currency_code in rates_map:
                exchange_rate = rates_map.get(currency_code)
                estimated_gdp = _compute_estimated_gdp(population, exchange_rate)
            else:
                exchange_rate = None
                estimated_gdp = None

        stmt = select(Country).where(Country.name_ci == name_ci)
        existing = db.execute(stmt).scalar_one_or_none()
        if existing is None:
            country = Country(
                name=name,
                name_ci=name_ci,
                capital=capital,
                region=region,
                population=int(population),
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                estimated_gdp=estimated_gdp,
                flag_url=flag_url,
                last_refreshed_at=now,
            )
            db.add(country)
            inserted += 1
        else:
            existing.name = name
            existing.capital = capital
            existing.region = region
            existing.population = int(population)
            existing.currency_code = currency_code
            existing.exchange_rate = exchange_rate
            existing.estimated_gdp = estimated_gdp
            existing.flag_url = flag_url
            existing.last_refreshed_at = now
            updated += 1

        total += 1

    meta = db.get(Meta, "last_refreshed_at")
    if meta is None:
        meta = Meta(key="last_refreshed_at", value=now.isoformat())
        db.add(meta)
    else:
        meta.value = now.isoformat()

    return inserted, updated, total


def generate_summary_image(db: Session) -> str:
    cache_dir = _ensure_cache_dir()
    output_path = os.path.join(cache_dir, "summary.png")

    total_countries = db.query(Country).count()
    top5 = (
        db.query(Country)
        .filter(Country.estimated_gdp.isnot(None))
        .order_by(Country.estimated_gdp.desc())
        .limit(5)
        .all()
    )

    meta = db.get(Meta, "last_refreshed_at")
    ts = meta.value if meta and meta.value else _now_utc().isoformat()

    img = Image.new("RGB", (900, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    title_font = _load_font(36)
    text_font = _load_font(22)

    y = 20
    draw.text((20, y), "Countries Summary", fill=(0, 0, 0), font=title_font)
    y += 60

    draw.text(
        (20, y), f"Total countries: {total_countries}", fill=(0, 0, 0), font=text_font
    )
    y += 40

    draw.text((20, y), "Top 5 by estimated GDP:", fill=(0, 0, 0), font=text_font)
    y += 36

    rank = 1
    for c in top5:
        line = f"{rank}. {c.name} — { _format_number(c.estimated_gdp) }"
        draw.text((40, y), line, fill=(0, 0, 0), font=text_font)
        y += 32
        rank += 1

    y += 20
    draw.text((20, y), f"Last refresh: {ts}", fill=(0, 0, 0), font=text_font)

    img.save(output_path)
    return output_path


async def refresh_all(
    db: Session, timeout_seconds: int = 20
) -> Tuple[int, int, int, datetime]:
    countries_json, rates_map = await fetch_external_data(
        timeout_seconds=timeout_seconds
    )

    with db.begin():
        inserted, updated, total = upsert_countries(db, countries_json, rates_map)

    try:
        generate_summary_image(db)
    except Exception:
        pass

    meta = db.get(Meta, "last_refreshed_at")
    last_ts = datetime.fromisoformat(meta.value) if meta and meta.value else _now_utc()

    return inserted, updated, total, last_ts
