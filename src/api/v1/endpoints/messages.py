"""
Messages endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.post("")
async def send_message(db: Session = Depends(get_db)):
    """Send message - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("")
async def get_messages(db: Session = Depends(get_db)):
    """Get messages - TODO: Implement"""
    return {"message": "Not implemented"}


@router.get("/conversations/{user_id}")
async def get_conversation(user_id: str, db: Session = Depends(get_db)):
    """Get conversation - TODO: Implement"""
    return {"message": "Not implemented"}


@router.put("/{message_id}/read")
async def mark_message_read(message_id: str, db: Session = Depends(get_db)):
    """Mark message as read - TODO: Implement"""
    return {"message": "Not implemented"}


@router.put("/conversations/{user_id}/read")
async def mark_conversation_read(user_id: str, db: Session = Depends(get_db)):
    """Mark conversation as read - TODO: Implement"""
    return {"message": "Not implemented"}


@router.delete("/{message_id}")
async def delete_message(message_id: str, db: Session = Depends(get_db)):
    """Delete message - TODO: Implement"""
    return {"message": "Not implemented"}

