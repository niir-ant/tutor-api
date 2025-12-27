"""
Competitions endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user, require_role, require_system_admin, require_tenant_admin
from src.models.user import UserRole
from src.schemas.competition import (
    CompetitionListResponse,
    CompetitionDetailResponse,
    CreateCompetitionRequest,
    UpdateCompetitionRequest,
    CompetitionRegistrationResponse,
    CompetitionLeaderboardResponse,
    CompetitionResultsResponse,
    CompetitionStatisticsResponse,
)
from src.services.competition import CompetitionService

router = APIRouter()


@router.get("", response_model=CompetitionListResponse, status_code=status.HTTP_200_OK)
async def list_competitions(
    subject_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List competitions"""
    competition_service = CompetitionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = competition_service.list_competitions(
        tenant_id=tenant_id,
        subject_id=subject_id,
        status=status_filter,
    )
    
    return CompetitionListResponse(**result)


@router.get("/{competition_id}", response_model=CompetitionDetailResponse, status_code=status.HTTP_200_OK)
async def get_competition(
    competition_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get competition details"""
    competition_service = CompetitionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    
    result = competition_service.get_competition(competition_id, tenant_id)
    
    return CompetitionDetailResponse(**result)


@router.post("/{competition_id}/register", response_model=CompetitionRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_competition(
    competition_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register for competition"""
    if current_user.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can register")
    
    competition_service = CompetitionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    student_id = UUID(current_user["user_id"])
    
    result = competition_service.register_for_competition(
        competition_id=competition_id,
        tenant_id=tenant_id,
        student_id=student_id,
    )
    
    return CompetitionRegistrationResponse(**result)


@router.post("/{competition_id}/start", status_code=status.HTTP_201_CREATED)
async def start_competition_session(
    competition_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start competition session"""
    if current_user.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can start competition sessions")
    
    competition_service = CompetitionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    student_id = UUID(current_user["user_id"])
    
    result = competition_service.start_competition_session(
        competition_id=competition_id,
        tenant_id=tenant_id,
        student_id=student_id,
    )
    
    return result


@router.get("/{competition_id}/leaderboard", response_model=CompetitionLeaderboardResponse, status_code=status.HTTP_200_OK)
async def get_competition_leaderboard(
    competition_id: UUID,
    type: str = Query("real_time"),
    limit: int = Query(100),
    offset: int = Query(0),
    grade_level: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Get competition leaderboard"""
    competition_service = CompetitionService(db)
    
    result = competition_service.get_leaderboard(
        competition_id=competition_id,
        type=type,
        limit=limit,
        offset=offset,
        grade_level=grade_level,
    )
    
    return CompetitionLeaderboardResponse(**result)


@router.get("/{competition_id}/results", response_model=CompetitionResultsResponse, status_code=status.HTTP_200_OK)
async def get_competition_results(
    competition_id: UUID,
    db: Session = Depends(get_db),
):
    """Get competition results"""
    competition_service = CompetitionService(db)
    competition = competition_service.get_competition(competition_id)
    
    if competition["status"] != "ended":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition has not ended")
    
    # Get leaderboard
    leaderboard_data = competition_service.get_leaderboard(competition_id, type="final", limit=100)
    
    # TODO: Get winners and statistics
    return CompetitionResultsResponse(
        competition_id=competition_id,
        name=competition["name"],
        status=competition["status"],
        ended_at=competition.get("end_date"),
        total_participants=leaderboard_data["total_participants"],
        winners=leaderboard_data["leaderboard"][:10],  # Top 10
        statistics={},
        leaderboard=leaderboard_data["leaderboard"],
    )


# Admin endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_competition(
    request: CreateCompetitionRequest,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Create competition (admin only)"""
    competition_service = CompetitionService(db)
    
    tenant_id = UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None
    created_by = UUID(current_user["user_id"])
    
    result = competition_service.create_competition(
        tenant_id=tenant_id,
        created_by=created_by,
        name=request.name,
        description=request.description,
        subject_id=request.subject_id,
        start_date=request.start_date,
        end_date=request.end_date,
        registration_start=request.registration_start,
        registration_end=request.registration_end,
        rules=request.rules.dict() if hasattr(request.rules, 'dict') else request.rules,
        eligibility=request.eligibility.dict() if hasattr(request.eligibility, 'dict') else request.eligibility,
        visibility=request.visibility,
        max_participants=request.max_participants,
    )
    
    return result


@router.get("/{competition_id}/statistics", response_model=CompetitionStatisticsResponse, status_code=status.HTTP_200_OK)
async def get_competition_statistics(
    competition_id: UUID,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Get competition statistics (admin only)"""
    # TODO: Implement statistics calculation
    return CompetitionStatisticsResponse(
        competition_id=competition_id,
        name="",
        status="",
        registrations={"total": 0, "confirmed": 0, "cancelled": 0},
        participation={"started": 0, "completed": 0, "completion_rate": 0.0},
        performance={"average_score": 0.0, "highest_score": 0.0, "lowest_score": 0.0, "median_score": 0.0},
        timing={"average_completion_time": None, "fastest_completion": None, "slowest_completion": None},
    )

