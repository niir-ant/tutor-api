"""
Database configuration and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import json

from src.core.config import settings

# #region agent log
log_path = "/Users/pavnitbhatia/atduty/github/code/tutor-api/.cursor/debug.log"
def _log(hypothesis_id, location, message, data):
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(__import__("time").time() * 1000)}) + "\n")
    except: pass
_log("D", "database.py:import", "Database module importing", {"database_url_exists": bool(settings.DATABASE_URL), "database_url_preview": settings.DATABASE_URL[:50] + "..." if settings.DATABASE_URL and len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL})
# #endregion

# Create engine
try:
    # #region agent log
    _log("D", "database.py:create_engine", "About to create engine", {"database_url": settings.DATABASE_URL[:50] + "..." if settings.DATABASE_URL and len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL})
    # #endregion
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DEBUG,
    )
    # #region agent log
    _log("D", "database.py:create_engine", "Engine created successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "database.py:create_engine", "Engine creation failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
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


# #region agent log
_log("D", "database.py:before_event_listener", "About to register event listener", {"engine_type": type(engine).__name__})
# #endregion
@event.listens_for(engine, "connect")
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
# #region agent log
_log("D", "database.py:after_event_listener", "Event listener registered successfully", {})
# #endregion

