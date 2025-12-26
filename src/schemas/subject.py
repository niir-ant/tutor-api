"""
Subject schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class SubjectSettings(BaseModel):
    """Subject settings"""
    default_difficulty: Optional[str] = None
    ai_prompt_template: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    hint_strategy: Optional[str] = None


class SubjectMetadata(BaseModel):
    """Subject metadata"""
    curriculum: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    icon_url: Optional[str] = None
    category: Optional[str] = None


class SubjectListItem(BaseModel):
    """Subject list item"""
    subject_id: UUID
    subject_code: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    status: str
    supported_question_types: Optional[List[str]] = None
    answer_validation_method: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubjectListResponse(BaseModel):
    """Subject list response"""
    subjects: List[SubjectListItem]
    total: int


class SubjectDetailResponse(BaseModel):
    """Subject detail response"""
    subject_id: UUID
    subject_code: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    status: str
    supported_question_types: Optional[List[str]] = None
    answer_validation_method: Optional[str] = None
    settings: Optional[SubjectSettings] = None
    metadata: Optional[SubjectMetadata] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateSubjectRequest(BaseModel):
    """Create subject request"""
    subject_code: str
    name: str
    description: Optional[str] = None
    type: str
    grade_levels: Optional[List[int]] = None
    supported_question_types: List[str]
    answer_validation_method: str
    settings: Optional[SubjectSettings] = None
    metadata: Optional[SubjectMetadata] = None


class UpdateSubjectRequest(BaseModel):
    """Update subject request"""
    name: Optional[str] = None
    description: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    status: Optional[str] = None
    supported_question_types: Optional[List[str]] = None
    settings: Optional[SubjectSettings] = None
    metadata: Optional[SubjectMetadata] = None


class SubjectStatisticsResponse(BaseModel):
    """Subject statistics response"""
    subject_id: UUID
    subject_code: str
    total_questions: int
    total_sessions: int
    total_students: int
    average_score: float
    questions_by_difficulty: Dict[str, int]

