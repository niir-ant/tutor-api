"""
Answer schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID


class SubmitAnswerRequest(BaseModel):
    """Submit answer request"""
    answer: Any  # Can be string, object, or array
    student_id: UUID
    session_id: Optional[UUID] = None
    time_spent: Optional[int] = None
    hints_used: Optional[List[UUID]] = None


class SubmitAnswerResponse(BaseModel):
    """Submit answer response"""
    question_id: UUID
    correct: bool
    score: float
    max_score: float
    feedback: str
    correct_answer: Optional[Any] = None
    explanation: Optional[str] = None
    areas_correct: Optional[List[str]] = None
    areas_incorrect: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class ValidateAnswerRequest(BaseModel):
    """Validate answer request (pre-submission)"""
    answer: Any
    student_id: Optional[UUID] = None


class ValidateAnswerResponse(BaseModel):
    """Validate answer response"""
    correct: bool
    score: float
    max_score: float
    feedback: str
    areas_correct: Optional[List[str]] = None
    areas_incorrect: Optional[List[str]] = None

