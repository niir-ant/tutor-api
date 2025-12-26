"""
Hint schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID


class GetHintRequest(BaseModel):
    """Get hint request"""
    hint_level: Optional[int] = Field(None, ge=1, le=4)
    student_id: UUID
    previous_attempts: Optional[List[Any]] = None
    hints_already_shown: Optional[List[UUID]] = None


class GetHintResponse(BaseModel):
    """Get hint response"""
    hint_id: UUID
    hint_level: int
    hint_text: str
    remaining_hints: int
    
    class Config:
        from_attributes = True

