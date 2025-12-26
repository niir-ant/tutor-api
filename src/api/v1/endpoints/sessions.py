"""
Sessions endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionStatusResponse,
    SessionResultsResponse,
)
from src.services.session import SessionService

router = APIRouter()


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new quiz session"""
    session_service = SessionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    student_id = UUID(current_user["user_id"])
    
    result = session_service.create_session(
        tenant_id=tenant_id,
        student_id=student_id,
        subject_id=request.subject_id,
        subject_code=request.subject_code,
        grade_level=request.grade_level,
        difficulty=request.difficulty,
        num_questions=request.num_questions,
        topics=request.topics,
        time_limit=request.time_limit,
    )
    
    return CreateSessionResponse(**result)


@router.get("/{session_id}", response_model=SessionStatusResponse, status_code=status.HTTP_200_OK)
async def get_session_status(
    session_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get session status"""
    session_service = SessionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = session_service.get_session_status(session_id, tenant_id)
    
    return SessionStatusResponse(**result)


@router.get("/{session_id}/results", response_model=SessionResultsResponse, status_code=status.HTTP_200_OK)
async def get_session_results(
    session_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get session results"""
    session_service = SessionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = session_service.get_session_results(session_id, tenant_id)
    
    return SessionResultsResponse(**result)

