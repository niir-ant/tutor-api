"""
Subject service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID

from src.models.database import Subject
from src.core.exceptions import NotFoundError, BadRequestError


class SubjectService:
    """Subject service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_subjects(
        self,
        status: Optional[str] = None,
        grade_level: Optional[int] = None,
        type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List subjects"""
        query = self.db.query(Subject)
        
        if status:
            query = query.filter(Subject.status == status)
        
        if grade_level:
            # Filter subjects that support this grade level
            query = query.filter(
                (Subject.grade_levels.is_(None)) | (grade_level.in_(Subject.grade_levels))
            )
        
        if type:
            query = query.filter(Subject.type == type)
        
        subjects = query.order_by(Subject.name).all()
        
        result = []
        for subject in subjects:
            result.append({
                "subject_id": subject.subject_id,
                "subject_code": subject.subject_code,
                "name": subject.name,
                "description": subject.description,
                "type": subject.type,
                "grade_levels": subject.grade_levels,
                "status": subject.status,
                "supported_question_types": subject.supported_question_types,
                "answer_validation_method": subject.answer_validation_method,
                "created_at": subject.created_at,
                "updated_at": subject.updated_at,
            })
        
        return {
            "subjects": result,
            "total": len(result),
        }
    
    def get_subject(self, subject_id: UUID) -> Dict[str, Any]:
        """Get subject details"""
        subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        
        if not subject:
            raise NotFoundError("Subject not found")
        
        return {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "name": subject.name,
            "description": subject.description,
            "type": subject.type,
            "grade_levels": subject.grade_levels,
            "status": subject.status,
            "supported_question_types": subject.supported_question_types,
            "answer_validation_method": subject.answer_validation_method,
            "settings": subject.settings,
            "metadata": subject.extra_metadata,
            "created_at": subject.created_at,
            "updated_at": subject.updated_at,
        }
    
    def create_subject(
        self,
        subject_code: str,
        name: str,
        description: Optional[str],
        type: str,
        grade_levels: Optional[List[int]],
        supported_question_types: List[str],
        answer_validation_method: str,
        settings: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a new subject"""
        # Check if subject_code already exists
        existing = self.db.query(Subject).filter(Subject.subject_code == subject_code).first()
        if existing:
            raise BadRequestError(f"Subject with code '{subject_code}' already exists")
        
        subject = Subject(
            subject_code=subject_code,
            name=name,
            description=description,
            type=type,
            grade_levels=grade_levels,
            status="active",
            supported_question_types=supported_question_types,
            answer_validation_method=answer_validation_method,
            settings=settings,
            extra_metadata=metadata,
        )
        
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        
        return {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "name": subject.name,
            "status": subject.status,
            "created_at": subject.created_at,
        }
    
    def update_subject(
        self,
        subject_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        grade_levels: Optional[List[int]] = None,
        status: Optional[str] = None,
        supported_question_types: Optional[List[str]] = None,
        settings: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update subject"""
        subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        
        if not subject:
            raise NotFoundError("Subject not found")
        
        if name is not None:
            subject.name = name
        if description is not None:
            subject.description = description
        if grade_levels is not None:
            subject.grade_levels = grade_levels
        if status is not None:
            subject.status = status
        if supported_question_types is not None:
            subject.supported_question_types = supported_question_types
        if settings is not None:
            subject.settings = settings
        if metadata is not None:
            subject.extra_metadata = metadata
        
        self.db.commit()
        self.db.refresh(subject)
        
        return {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "name": subject.name,
            "updated_at": subject.updated_at,
        }
    
    def get_subject_statistics(self, subject_id: UUID) -> Dict[str, Any]:
        """Get subject statistics"""
        subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        
        if not subject:
            raise NotFoundError("Subject not found")
        
        # TODO: Calculate actual statistics from questions, sessions, etc.
        return {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "total_questions": 0,
            "total_sessions": 0,
            "total_students": 0,
            "average_score": 0.0,
            "questions_by_difficulty": {
                "beginner": 0,
                "intermediate": 0,
                "advanced": 0,
            },
        }

