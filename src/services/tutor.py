"""
Tutor service - updated for new model structure
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, Dict, Any, List
from uuid import UUID

from src.models.database import (
    UserAccount, UserSubjectRole, TutorSubjectProfile, 
    StudentTutorAssignment, AnswerSubmission, Subject
)
from src.core.exceptions import NotFoundError, BadRequestError
from src.core.security import get_password_hash
from src.models.user import AccountStatus, UserRole, AssignmentStatus, SubjectStatus, SubjectType, ValidationMethod, QuestionType


class TutorService:
    """Tutor service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _get_or_create_default_subject(self, created_by: Optional[UUID] = None) -> Subject:
        """Get or create the default subject for the system"""
        # Check if default subject exists
        default_subject = self.db.query(Subject).filter(
            Subject.subject_code == "default"
        ).first()
        
        if not default_subject:
            # Create default subject
            default_subject = Subject(
                subject_code="default",
                name="Default Subject",
                description="Default subject created automatically for new users",
                type=SubjectType.OTHER,
                status=SubjectStatus.ACTIVE,
                supported_question_types=[QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER, QuestionType.TRUE_FALSE],
                answer_validation_method=ValidationMethod.EXACT_MATCH,
                grade_levels=None,  # Support all grade levels
                created_by=created_by,
            )
            self.db.add(default_subject)
            self.db.flush()  # Flush to get subject_id
        
        return default_subject
    
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
        # Check if username or email already exists in this tenant
        existing = self.db.query(UserAccount).filter(
            and_(
                or_(
                    UserAccount.username == username,
                    UserAccount.email == email
                ),
                UserAccount.tenant_id == tenant_id
            )
        ).first()
        
        if existing:
            raise BadRequestError("Username or email already exists in this tenant")
        
        # Generate temporary password
        import secrets
        temp_password = secrets.token_urlsafe(12)
        password_hash = get_password_hash(temp_password)
        
        # Create user account
        user = UserAccount(
            tenant_id=tenant_id,
            username=username,
            email=email,
            password_hash=password_hash,
            name=name or username,  # Use provided name or default to username
            account_status=AccountStatus.PENDING_ACTIVATION,
            requires_password_change=True,
            created_by=created_by,
        )
        
        self.db.add(user)
        self.db.flush()  # Flush to get user_id
        
        # Get or create default subject and assign user to it
        subject = self._get_or_create_default_subject(created_by=created_by)
        subject_role = UserSubjectRole(
            user_id=user.user_id,
            tenant_id=tenant_id,
            subject_id=subject.subject_id,
            role=UserRole.TUTOR,
            status=AssignmentStatus.ACTIVE,
            assigned_by=created_by if created_by else user.user_id,  # Use user_id as fallback
        )
        self.db.add(subject_role)
        
        # TODO: Send activation email if requested
        
        # Commit the transaction to save the user and role
        self.db.commit()
        self.db.refresh(user)  # Refresh to get created_at timestamp
        
        result = {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "status": user.account_status.value,
            "created_at": user.created_at,
        }
        
        if not send_activation_email:
            result["temporary_password"] = temp_password
        
        return result
    
    def get_tutor(self, tutor_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get tutor details"""
        query = self.db.query(UserAccount).filter(UserAccount.user_id == tutor_id)
        
        if tenant_id:
            query = query.filter(UserAccount.tenant_id == tenant_id)
        
        user = query.first()
        if not user:
            raise NotFoundError("Tutor not found")
        
        # Verify user has tutor role (check subject roles)
        has_tutor_role = self.db.query(UserSubjectRole).filter(
            and_(
                UserSubjectRole.user_id == user.user_id,
                UserSubjectRole.role == UserRole.TUTOR,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).first()
        
        if not has_tutor_role:
            raise NotFoundError("User is not a tutor")
        
        # Get tutor profile (for profile data, not name anymore)
        profile = self.db.query(TutorSubjectProfile).filter(
            TutorSubjectProfile.user_id == user.user_id
        ).first()
        
        profile_data = profile.profile if profile else None
        
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name or user.username,  # Use name from user_accounts
            "status": user.account_status.value,
            "profile": profile_data,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    
    def list_tutors(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List tutors"""
        # Find all users with tutor role in this tenant
        tutor_role_ids = self.db.query(UserSubjectRole.user_id).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.TUTOR,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).distinct().subquery()
        
        query = self.db.query(UserAccount).filter(
            and_(
                UserAccount.tenant_id == tenant_id,
                UserAccount.user_id.in_(self.db.query(tutor_role_ids.c.user_id))
            )
        )
        
        if status:
            query = query.filter(UserAccount.account_status == AccountStatus(status))
        
        if search:
            query = query.filter(
                or_(
                    UserAccount.username.ilike(f"%{search}%"),
                    UserAccount.email.ilike(f"%{search}%"),
                    UserAccount.name.ilike(f"%{search}%")
                )
            )
        
        users = query.order_by(UserAccount.created_at.desc()).all()
        
        result = []
        for user in users:
            # Get student count
            student_count = self.db.query(StudentTutorAssignment).filter(
                and_(
                    StudentTutorAssignment.tutor_id == user.user_id,
                    StudentTutorAssignment.status == AssignmentStatus.ACTIVE
                )
            ).count()
            
            result.append({
                "user_id": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "name": user.name or user.username,  # Use name from user_accounts
                "status": user.account_status.value,
                "student_count": student_count,
                "created_at": user.created_at,
            })
        
        return {
            "tutors": result,
            "total": len(result),
        }
    
    def get_tutor_students(self, tutor_id: UUID, tenant_id: UUID) -> Dict[str, Any]:
        """Get students assigned to a tutor"""
        # Verify tutor exists and has tutor role
        tutor = self.db.query(UserAccount).filter(
            and_(
                UserAccount.user_id == tutor_id,
                UserAccount.tenant_id == tenant_id
            )
        ).first()
        
        if not tutor:
            raise NotFoundError("Tutor not found")
        
        has_tutor_role = self.db.query(UserSubjectRole).filter(
            and_(
                UserSubjectRole.user_id == tutor_id,
                UserSubjectRole.role == UserRole.TUTOR,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).first()
        
        if not has_tutor_role:
            raise NotFoundError("User is not a tutor")
        
        assignments = self.db.query(StudentTutorAssignment).filter(
            and_(
            StudentTutorAssignment.tutor_id == tutor_id,
            StudentTutorAssignment.tenant_id == tenant_id,
                StudentTutorAssignment.status == AssignmentStatus.ACTIVE
            )
        ).all()
        
        students = []
        for assignment in assignments:
            student = self.db.query(UserAccount).filter(
                UserAccount.user_id == assignment.student_id
            ).first()
            
            if student:
                # Get progress summary
                total_questions = self.db.query(func.count(AnswerSubmission.submission_id)).filter(
                    and_(
                        AnswerSubmission.student_id == student.user_id,
                        AnswerSubmission.tenant_id == tenant_id
                    )
                ).scalar() or 0
                
                correct_answers = self.db.query(func.count(AnswerSubmission.submission_id)).filter(
                    and_(
                        AnswerSubmission.student_id == student.user_id,
                    AnswerSubmission.tenant_id == tenant_id,
                        AnswerSubmission.is_correct == True
                    )
                ).scalar() or 0
                
                accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
                
                # Get grade level
                from src.models.database import StudentSubjectProfile
                profile = self.db.query(StudentSubjectProfile).filter(
                    StudentSubjectProfile.user_id == student.user_id
                ).first()
                
                students.append({
                    "user_id": str(student.user_id),
                    "username": student.username,
                    "name": student.name or student.username,  # Use name from user_accounts
                    "email": student.email,
                    "grade_level": profile.grade_level if profile else None,
                    "assigned_at": assignment.assigned_at,
                    "progress_summary": {
                        "total_questions": total_questions,
                        "accuracy": accuracy,
                        "average_score": 0.0,  # TODO: Calculate actual average
                    },
                })
        
        return {
            "tutor_id": str(tutor_id),
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
            and_(
            StudentTutorAssignment.tutor_id == tutor_id,
            StudentTutorAssignment.student_id == student_id,
            StudentTutorAssignment.tenant_id == tenant_id,
                StudentTutorAssignment.status == AssignmentStatus.ACTIVE
            )
        ).first()
        
        if not assignment:
            raise NotFoundError("Student not assigned to this tutor")
        
        student = self.db.query(UserAccount).filter(
            UserAccount.user_id == student_id
        ).first()
        
        if not student:
            raise NotFoundError("Student not found")
        
        # Get progress data
        from src.services.progress import ProgressService
        progress_service = ProgressService(self.db)
        progress = progress_service.get_student_progress(student_id, tenant_id)
        
        return {
            "student_id": str(student_id),
            "student_name": student.name or student.username,  # Use name from user_accounts
            **progress,
        }
