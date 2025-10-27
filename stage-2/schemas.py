from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CountryOut(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: Optional[datetime] = None


class StatusOut(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime] = None


class RefreshResponse(BaseModel):
    message: str = Field(default="Refresh complete")
    total_countries: int
    last_refreshed_at: datetime
