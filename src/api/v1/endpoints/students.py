"""
Students endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.get("/{student_id}")
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """Get student - TODO: Implement"""
    return {"message": "Not implemented"}

