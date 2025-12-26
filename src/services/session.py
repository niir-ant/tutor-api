"""
Session service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from src.models.database import QuizSession, Question, Subject, StudentAccount
from src.core.exceptions import NotFoundError, BadRequestError
from src.services.question import QuestionService


class SessionService:
    """Session service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.question_service = QuestionService(db)
    
    def create_session(
        self,
        tenant_id: UUID,
        student_id: UUID,
        subject_id: Optional[UUID] = None,
        subject_code: Optional[str] = None,
        grade_level: Optional[int] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 10,
        topics: Optional[List[str]] = None,
        time_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new quiz session"""
        # Validate student
        student = self.db.query(StudentAccount).filter(
            StudentAccount.student_id == student_id,
            StudentAccount.tenant_id == tenant_id,
        ).first()
        
        if not student:
            raise NotFoundError("Student not found")
        
        # Resolve subject
        if subject_id:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        elif subject_code:
            subject = self.db.query(Subject).filter(Subject.subject_code == subject_code).first()
        else:
            raise BadRequestError("Either subject_id or subject_code is required")
        
        if not subject:
            raise NotFoundError("Subject not found")
        
        if subject.status != "active":
            raise BadRequestError("Subject is not active")
        
        # Generate questions
        question_ids = []
        for _ in range(num_questions):
            question = self.question_service.generate_question(
                tenant_id=tenant_id,
                subject_id=subject.subject_id,
                grade_level=grade_level,
                difficulty=difficulty,
                topic=topics[0] if topics else None,
            )
            question_ids.append(question["question_id"])
        
        # Create session
        expires_at = None
        if time_limit:
            expires_at = datetime.utcnow() + timedelta(seconds=time_limit)
        
        session = QuizSession(
            tenant_id=tenant_id,
            student_id=student_id,
            subject_id=subject.subject_id,
            status="in_progress",
            questions=question_ids,
            time_limit=time_limit,
            expires_at=expires_at,
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "session_id": session.session_id,
            "questions": question_ids,
            "created_at": session.created_at,
            "expires_at": session.expires_at,
        }
    
    def get_session_status(self, session_id: UUID, tenant_id: UUID) -> Dict[str, Any]:
        """Get session status"""
        session = self.db.query(QuizSession).filter(
            QuizSession.session_id == session_id,
            QuizSession.tenant_id == tenant_id,
        ).first()
        
        if not session:
            raise NotFoundError("Session not found")
        
        # Calculate current question index
        # TODO: Track current question properly
        current_question = 0
        questions_answered = 0
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "current_question": current_question,
            "total_questions": len(session.questions) if session.questions else 0,
            "score": float(session.score),
            "max_score": float(session.max_score),
            "time_elapsed": session.time_elapsed or 0,
            "questions_answered": questions_answered,
        }
    
    def get_session_results(self, session_id: UUID, tenant_id: UUID) -> Dict[str, Any]:
        """Get session results"""
        session = self.db.query(QuizSession).filter(
            QuizSession.session_id == session_id,
            QuizSession.tenant_id == tenant_id,
        ).first()
        
        if not session:
            raise NotFoundError("Session not found")
        
        accuracy = 0.0
        if session.max_score > 0:
            accuracy = (session.score / session.max_score) * 100
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "score": float(session.score),
            "max_score": float(session.max_score),
            "accuracy": accuracy,
            "questions_answered": len(session.questions) if session.questions else 0,
            "time_elapsed": session.time_elapsed or 0,
            "completed_at": session.completed_at,
            "questions": [],  # TODO: Include question details
        }

