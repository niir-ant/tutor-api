"""
Progress schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID


class OverallStats(BaseModel):
    """Overall statistics"""
    total_questions: int
    correct_answers: int
    accuracy: float
    average_score: float


class SubjectStats(BaseModel):
    """Subject statistics"""
    total_questions: int
    correct_answers: int
    accuracy: float
    average_score: float
    topics: Optional[Dict[str, Any]] = None


class ProgressTrends(BaseModel):
    """Progress trends"""
    improvement_rate: Optional[float] = None
    weak_areas: List[str]
    strong_areas: List[str]


class StudentProgressResponse(BaseModel):
    """Student progress response"""
    student_id: UUID
    overall_stats: OverallStats
    by_subject: Dict[str, SubjectStats]
    by_topic: Optional[Dict[str, Any]] = None
    trends: ProgressTrends
    
    class Config:
        from_attributes = True


class PerformanceAnalyticsResponse(BaseModel):
    """Performance analytics response"""
    student_id: UUID
    analytics: Dict[str, Any]
    
    class Config:
        from_attributes = True

