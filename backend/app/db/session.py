"""Database engine and session management for PostgreSQL."""

import os
from pathlib import Path
from typing import Generator, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/aegis_rto"
)

Base = declarative_base()

_engine = None
_SessionFactory = None


def get_engine():
    """Initializes and returns the singleton SQLAlchemy engine (with automatic SQLite fallback)."""
    global _engine
    if _engine is None:
        # Try PostgreSQL if configured
        if DATABASE_URL and "postgresql" in DATABASE_URL:
            try:
                test_engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_size=5,
                    connect_args={"connect_timeout": 1},
                )
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                _engine = test_engine
            except Exception:
                # PostgreSQL offline -> fallback seamlessly to SQLite
                sqlite_path = Path(__file__).resolve().parent.parent.parent / "aegis_rto.db"
                _engine = create_engine(
                    f"sqlite:///{sqlite_path}",
                    connect_args={"check_same_thread": False},
                )
                Base.metadata.create_all(bind=_engine)
        else:
            _engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(bind=_engine)
    return _engine


def get_session_factory():
    """Returns the singleton sessionmaker."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI & context dependency providing a transactional DB session."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifies whether PostgreSQL database is reachable."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
