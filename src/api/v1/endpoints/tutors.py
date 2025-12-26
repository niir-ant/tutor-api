"""
Tutors endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.get("")
async def list_tutors(db: Session = Depends(get_db)):
    """List tutors - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{tutor_id}")
async def get_tutor(tutor_id: str, db: Session = Depends(get_db)):
    """Get tutor - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{tutor_id}/students")
async def get_tutor_students(tutor_id: str, db: Session = Depends(get_db)):
    """Get tutor's students - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{tutor_id}/students/{student_id}/progress")
async def get_tutor_student_progress(tutor_id: str, student_id: str, db: Session = Depends(get_db)):
    """Get tutor student progress - TODO: Implement"""
    return {"message": "Not implemented"}

