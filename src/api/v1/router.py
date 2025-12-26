"""
Main API router
"""
from fastapi import APIRouter
import json

# #region agent log
log_path = "/Users/pavnitbhatia/atduty/github/code/tutor-api/.cursor/debug.log"
def _log(hypothesis_id, location, message, data):
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(__import__("time").time() * 1000)}) + "\n")
    except: pass
_log("D", "router.py:import", "Router module importing", {})
# #endregion

try:
    from src.api.v1.endpoints import (
        auth,
        questions,
        answers,
        hints,
        sessions,
        progress,
        students,
        tutors,
        messages,
        subjects,
        competitions,
        tenants,
        system_admin,
        tenant_admin,
    )
    # #region agent log
    _log("D", "router.py:import", "All endpoints imported successfully", {})
    # #endregion
except Exception as e:
    # #region agent log
    _log("D", "router.py:import", "Endpoints import failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(answers.router, prefix="/questions", tags=["Answers"])
api_router.include_router(hints.router, prefix="/questions", tags=["Hints"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(progress.router, prefix="/students", tags=["Progress"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(tutors.router, prefix="/tutors", tags=["Tutors"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["Competitions"])
api_router.include_router(tenants.router, prefix="/tenant", tags=["Tenants"])
api_router.include_router(system_admin.router, prefix="/system", tags=["System Admin"])
api_router.include_router(tenant_admin.router, prefix="/admin", tags=["Tenant Admin"])

