"""Single place that owns the SQLAlchemy engine/session.

Reads DATABASE_URL from the environment (see .env.example). If it's not
set, falls back to a local SQLite file so the MVP runs with zero setup —
swap in real Postgres for anything beyond a demo.
"""
from __future__ import annotations

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cultura.db")

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def init_db() -> None:
    """Create all tables. Safe to call repeatedly (no-op on existing tables)."""
    # Import models so they register on Base.metadata before create_all.
    from database import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
