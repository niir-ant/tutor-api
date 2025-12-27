"""
Subjects endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user, require_system_admin, require_tenant_admin
from src.schemas.subject import (
    SubjectListResponse,
    SubjectDetailResponse,
    CreateSubjectRequest,
    UpdateSubjectRequest,
    SubjectStatisticsResponse,
)
from src.services.subject import SubjectService

router = APIRouter()


@router.get("", response_model=SubjectListResponse, status_code=status.HTTP_200_OK)
async def list_subjects(
    status_filter: Optional[str] = Query(None, alias="status"),
    grade_level: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List subjects"""
    subject_service = SubjectService(db)
    
    result = subject_service.list_subjects(
        status=status_filter,
        grade_level=grade_level,
        type=type,
    )
    
    return SubjectListResponse(**result)


@router.get("/{subject_id}", response_model=SubjectDetailResponse, status_code=status.HTTP_200_OK)
async def get_subject(
    subject_id: UUID,
    db: Session = Depends(get_db),
):
    """Get subject details"""
    subject_service = SubjectService(db)
    result = subject_service.get_subject(subject_id)
    return SubjectDetailResponse(**result)


# Admin endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: CreateSubjectRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Create subject (admin only)"""
    subject_service = SubjectService(db)
    
    result = subject_service.create_subject(
        subject_code=request.subject_code,
        name=request.name,
        description=request.description,
        type=request.type,
        grade_levels=request.grade_levels,
        supported_question_types=request.supported_question_types,
        answer_validation_method=request.answer_validation_method,
        settings=request.settings.dict() if hasattr(request.settings, 'dict') else request.settings,
        metadata=request.metadata.dict() if hasattr(request.metadata, 'dict') else request.metadata,
    )
    
    return result


@router.put("/{subject_id}", status_code=status.HTTP_200_OK)
async def update_subject(
    subject_id: UUID,
    request: UpdateSubjectRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Update subject (admin only)"""
    subject_service = SubjectService(db)
    
    result = subject_service.update_subject(
        subject_id=subject_id,
        name=request.name,
        description=request.description,
        grade_levels=request.grade_levels,
        status=request.status,
        supported_question_types=request.supported_question_types,
        settings=request.settings.dict() if hasattr(request.settings, 'dict') else request.settings,
        metadata=request.metadata.dict() if hasattr(request.metadata, 'dict') else request.metadata,
    )
    
    return result


@router.post("/{subject_id}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_subject(
    subject_id: UUID,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Deactivate subject (admin only) - cannot deactivate default subject"""
    subject_service = SubjectService(db)
    
    # Check if it's the default subject before attempting deactivation
    from src.core.subject_utils import is_default_subject
    if is_default_subject(subject_id, db):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the default subject. It is required for system operation."
        )
    
    result = subject_service.update_subject(subject_id=subject_id, status="inactive")
    
    return {
        "subject_id": result["subject_id"],
        "status": "inactive",
        "message": "Subject deactivated. Existing data preserved.",
    }


@router.get("/{subject_id}/statistics", response_model=SubjectStatisticsResponse, status_code=status.HTTP_200_OK)
async def get_subject_statistics(
    subject_id: UUID,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get subject statistics (admin only)"""
    subject_service = SubjectService(db)
    result = subject_service.get_subject_statistics(subject_id)
    return SubjectStatisticsResponse(**result)

