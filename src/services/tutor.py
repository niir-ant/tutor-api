"""
Tutor service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy import func

from src.models.database import TutorAccount, StudentTutorAssignment, StudentAccount, AnswerSubmission
from src.core.exceptions import NotFoundError, BadRequestError
from src.core.security import get_password_hash
from src.models.user import AccountStatus


class TutorService:
    """Tutor service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tutor(
        self,
        tenant_id: UUID,
        username: str,
        email: str,
        name: Optional[str] = None,
        created_by: UUID = None,
        send_activation_email: bool = False,
    ) -> Dict[str, Any]:
        """Create a new tutor account"""
        # Check if username or email already exists
        existing = self.db.query(TutorAccount).filter(
            (TutorAccount.username == username) | (TutorAccount.email == email),
        ).first()
        
        if existing:
            raise BadRequestError("Username or email already exists")
        
        # Generate temporary password
        import secrets
        temp_password = secrets.token_urlsafe(12)
        password_hash = get_password_hash(temp_password)
        
        tutor = TutorAccount(
            tenant_id=tenant_id,
            username=username,
            email=email,
            password_hash=password_hash,
            name=name,
            account_status=AccountStatus.PENDING_ACTIVATION,
            requires_password_change=True,
        )
        
        self.db.add(tutor)
        self.db.commit()
        self.db.refresh(tutor)
        
        # TODO: Send activation email if requested
        
        result = {
            "tutor_id": tutor.tutor_id,
            "username": tutor.username,
            "email": tutor.email,
            "status": tutor.account_status.value,
            "created_at": tutor.created_at,
        }
        
        if not send_activation_email:
            result["temporary_password"] = temp_password
        
        return result
    
    def get_tutor(self, tutor_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get tutor details"""
        query = self.db.query(TutorAccount).filter(TutorAccount.tutor_id == tutor_id)
        
        if tenant_id:
            query = query.filter(TutorAccount.tenant_id == tenant_id)
        
        tutor = query.first()
        if not tutor:
            raise NotFoundError("Tutor not found")
        
        return {
            "tutor_id": tutor.tutor_id,
            "username": tutor.username,
            "email": tutor.email,
            "name": tutor.name,
            "status": tutor.account_status.value,
            "profile": tutor.profile,
            "created_at": tutor.created_at,
            "last_login": tutor.last_login,
        }
    
    def list_tutors(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List tutors"""
        query = self.db.query(TutorAccount).filter(TutorAccount.tenant_id == tenant_id)
        
        if status:
            query = query.filter(TutorAccount.account_status == AccountStatus(status))
        
        if search:
            query = query.filter(
                (TutorAccount.username.ilike(f"%{search}%")) |
                (TutorAccount.email.ilike(f"%{search}%")) |
                (TutorAccount.name.ilike(f"%{search}%"))
            )
        
        tutors = query.order_by(TutorAccount.created_at.desc()).all()
        
        result = []
        for tutor in tutors:
            # Get student count
            student_count = self.db.query(StudentTutorAssignment).filter(
                StudentTutorAssignment.tutor_id == tutor.tutor_id,
                StudentTutorAssignment.status == "active",
            ).count()
            
            result.append({
                "tutor_id": tutor.tutor_id,
                "username": tutor.username,
                "email": tutor.email,
                "name": tutor.name,
                "status": tutor.account_status.value,
                "student_count": student_count,
                "created_at": tutor.created_at,
            })
        
        return {
            "tutors": result,
            "total": len(result),
        }
    
    def get_tutor_students(self, tutor_id: UUID, tenant_id: UUID) -> Dict[str, Any]:
        """Get students assigned to a tutor"""
        tutor = self.db.query(TutorAccount).filter(
            TutorAccount.tutor_id == tutor_id,
            TutorAccount.tenant_id == tenant_id,
        ).first()
        
        if not tutor:
            raise NotFoundError("Tutor not found")
        
        assignments = self.db.query(StudentTutorAssignment).filter(
            StudentTutorAssignment.tutor_id == tutor_id,
            StudentTutorAssignment.tenant_id == tenant_id,
            StudentTutorAssignment.status == "active",
        ).all()
        
        students = []
        for assignment in assignments:
            student = self.db.query(StudentAccount).filter(
                StudentAccount.student_id == assignment.student_id,
            ).first()
            
            if student:
                # Get progress summary
                total_questions = self.db.query(func.count(AnswerSubmission.submission_id)).filter(
                    AnswerSubmission.student_id == student.student_id,
                    AnswerSubmission.tenant_id == tenant_id,
                ).scalar() or 0
                
                correct_answers = self.db.query(func.count(AnswerSubmission.submission_id)).filter(
                    AnswerSubmission.student_id == student.student_id,
                    AnswerSubmission.tenant_id == tenant_id,
                    AnswerSubmission.is_correct == True,
                ).scalar() or 0
                
                accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
                
                students.append({
                    "student_id": student.student_id,
                    "username": student.username,
                    "name": student.username,
                    "email": student.email,
                    "grade_level": student.grade_level,
                    "assigned_at": assignment.assigned_at,
                    "progress_summary": {
                        "total_questions": total_questions,
                        "accuracy": accuracy,
                        "average_score": 0.0,  # TODO: Calculate actual average
                    },
                })
        
        return {
            "tutor_id": tutor_id,
            "students": students,
            "total": len(students),
        }
    
    def get_student_progress(
        self,
        tutor_id: UUID,
        student_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get student progress (tutor view)"""
        # Verify assignment
        assignment = self.db.query(StudentTutorAssignment).filter(
            StudentTutorAssignment.tutor_id == tutor_id,
            StudentTutorAssignment.student_id == student_id,
            StudentTutorAssignment.tenant_id == tenant_id,
            StudentTutorAssignment.status == "active",
        ).first()
        
        if not assignment:
            raise NotFoundError("Student not assigned to this tutor")
        
        student = self.db.query(StudentAccount).filter(
            StudentAccount.student_id == student_id,
        ).first()
        
        if not student:
            raise NotFoundError("Student not found")
        
        # Get progress data
        from src.services.progress import ProgressService
        progress_service = ProgressService(self.db)
        progress = progress_service.get_student_progress(student_id, tenant_id)
        
        return {
            "student_id": student_id,
            "student_name": student.username,
            **progress,
        }

