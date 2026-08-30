"""Database engine and session management for PostgreSQL with resilient SQLite fallback."""

import os
import socket
from urllib.parse import urlparse
from pathlib import Path
from typing import Generator, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

Base = declarative_base()

_engine = None
_SessionFactory = None


def _is_pg_socket_open(url: str, timeout: float = 0.2) -> bool:
    """Fast non-blocking probe to determine if PostgreSQL port is actively listening."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        port = parsed.port or 5432
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def _resolve_sqlite_path() -> Path:
    """Finds the local SQLite database file path."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    return backend_dir / "aegis_rto.db"


def get_engine():
    """Initializes and returns the singleton SQLAlchemy engine (with automatic SQLite fallback)."""
    global _engine
    if _engine is None:
        # Try PostgreSQL if configured and socket reachable
        if DATABASE_URL and "postgresql" in DATABASE_URL:
            if _is_pg_socket_open(DATABASE_URL, timeout=0.8):
                try:
                    test_engine = create_engine(
                        DATABASE_URL,
                        pool_pre_ping=True,
                        pool_size=5,
                        connect_args={"connect_timeout": 2},
                    )
                    with test_engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    _engine = test_engine
                except Exception:
                    _engine = None

        if _engine is None:
            # PostgreSQL offline or not configured -> fallback seamlessly to SQLite
            sqlite_path = _resolve_sqlite_path()
            _engine = create_engine(
                f"sqlite:///{sqlite_path}",
                connect_args={"check_same_thread": False},
            )
            try:
                Base.metadata.create_all(bind=_engine)
            except Exception:
                pass
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
    """Verifies whether active database is reachable."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

