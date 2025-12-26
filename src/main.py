"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

# #region agent log
log_path = "/Users/pavnitbhatia/atduty/github/code/tutor-api/.cursor/debug.log"
def _log(hypothesis_id, location, message, data):
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(__import__("time").time() * 1000)}) + "\n")
    except: pass
_log("D", "main.py:import", "Main module importing", {})
# #endregion

try:
    from src.core.config import settings
    # #region agent log
    _log("D", "main.py:import", "Settings imported successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "main.py:import", "Settings import failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

try:
    from src.api.v1.router import api_router
    # #region agent log
    _log("D", "main.py:import", "API router imported successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "main.py:import", "API router import failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

try:
    from src.core.database import init_db
    # #region agent log
    _log("D", "main.py:import", "Database module imported successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "main.py:import", "Database module import failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    # #region agent log
    _log("D", "main.py:lifespan", "Lifespan startup", {})
    # #endregion
    await init_db()
    # #region agent log
    _log("D", "main.py:lifespan", "Database initialized", {})
    # #endregion
    yield
    # Shutdown
    # #region agent log
    _log("D", "main.py:lifespan", "Lifespan shutdown", {})
    # #endregion
    pass

# #region agent log
_log("D", "main.py:app_creation", "About to create FastAPI app", {})
# #endregion
try:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    # #region agent log
    _log("D", "main.py:app_creation", "FastAPI app created successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "main.py:app_creation", "FastAPI app creation failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

# CORS middleware
# #region agent log
_log("D", "main.py:middleware", "About to add CORS middleware", {"cors_origins": bool(settings.CORS_ORIGINS)})
# #endregion
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # #region agent log
    _log("D", "main.py:middleware", "CORS middleware added", {})
    # #endregion

# Include API router
# #region agent log
_log("D", "main.py:router", "About to include API router", {"prefix": settings.API_V1_PREFIX})
# #endregion
try:
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    # #region agent log
    _log("D", "main.py:router", "API router included successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "main.py:router", "API router inclusion failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

