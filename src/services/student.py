"""
Student service - updated for new model structure
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from src.models.database import (
    UserAccount, UserSubjectRole, StudentSubjectProfile, StudentTutorAssignment, Subject
)
from src.core.exceptions import NotFoundError, BadRequestError
from src.core.security import get_password_hash
from src.models.user import AccountStatus, UserRole, AssignmentStatus, SubjectStatus, SubjectType, ValidationMethod, QuestionType


class StudentService:
    """Student service"""
    
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
    
    def create_student(
        self,
        tenant_id: UUID,
        username: str,
        email: str,
        grade_level: Optional[int] = None,
        created_by: UUID = None,
        send_activation_email: bool = False,
    ) -> Dict[str, Any]:
        """Create a new student account"""
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
            name=username,  # Default name to username for students
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
            role=UserRole.STUDENT,
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
    
    def get_student(self, student_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get student details"""
        query = self.db.query(UserAccount).filter(UserAccount.user_id == student_id)
        
        if tenant_id:
            query = query.filter(UserAccount.tenant_id == tenant_id)
        
        user = query.first()
        if not user:
            raise NotFoundError("Student not found")
        
        # Verify user has student role (check subject roles)
        has_student_role = self.db.query(UserSubjectRole).filter(
            and_(
                UserSubjectRole.user_id == user.user_id,
                UserSubjectRole.role == UserRole.STUDENT,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).first()
        
        if not has_student_role:
            raise NotFoundError("User is not a student")
        
        # Get grade level from student profile
        profile = self.db.query(StudentSubjectProfile).filter(
            StudentSubjectProfile.user_id == user.user_id
        ).first()
        
        grade_level = profile.grade_level if profile else None
        
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name or user.username,  # Use name from user_accounts
            "grade_level": grade_level,
            "account_status": user.account_status.value,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "requires_password_change": user.requires_password_change,
        }
    
    def list_students(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List students"""
        # Find all users with student role in this tenant
        student_role_ids = self.db.query(UserSubjectRole.user_id).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.STUDENT,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).distinct().subquery()
        
        query = self.db.query(UserAccount).filter(
            and_(
                UserAccount.tenant_id == tenant_id,
                UserAccount.user_id.in_(self.db.query(student_role_ids.c.user_id))
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
            # Get grade level from profile
            profile = self.db.query(StudentSubjectProfile).filter(
                StudentSubjectProfile.user_id == user.user_id
            ).first()
            
            result.append({
                "user_id": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "name": user.name or user.username,  # Include name from user_accounts
                "grade_level": profile.grade_level if profile else None,
                "account_status": user.account_status.value,
                "created_at": user.created_at,
            })
        
        return {
            "students": result,
            "total": len(result),
        }
