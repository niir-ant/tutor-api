"""
Questions endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.question import (
    GenerateQuestionRequest,
    QuestionResponse,
    QuestionNarrativeResponse,
)
from src.services.question import QuestionService

router = APIRouter()


@router.post("/generate", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def generate_question(
    request: GenerateQuestionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a question using AI"""
    question_service = QuestionService(db)
    
    result = question_service.generate_question(
        tenant_id=UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None,
        subject_id=request.subject_id,
        subject_code=request.subject_code,
        grade_level=request.grade_level,
        difficulty=request.difficulty,
        topic=request.topic,
        question_type=request.question_type,
        session_id=request.session_id,
    )
    
    return QuestionResponse(**result)


@router.get("/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
async def get_question(
    question_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get question by ID"""
    question_service = QuestionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    result = question_service.get_question(question_id, tenant_id)
    
    return QuestionResponse(**result)


@router.get("/{question_id}/narrative", response_model=QuestionNarrativeResponse, status_code=status.HTTP_200_OK)
async def get_question_narrative(
    question_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get educational narrative for a question"""
    question_service = QuestionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    result = question_service.get_question_narrative(question_id, tenant_id)
    
    return QuestionNarrativeResponse(**result)

