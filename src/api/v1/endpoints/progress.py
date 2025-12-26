"""
Progress endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.get("/{student_id}/progress")
async def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    """Get student progress - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{student_id}/analytics")
async def get_performance_analytics(student_id: str, db: Session = Depends(get_db)):
    """Get performance analytics - TODO: Implement"""
    return {"message": "Not implemented"}

