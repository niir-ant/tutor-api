"""
Progress endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.progress import StudentProgressResponse, PerformanceAnalyticsResponse
from src.services.progress import ProgressService

router = APIRouter()


@router.get("/{student_id}/progress", response_model=StudentProgressResponse, status_code=status.HTTP_200_OK)
async def get_student_progress(
    student_id: UUID,
    subject: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    time_range: Optional[str] = Query(None, pattern="^(last_week|last_month|all_time)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get student progress"""
    # Verify access: students can only view their own progress
    if current_user.get("role") == "student" and UUID(current_user["user_id"]) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    progress_service = ProgressService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = progress_service.get_student_progress(
        student_id=student_id,
        tenant_id=tenant_id,
        subject=subject,
        grade_level=grade_level,
        time_range=time_range,
    )
    
    return StudentProgressResponse(**result)


@router.get("/{student_id}/analytics", response_model=PerformanceAnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_performance_analytics(
    student_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get performance analytics"""
    # Verify access
    if current_user.get("role") == "student" and UUID(current_user["user_id"]) != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    progress_service = ProgressService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = progress_service.get_performance_analytics(
        student_id=student_id,
        tenant_id=tenant_id,
    )
    
    return PerformanceAnalyticsResponse(**result)

