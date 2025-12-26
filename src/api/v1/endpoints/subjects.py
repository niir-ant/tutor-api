"""
Subjects endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.get("")
async def list_subjects(db: Session = Depends(get_db)):
    """List subjects - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{subject_id}")
async def get_subject(subject_id: str, db: Session = Depends(get_db)):
    """Get subject - TODO: Implement"""
    return {"message": "Not implemented"}

