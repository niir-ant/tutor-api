"""
Answers endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.post("/{question_id}/answer")
async def submit_answer(question_id: str, db: Session = Depends(get_db)):
    """Submit answer - TODO: Implement"""
    return {"message": "Not implemented"}


@router.post("/{question_id}/validate")
async def validate_answer(question_id: str, db: Session = Depends(get_db)):
    """Validate answer - TODO: Implement"""
    return {"message": "Not implemented"}

