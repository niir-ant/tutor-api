"""
Database configuration and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator

from src.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=settings.DEBUG,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """
    Initialize database (create tables if needed)
    Note: In production, use Alembic migrations instead
    """
    # Base.metadata.create_all(bind=engine)
    pass


@event.listens_for(engine.sync_engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    """
    Set PostgreSQL session variables for RLS
    This should be set by the application based on current user/tenant
    """
    # Example: Set tenant_id and user_id for RLS
    # dbapi_conn.cursor().execute("SET app.current_tenant_id = %s", (tenant_id,))
    # dbapi_conn.cursor().execute("SET app.current_user_id = %s", (user_id,))
    # dbapi_conn.cursor().execute("SET app.current_user_role = %s", (role,))
    pass

