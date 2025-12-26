"""
Message service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

from src.models.database import Message, StudentAccount, TutorAccount, StudentTutorAssignment
from src.models.user import UserRole
from src.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class MessageService:
    """Message service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_message(
        self,
        tenant_id: UUID,
        sender_id: UUID,
        sender_role: str,
        recipient_id: UUID,
        content: str,
        send_email_copy: bool = False,
        subject_reference: Optional[UUID] = None,
        question_reference: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Send a message"""
        # Validate sender-recipient relationship
        if sender_role == "student":
            # Student can only message their assigned tutor
            assignment = self.db.query(StudentTutorAssignment).filter(
                StudentTutorAssignment.student_id == sender_id,
                StudentTutorAssignment.tutor_id == recipient_id,
                StudentTutorAssignment.tenant_id == tenant_id,
                StudentTutorAssignment.status == "active",
            ).first()
            
            if not assignment:
                raise ForbiddenError("You can only message your assigned tutor")
            
            recipient_role = "tutor"
        elif sender_role == "tutor":
            # Tutor can message assigned students
            assignment = self.db.query(StudentTutorAssignment).filter(
                StudentTutorAssignment.tutor_id == sender_id,
                StudentTutorAssignment.student_id == recipient_id,
                StudentTutorAssignment.tenant_id == tenant_id,
                StudentTutorAssignment.status == "active",
            ).first()
            
            if not assignment:
                raise ForbiddenError("You can only message your assigned students")
            
            recipient_role = "student"
        else:
            raise BadRequestError("Invalid sender role")
        
        # Generate conversation ID
        conversation_id = self._get_conversation_id(sender_id, recipient_id)
        
        # Create message
        message = Message(
            tenant_id=tenant_id,
            sender_id=sender_id,
            sender_role=UserRole(sender_role),
            recipient_id=recipient_id,
            recipient_role=UserRole(recipient_role),
            content=content,
            status="sent",
            email_sent=False,
            subject_reference=subject_reference,
            question_reference=question_reference,
            conversation_id=conversation_id,
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Send email copy if requested
        email_sent = False
        if send_email_copy:
            # TODO: Implement email sending
            email_sent = False
            message.email_sent = email_sent
            if email_sent:
                message.email_sent_at = datetime.utcnow()
            self.db.commit()
        
        return {
            "message_id": message.message_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
            "status": message.status,
            "email_sent": email_sent,
            "created_at": message.created_at,
        }
    
    def get_messages(
        self,
        tenant_id: UUID,
        user_id: UUID,
        conversation_with: Optional[UUID] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get messages for a user"""
        query = self.db.query(Message).filter(
            Message.tenant_id == tenant_id,
            Message.deleted_at.is_(None),
        ).filter(
            (Message.sender_id == user_id) | (Message.recipient_id == user_id),
        )
        
        if conversation_with:
            query = query.filter(
                (Message.sender_id == conversation_with) | (Message.recipient_id == conversation_with),
            )
        
        if unread_only:
            query = query.filter(Message.read_at.is_(None))
        
        messages = query.order_by(Message.created_at.desc()).limit(limit).offset(offset).all()
        
        result = []
        for msg in messages:
            sender = self._get_user_info(msg.sender_id, msg.sender_role.value)
            recipient = self._get_user_info(msg.recipient_id, msg.recipient_role.value)
            
            result.append({
                "message_id": msg.message_id,
                "sender_id": msg.sender_id,
                "sender_name": sender.get("name", "Unknown"),
                "sender_role": msg.sender_role.value,
                "recipient_id": msg.recipient_id,
                "recipient_name": recipient.get("name", "Unknown"),
                "content": msg.content,
                "status": msg.status,
                "read_at": msg.read_at,
                "created_at": msg.created_at,
            })
        
        unread_count = self.db.query(Message).filter(
            Message.tenant_id == tenant_id,
            Message.recipient_id == user_id,
            Message.read_at.is_(None),
            Message.deleted_at.is_(None),
        ).count()
        
        return {
            "messages": result,
            "total": len(result),
            "unread_count": unread_count,
        }
    
    def get_conversation(
        self,
        tenant_id: UUID,
        user_id: UUID,
        other_user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get conversation thread"""
        # Get other user info
        other_user = self._get_user_info(other_user_id, None)
        
        # Get messages
        messages_data = self.get_messages(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_with=other_user_id,
            limit=limit,
            offset=offset,
        )
        
        return {
            "conversation_with": {
                "user_id": other_user_id,
                "name": other_user.get("name", "Unknown"),
                "role": other_user.get("role", "unknown"),
            },
            "messages": messages_data["messages"],
            "total": messages_data["total"],
        }
    
    def mark_message_read(self, message_id: UUID, tenant_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Mark message as read"""
        message = self.db.query(Message).filter(
            Message.message_id == message_id,
            Message.tenant_id == tenant_id,
            Message.recipient_id == user_id,
        ).first()
        
        if not message:
            raise NotFoundError("Message not found")
        
        if not message.read_at:
            message.read_at = datetime.utcnow()
            message.status = "read"
            self.db.commit()
        
        return {
            "message_id": message.message_id,
            "status": message.status,
            "read_at": message.read_at,
        }
    
    def mark_conversation_read(
        self,
        tenant_id: UUID,
        user_id: UUID,
        other_user_id: UUID,
    ) -> Dict[str, Any]:
        """Mark all messages in conversation as read"""
        count = self.db.query(Message).filter(
            Message.tenant_id == tenant_id,
            Message.recipient_id == user_id,
            Message.sender_id == other_user_id,
            Message.read_at.is_(None),
        ).update({
            "read_at": datetime.utcnow(),
            "status": "read",
        })
        
        self.db.commit()
        
        return {
            "conversation_with": other_user_id,
            "messages_marked_read": count,
        }
    
    def delete_message(self, message_id: UUID, tenant_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Delete a message (soft delete)"""
        message = self.db.query(Message).filter(
            Message.message_id == message_id,
            Message.tenant_id == tenant_id,
        ).filter(
            (Message.sender_id == user_id) | (Message.recipient_id == user_id),
        ).first()
        
        if not message:
            raise NotFoundError("Message not found")
        
        message.deleted_at = datetime.utcnow()
        message.status = "deleted"
        self.db.commit()
        
        return {
            "message_id": message.message_id,
            "status": "deleted",
            "deleted_at": message.deleted_at,
        }
    
    def _get_conversation_id(self, user1_id: UUID, user2_id: UUID) -> UUID:
        """Generate consistent conversation ID"""
        # Sort IDs to ensure consistent conversation ID
        ids = sorted([str(user1_id), str(user2_id)])
        # Use hash to generate UUID-like identifier
        import hashlib
        hash_obj = hashlib.md5(f"{ids[0]}_{ids[1]}".encode())
        return UUID(hash_obj.hexdigest())
    
    def _get_user_info(self, user_id: UUID, role: Optional[str]) -> Dict[str, Any]:
        """Get user information"""
        if role == "student":
            user = self.db.query(StudentAccount).filter(StudentAccount.student_id == user_id).first()
            if user:
                return {"name": user.username, "role": "student"}
        elif role == "tutor":
            user = self.db.query(TutorAccount).filter(TutorAccount.tutor_id == user_id).first()
            if user:
                return {"name": user.name or user.username, "role": "tutor"}
        
        return {"name": "Unknown", "role": role or "unknown"}

