"""
Message schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SendMessageRequest(BaseModel):
    """Send message request"""
    recipient_id: UUID
    content: str
    send_email_copy: bool = False
    subject_reference: Optional[UUID] = None
    question_reference: Optional[UUID] = None


class MessageItem(BaseModel):
    """Message item"""
    message_id: UUID
    sender_id: UUID
    sender_name: str
    sender_role: str
    recipient_id: UUID
    recipient_name: str
    content: str
    status: str
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    """Send message response"""
    message_id: UUID
    sender_id: UUID
    recipient_id: UUID
    content: str
    status: str
    email_sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Message list response"""
    messages: List[MessageItem]
    total: int
    unread_count: int


class ConversationResponse(BaseModel):
    """Conversation response"""
    conversation_with: dict
    messages: List[MessageItem]
    total: int


class MarkReadResponse(BaseModel):
    """Mark read response"""
    message_id: UUID
    status: str
    read_at: datetime
    
    class Config:
        from_attributes = True


class MarkConversationReadResponse(BaseModel):
    """Mark conversation read response"""
    conversation_with: UUID
    messages_marked_read: int

