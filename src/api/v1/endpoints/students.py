"""
Students endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user, require_tenant_admin
from src.services.student import StudentService

router = APIRouter()


@router.get("/{student_id}", status_code=status.HTTP_200_OK)
async def get_student(
    student_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get student details"""
    # Verify access
    if current_user.get("role") == "student" and UUID(current_user["user_id"]) != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    student_service = StudentService(db)
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = student_service.get_student(student_id, tenant_id)
    return result

