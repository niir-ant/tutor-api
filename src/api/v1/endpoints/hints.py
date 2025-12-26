"""
Hints endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.hint import GetHintRequest, GetHintResponse
from src.services.hint import HintService

router = APIRouter()


@router.post("/{question_id}/hint", response_model=GetHintResponse, status_code=status.HTTP_200_OK)
async def get_hint(
    question_id: UUID,
    request: GetHintRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get hint for a question"""
    hint_service = HintService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    student_id = UUID(current_user["user_id"])
    
    result = hint_service.get_hint(
        question_id=question_id,
        tenant_id=tenant_id,
        hint_level=request.hint_level,
        student_id=student_id,
        previous_attempts=request.previous_attempts,
        hints_already_shown=request.hints_already_shown,
    )
    
    return GetHintResponse(**result)

