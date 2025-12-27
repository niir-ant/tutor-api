"""
Progress service - updated for new model structure
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, Dict, Any
from uuid import UUID

from src.models.database import (
    StudentProgress, AnswerSubmission, QuizSession, UserAccount
)
from src.core.exceptions import NotFoundError


class ProgressService:
    """Progress service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_student_progress(
        self,
        student_id: UUID,
        tenant_id: UUID,
        subject: Optional[str] = None,
        grade_level: Optional[int] = None,
        time_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get student progress"""
        # Validate student
        student = self.db.query(UserAccount).filter(
            and_(
                UserAccount.user_id == student_id,
                UserAccount.tenant_id == tenant_id
            )
        ).first()
        
        if not student:
            raise NotFoundError("Student not found")
        
        # Get or create progress record
        progress = self.db.query(StudentProgress).filter(
            and_(
                StudentProgress.student_id == student_id,
                StudentProgress.tenant_id == tenant_id
            )
        ).first()
        
        if not progress:
            progress = StudentProgress(
                student_id=student_id,
                tenant_id=tenant_id,
                subject_stats={},
            )
            self.db.add(progress)
            self.db.commit()
        
        # Calculate overall stats from answer submissions
        query = self.db.query(
            func.count(AnswerSubmission.submission_id).label("total"),
            func.sum(func.cast(AnswerSubmission.is_correct, func.Integer)).label("correct"),
            func.avg(AnswerSubmission.score).label("avg_score"),
        ).filter(
            and_(
                AnswerSubmission.student_id == student_id,
                AnswerSubmission.tenant_id == tenant_id
            )
        )
        
        # Apply filters
        if time_range:
            from datetime import datetime, timedelta
            if time_range == "last_week":
                cutoff = datetime.utcnow() - timedelta(days=7)
                query = query.filter(AnswerSubmission.submitted_at >= cutoff)
            elif time_range == "last_month":
                cutoff = datetime.utcnow() - timedelta(days=30)
                query = query.filter(AnswerSubmission.submitted_at >= cutoff)
        
        stats = query.first()
        
        total_questions = stats.total or 0
        correct_answers = stats.correct or 0
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
        average_score = float(stats.avg_score or 0.0)
        
        # Get subject stats from progress record
        subject_stats = progress.subject_stats or {}
        
        # Calculate trends (simplified)
        weak_areas = []
        strong_areas = []
        
        return {
            "student_id": str(student_id),
            "overall_stats": {
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "accuracy": accuracy,
                "average_score": average_score,
            },
            "by_subject": subject_stats,
            "by_topic": {},
            "trends": {
                "improvement_rate": None,
                "weak_areas": weak_areas,
                "strong_areas": strong_areas,
            },
        }
    
    def get_performance_analytics(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get performance analytics"""
        # Get progress
        progress_data = self.get_student_progress(student_id, tenant_id)
        
        # Additional analytics calculations
        analytics = {
            "progress": progress_data,
            "performance_by_time": {},
            "improvement_trends": {},
        }
        
        return {
            "student_id": str(student_id),
            "analytics": analytics,
        }
