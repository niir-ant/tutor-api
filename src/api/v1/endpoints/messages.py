"""
Messages endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.schemas.message import (
    SendMessageRequest,
    SendMessageResponse,
    MessageListResponse,
    ConversationResponse,
    MarkReadResponse,
    MarkConversationReadResponse,
)
from src.services.message import MessageService

router = APIRouter()


@router.post("", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    sender_id = UUID(current_user["user_id"])
    sender_role = current_user.get("role", "student")
    
    result = message_service.send_message(
        tenant_id=tenant_id,
        sender_id=sender_id,
        sender_role=sender_role,
        recipient_id=request.recipient_id,
        content=request.content,
        send_email_copy=request.send_email_copy,
        subject_reference=request.subject_reference,
        question_reference=request.question_reference,
    )
    
    return SendMessageResponse(**result)


@router.get("", response_model=MessageListResponse, status_code=status.HTTP_200_OK)
async def get_messages(
    conversation_with: Optional[UUID] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(50),
    offset: int = Query(0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get messages"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    user_id = UUID(current_user["user_id"])
    
    result = message_service.get_messages(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_with=conversation_with,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    
    return MessageListResponse(**result)


@router.get("/conversations/{user_id}", response_model=ConversationResponse, status_code=status.HTTP_200_OK)
async def get_conversation(
    user_id: UUID,
    limit: int = Query(50),
    offset: int = Query(0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get conversation thread"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    current_user_id = UUID(current_user["user_id"])
    
    result = message_service.get_conversation(
        tenant_id=tenant_id,
        user_id=current_user_id,
        other_user_id=user_id,
        limit=limit,
        offset=offset,
    )
    
    return ConversationResponse(**result)


@router.put("/{message_id}/read", response_model=MarkReadResponse, status_code=status.HTTP_200_OK)
async def mark_message_read(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark message as read"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    user_id = UUID(current_user["user_id"])
    
    result = message_service.mark_message_read(message_id, tenant_id, user_id)
    
    return MarkReadResponse(**result)


@router.put("/conversations/{user_id}/read", response_model=MarkConversationReadResponse, status_code=status.HTTP_200_OK)
async def mark_conversation_read(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark conversation as read"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    current_user_id = UUID(current_user["user_id"])
    
    result = message_service.mark_conversation_read(tenant_id, current_user_id, user_id)
    
    return MarkConversationReadResponse(**result)


@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a message"""
    message_service = MessageService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    user_id = UUID(current_user["user_id"])
    
    result = message_service.delete_message(message_id, tenant_id, user_id)
    
    return result

