import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

def _build_mysql_url_from_env() -> str | None:
    """Compose a SQLAlchemy MySQL URL from MYSQL_* env vars if available."""
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db = os.getenv("MYSQL_DB")
    port = os.getenv("MYSQL_PORT", "3306")
    if all([host, user, password, db]):
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return None


# Prefer explicit DATABASE_URL; otherwise, build from MYSQL_*; otherwise fall back to SQLite
DATABASE_URL = os.getenv("DATABASE_URL") or _build_mysql_url_from_env() or (
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'app.db')}"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
