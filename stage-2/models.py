from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, Index
from sqlalchemy.sql import func
from database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ci = Column(String(255), nullable=False, unique=True, index=True)
    capital = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(16), nullable=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(512), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=False), nullable=True)


Index("ix_countries_name_ci", Country.name_ci, unique=True)


class Meta(Base):
    __tablename__ = "meta"

    key = Column(String(128), primary_key=True)
    value = Column(String(1024), nullable=True)
    updated_at = Column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )
