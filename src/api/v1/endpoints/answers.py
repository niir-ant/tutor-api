"""
Answers endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.answer import (
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    ValidateAnswerRequest,
    ValidateAnswerResponse,
)
from src.services.answer import AnswerService

router = APIRouter()


@router.post("/{question_id}/answer", response_model=SubmitAnswerResponse, status_code=status.HTTP_200_OK)
async def submit_answer(
    question_id: UUID,
    request: SubmitAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit answer for validation"""
    answer_service = AnswerService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    student_id = UUID(current_user["user_id"])
    
    result = answer_service.submit_answer(
        question_id=question_id,
        tenant_id=tenant_id,
        student_id=student_id,
        answer=request.answer,
        session_id=request.session_id,
        time_spent=request.time_spent,
        hints_used=request.hints_used,
    )
    
    return SubmitAnswerResponse(**result)


@router.post("/{question_id}/validate", response_model=ValidateAnswerResponse, status_code=status.HTTP_200_OK)
async def validate_answer(
    question_id: UUID,
    request: ValidateAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate answer without recording submission (practice mode)"""
    answer_service = AnswerService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = answer_service.validate_answer(
        question_id=question_id,
        tenant_id=tenant_id,
        answer=request.answer,
    )
    
    return ValidateAnswerResponse(**result)

