"""
Tutors endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user, require_tutor_or_admin, require_tenant_admin
from src.services.tutor import TutorService

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def list_tutors(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """List tutors (admin only)"""
    tutor_service = TutorService(db)
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = tutor_service.list_tutors(tenant_id=tenant_id, status=status, search=search)
    return result


@router.get("/{tutor_id}", status_code=status.HTTP_200_OK)
async def get_tutor(
    tutor_id: UUID,
    current_user: dict = Depends(require_tutor_or_admin),
    db: Session = Depends(get_db),
):
    """Get tutor details"""
    # Verify access: tutors can only view their own profile unless admin
    if current_user.get("role") == "tutor" and UUID(current_user["user_id"]) != tutor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    tutor_service = TutorService(db)
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = tutor_service.get_tutor(tutor_id, tenant_id)
    return result


@router.get("/{tutor_id}/students", status_code=status.HTTP_200_OK)
async def get_tutor_students(
    tutor_id: UUID,
    current_user: dict = Depends(require_tutor_or_admin),
    db: Session = Depends(get_db),
):
    """Get tutor's students"""
    # Verify access
    if current_user.get("role") == "tutor" and UUID(current_user["user_id"]) != tutor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    tutor_service = TutorService(db)
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = tutor_service.get_tutor_students(tutor_id, tenant_id)
    return result


@router.get("/{tutor_id}/students/{student_id}/progress", status_code=status.HTTP_200_OK)
async def get_tutor_student_progress(
    tutor_id: UUID,
    student_id: UUID,
    current_user: dict = Depends(require_tutor_or_admin),
    db: Session = Depends(get_db),
):
    """Get student progress (tutor view)"""
    # Verify access
    if current_user.get("role") == "tutor" and UUID(current_user["user_id"]) != tutor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    tutor_service = TutorService(db)
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = tutor_service.get_student_progress(tutor_id, student_id, tenant_id)
    return result

