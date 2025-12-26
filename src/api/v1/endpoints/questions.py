"""
Questions endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.post("/generate")
async def generate_question(db: Session = Depends(get_db)):
    """Generate question - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{question_id}")
async def get_question(question_id: str, db: Session = Depends(get_db)):
    """Get question - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{question_id}/narrative")
async def get_question_narrative(question_id: str, db: Session = Depends(get_db)):
    """Get question narrative - TODO: Implement"""
    return {"message": "Not implemented"}

