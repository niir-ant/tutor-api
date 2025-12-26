"""
Question schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class GenerateQuestionRequest(BaseModel):
    """Generate question request"""
    subject_id: Optional[UUID] = None
    subject_code: Optional[str] = None
    grade_level: Optional[int] = Field(None, ge=6, le=12)
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    topic: Optional[str] = None
    question_type: Optional[str] = Field(
        None,
        pattern="^(multiple_choice|short_answer|code_completion|code_writing|fill_blank|true_false)$"
    )
    session_id: Optional[UUID] = None


class QuestionMetadata(BaseModel):
    """Question metadata"""
    difficulty: Optional[str] = None
    estimated_time: Optional[int] = None
    learning_objectives: Optional[List[str]] = None
    topic: Optional[str] = None


class QuestionResponse(BaseModel):
    """Question response"""
    question_id: UUID
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    metadata: Optional[QuestionMetadata] = None
    session_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class NarrativeExplanation(BaseModel):
    """Narrative explanation"""
    concept: str
    steps: List[str]
    why_correct: str
    common_mistakes: Optional[List[str]] = None
    related_concepts: Optional[List[str]] = None


class QuestionNarrativeResponse(BaseModel):
    """Question narrative response"""
    question_id: UUID
    narrative: str
    explanation: Optional[NarrativeExplanation] = None
    
    class Config:
        from_attributes = True

