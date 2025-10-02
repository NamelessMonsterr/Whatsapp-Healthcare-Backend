# app/core/database.py
from __future__ import annotations

import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional, Union   # <-- Dict removed, dict is built-in

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# SQLite FK enforcement
# ------------------------------------------------------------------
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ------------------------------------------------------------------
# Engine & sessionmaker
# ------------------------------------------------------------------
engine: Engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=False,
)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------------
# FastAPI dependency
# ------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------------
# Initialise tables once
# ------------------------------------------------------------------
def init_db() -> None:
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created / verified")

# ------------------------------------------------------------------
# Helper context-manager (used by scripts)
# ------------------------------------------------------------------
@contextmanager
def db_session() -> Generator[Session, None, None]:
    db = LocalSession()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------
def get_db_health(db: Session) -> dict[str, Any]:          # <-- dict instead of Dict
    """Return DB health metrics."""
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency = round((time.time() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency}
    except Exception as exc:
        logger.error("DB health-check failed: %s", exc)
        return {"status": "unhealthy", "error": str(exc)}
