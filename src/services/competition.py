"""
Competition service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

from src.models.database import (
    Competition, CompetitionRegistration, CompetitionSession,
    QuizSession, UserAccount, Subject
)
from src.core.exceptions import NotFoundError, BadRequestError
from src.services.session import SessionService


class CompetitionService:
    """Competition service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session_service = SessionService(db)
    
    def list_competitions(
        self,
        tenant_id: Optional[UUID] = None,
        subject_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List competitions"""
        query = self.db.query(Competition)
        
        if tenant_id:
            query = query.filter(Competition.tenant_id == tenant_id)
        
        if subject_id:
            query = query.filter(Competition.subject_id == subject_id)
        
        if status:
            query = query.filter(Competition.status == status)
        
        competitions = query.order_by(Competition.created_at.desc()).all()
        
        result = []
        for comp in competitions:
            subject = self.db.query(Subject).filter(Subject.subject_id == comp.subject_id).first()
            result.append({
                "competition_id": comp.competition_id,
                "name": comp.name,
                "subject_id": comp.subject_id,
                "subject_code": subject.subject_code if subject else None,
                "status": comp.status,
                "start_date": comp.start_date,
                "end_date": comp.end_date,
                "registration_start": comp.registration_start,
                "registration_end": comp.registration_end,
                "participant_count": comp.participant_count or 0,
                "created_at": comp.created_at,
            })
        
        return {
            "competitions": result,
            "total": len(result),
        }
    
    def get_competition(self, competition_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get competition details"""
        query = self.db.query(Competition).filter(Competition.competition_id == competition_id)
        
        if tenant_id:
            query = query.filter(Competition.tenant_id == tenant_id)
        
        competition = query.first()
        if not competition:
            raise NotFoundError("Competition not found")
        
        subject = self.db.query(Subject).filter(Subject.subject_id == competition.subject_id).first()
        
        return {
            "competition_id": competition.competition_id,
            "tenant_id": competition.tenant_id,
            "name": competition.name,
            "description": competition.description,
            "subject_id": competition.subject_id,
            "subject_code": subject.subject_code if subject else None,
            "status": competition.status,
            "start_date": competition.start_date,
            "end_date": competition.end_date,
            "registration_start": competition.registration_start,
            "registration_end": competition.registration_end,
            "rules": competition.rules or {},
            "eligibility": competition.eligibility or {},
            "visibility": competition.visibility,
            "participant_count": competition.participant_count or 0,
            "max_participants": competition.max_participants,
            "created_at": competition.created_at,
            "updated_at": competition.updated_at,
        }
    
    def create_competition(
        self,
        tenant_id: Optional[UUID],
        created_by: UUID,
        name: str,
        description: Optional[str],
        subject_id: UUID,
        start_date: datetime,
        end_date: datetime,
        registration_start: datetime,
        registration_end: datetime,
        rules: Dict[str, Any],
        eligibility: Dict[str, Any],
        visibility: str,
        max_participants: Optional[int],
    ) -> Dict[str, Any]:
        """Create a new competition"""
        # Validate subject
        subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        if not subject:
            raise NotFoundError("Subject not found")
        
        # Validate dates
        if start_date >= end_date:
            raise BadRequestError("Start date must be before end date")
        
        if registration_start >= registration_end:
            raise BadRequestError("Registration start must be before registration end")
        
        if registration_end > start_date:
            raise BadRequestError("Registration end must be before competition start")
        
        competition = Competition(
            tenant_id=tenant_id,
            name=name,
            description=description,
            subject_id=subject_id,
            status="upcoming",
            start_date=start_date,
            end_date=end_date,
            registration_start=registration_start,
            registration_end=registration_end,
            rules=rules,
            eligibility=eligibility,
            visibility=visibility,
            max_participants=max_participants,
            participant_count=0,
            created_by=created_by,
        )
        
        self.db.add(competition)
        self.db.commit()
        self.db.refresh(competition)
        
        return {
            "competition_id": competition.competition_id,
            "name": competition.name,
            "status": competition.status,
            "created_at": competition.created_at,
        }
    
    def register_for_competition(
        self,
        competition_id: UUID,
        tenant_id: UUID,
        student_id: UUID,
    ) -> Dict[str, Any]:
        """Register student for competition"""
        # Get competition
        competition = self.db.query(Competition).filter(
            Competition.competition_id == competition_id,
        ).first()
        
        if not competition:
            raise NotFoundError("Competition not found")
        
        # Check if registration is open
        now = datetime.utcnow()
        if now < competition.registration_start or now > competition.registration_end:
            raise BadRequestError("Registration period is closed")
        
        # Check if already registered
        existing = self.db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == competition_id,
            CompetitionRegistration.student_id == student_id,
            CompetitionRegistration.status == "registered",
        ).first()
        
        if existing:
            raise BadRequestError("Already registered for this competition")
        
        # Check max participants
        if competition.max_participants:
            current_count = competition.participant_count or 0
            if current_count >= competition.max_participants:
                raise BadRequestError("Maximum participants reached")
        
        # Create registration
        registration = CompetitionRegistration(
            competition_id=competition_id,
            tenant_id=tenant_id,
            student_id=student_id,
            status="registered",
        )
        
        self.db.add(registration)
        
        # Update participant count
        competition.participant_count = (competition.participant_count or 0) + 1
        
        self.db.commit()
        self.db.refresh(registration)
        
        return {
            "registration_id": registration.registration_id,
            "competition_id": competition_id,
            "student_id": student_id,
            "status": registration.status,
            "registered_at": registration.registered_at,
        }
    
    def start_competition_session(
        self,
        competition_id: UUID,
        tenant_id: UUID,
        student_id: UUID,
    ) -> Dict[str, Any]:
        """Start a competition session"""
        # Get competition
        competition = self.db.query(Competition).filter(
            Competition.competition_id == competition_id,
        ).first()
        
        if not competition:
            raise NotFoundError("Competition not found")
        
        # Check if competition is active
        now = datetime.utcnow()
        if competition.status != "active" or now < competition.start_date or now > competition.end_date:
            raise BadRequestError("Competition is not currently active")
        
        # Check registration
        registration = self.db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == competition_id,
            CompetitionRegistration.student_id == student_id,
            CompetitionRegistration.status == "registered",
        ).first()
        
        if not registration:
            raise BadRequestError("Not registered for this competition")
        
        # Check if already started
        existing_session = self.db.query(CompetitionSession).filter(
            CompetitionSession.competition_id == competition_id,
            CompetitionSession.student_id == student_id,
            CompetitionSession.status == "in_progress",
        ).first()
        
        if existing_session:
            raise BadRequestError("Competition session already started")
        
        # Create quiz session
        rules = competition.rules or {}
        session_data = self.session_service.create_session(
            tenant_id=tenant_id,
            student_id=student_id,
            subject_id=competition.subject_id,
            num_questions=rules.get("num_questions", 10),
            difficulty=rules.get("difficulty"),
            time_limit=rules.get("time_limit"),
        )
        
        # Create competition session
        comp_session = CompetitionSession(
            competition_id=competition_id,
            tenant_id=tenant_id,
            student_id=student_id,
            session_id=session_data["session_id"],
            time_limit=rules.get("time_limit"),
            status="in_progress",
        )
        
        self.db.add(comp_session)
        self.db.commit()
        self.db.refresh(comp_session)
        
        return {
            "competition_session_id": comp_session.competition_session_id,
            "competition_id": competition_id,
            "student_id": student_id,
            "session_id": session_data["session_id"],
            "started_at": comp_session.started_at,
            "time_limit": comp_session.time_limit,
            "questions": session_data["questions"],
        }
    
    def get_leaderboard(
        self,
        competition_id: UUID,
        type: str = "real_time",
        limit: int = 100,
        offset: int = 0,
        grade_level: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get competition leaderboard"""
        competition = self.db.query(Competition).filter(
            Competition.competition_id == competition_id,
        ).first()
        
        if not competition:
            raise NotFoundError("Competition not found")
        
        # Get completed sessions
        query = self.db.query(CompetitionSession).filter(
            CompetitionSession.competition_id == competition_id,
            CompetitionSession.status == "completed",
        )
        
        if grade_level:
            # Join with student profiles to filter by grade
            from src.models.database import StudentSubjectProfile
            query = query.join(StudentSubjectProfile).filter(
                StudentSubjectProfile.grade_level == grade_level
            )
        
        sessions = query.order_by(
            CompetitionSession.score.desc(),
            CompetitionSession.accuracy.desc(),
            CompetitionSession.completion_time.asc(),
        ).limit(limit).offset(offset).all()
        
        leaderboard = []
        for idx, session in enumerate(sessions, start=offset + 1):
            student = self.db.query(UserAccount).filter(
                UserAccount.user_id == session.student_id,
            ).first()
            
            leaderboard.append({
                "rank": idx,
                "student_id": str(session.student_id),
                "student_name": (student.name or student.username) if student else "Unknown",
                "score": float(session.score),
                "max_score": float(session.max_score),
                "accuracy": float(session.accuracy) if session.accuracy else 0.0,
                "completion_time": session.completion_time,
                "questions_answered": session.questions_answered,
                "completed_at": session.completed_at,
            })
        
        total = self.db.query(CompetitionSession).filter(
            CompetitionSession.competition_id == competition_id,
            CompetitionSession.status == "completed",
        ).count()
        
        return {
            "competition_id": competition_id,
            "type": type,
            "last_updated": datetime.utcnow(),
            "leaderboard": leaderboard,
            "total_participants": total,
            "user_rank": None,
            "user_position": None,
        }

