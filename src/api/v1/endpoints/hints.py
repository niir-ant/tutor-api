"""
Hints endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.post("/{question_id}/hint")
async def get_hint(question_id: str, db: Session = Depends(get_db)):
    """Get hint - TODO: Implement"""
    return {"message": "Not implemented"}

