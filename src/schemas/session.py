"""
Session schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CreateSessionRequest(BaseModel):
    """Create quiz session request"""
    student_id: UUID
    subject_id: Optional[UUID] = None
    subject_code: Optional[str] = None
    grade_level: Optional[int] = None
    difficulty: Optional[str] = None
    num_questions: int
    topics: Optional[List[str]] = None
    time_limit: Optional[int] = None


class CreateSessionResponse(BaseModel):
    """Create quiz session response"""
    session_id: UUID
    questions: List[UUID]
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SessionStatusResponse(BaseModel):
    """Session status response"""
    session_id: UUID
    status: str
    current_question: int
    total_questions: int
    score: float
    max_score: float
    time_elapsed: int
    questions_answered: int
    
    class Config:
        from_attributes = True


class SessionResultsResponse(BaseModel):
    """Session results response"""
    session_id: UUID
    status: str
    score: float
    max_score: float
    accuracy: float
    questions_answered: int
    time_elapsed: int
    completed_at: Optional[datetime] = None
    questions: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True

