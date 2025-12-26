"""
Main API router
"""
from fastapi import APIRouter

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

