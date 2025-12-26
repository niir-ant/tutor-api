"""
Competition schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class CompetitionRules(BaseModel):
    """Competition rules"""
    time_limit: Optional[int] = None
    num_questions: int
    difficulty: Optional[str] = None
    allowed_question_types: Optional[List[str]] = None
    max_attempts: int = 1
    scoring_rules: Optional[Dict[str, Any]] = None
    hints_allowed: bool = False
    narratives_allowed: bool = False


class CompetitionEligibility(BaseModel):
    """Competition eligibility"""
    grade_levels: Optional[List[int]] = None
    tenant_restrictions: Optional[List[UUID]] = None
    minimum_requirements: Optional[Dict[str, Any]] = None


class CompetitionListItem(BaseModel):
    """Competition list item"""
    competition_id: UUID
    name: str
    subject_id: UUID
    subject_code: str
    status: str
    start_date: datetime
    end_date: datetime
    registration_start: datetime
    registration_end: datetime
    participant_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompetitionListResponse(BaseModel):
    """Competition list response"""
    competitions: List[CompetitionListItem]
    total: int


class CompetitionDetailResponse(BaseModel):
    """Competition detail response"""
    competition_id: UUID
    tenant_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    subject_id: UUID
    subject_code: str
    status: str
    start_date: datetime
    end_date: datetime
    registration_start: datetime
    registration_end: datetime
    rules: CompetitionRules
    eligibility: CompetitionEligibility
    visibility: str
    participant_count: int
    max_participants: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateCompetitionRequest(BaseModel):
    """Create competition request"""
    name: str
    description: Optional[str] = None
    subject_id: UUID
    start_date: datetime
    end_date: datetime
    registration_start: datetime
    registration_end: datetime
    rules: CompetitionRules
    eligibility: CompetitionEligibility
    visibility: str = "public"
    max_participants: Optional[int] = None


class UpdateCompetitionRequest(BaseModel):
    """Update competition request"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    rules: Optional[CompetitionRules] = None
    eligibility: Optional[CompetitionEligibility] = None
    visibility: Optional[str] = None
    max_participants: Optional[int] = None


class CompetitionRegistrationResponse(BaseModel):
    """Competition registration response"""
    registration_id: UUID
    competition_id: UUID
    student_id: UUID
    status: str
    registered_at: datetime
    
    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    student_id: UUID
    student_name: str
    score: float
    max_score: float
    accuracy: float
    completion_time: Optional[int] = None
    questions_answered: int
    completed_at: Optional[datetime] = None


class CompetitionLeaderboardResponse(BaseModel):
    """Competition leaderboard response"""
    competition_id: UUID
    type: str
    last_updated: datetime
    leaderboard: List[LeaderboardEntry]
    total_participants: int
    user_rank: Optional[int] = None
    user_position: Optional[LeaderboardEntry] = None


class CompetitionResultsResponse(BaseModel):
    """Competition results response"""
    competition_id: UUID
    name: str
    status: str
    ended_at: Optional[datetime] = None
    total_participants: int
    winners: List[LeaderboardEntry]
    statistics: Dict[str, Any]
    leaderboard: List[LeaderboardEntry]


class CompetitionStatisticsResponse(BaseModel):
    """Competition statistics response"""
    competition_id: UUID
    name: str
    status: str
    registrations: Dict[str, int]
    participation: Dict[str, Any]
    performance: Dict[str, float]
    timing: Dict[str, Optional[int]]

