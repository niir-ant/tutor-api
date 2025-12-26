"""
Sessions endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.post("")
async def create_session(db: Session = Depends(get_db)):
    """Create session - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{session_id}")
async def get_session_status(session_id: str, db: Session = Depends(get_db)):
    """Get session status - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/{session_id}/results")
async def get_session_results(session_id: str, db: Session = Depends(get_db)):
    """Get session results - TODO: Implement"""
    return {"message": "Not implemented"}

