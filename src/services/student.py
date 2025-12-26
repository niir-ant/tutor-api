"""
Student service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from src.models.database import StudentAccount, StudentTutorAssignment
from src.core.exceptions import NotFoundError, BadRequestError
from src.core.security import get_password_hash
from src.models.user import AccountStatus


class StudentService:
    """Student service"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        # Check if username or email already exists
        existing = self.db.query(StudentAccount).filter(
            (StudentAccount.username == username) | (StudentAccount.email == email),
        ).first()
        
        if existing:
            raise BadRequestError("Username or email already exists")
        
        # Generate temporary password
        import secrets
        temp_password = secrets.token_urlsafe(12)
        password_hash = get_password_hash(temp_password)
        
        student = StudentAccount(
            tenant_id=tenant_id,
            username=username,
            email=email,
            password_hash=password_hash,
            grade_level=grade_level,
            account_status=AccountStatus.PENDING_ACTIVATION,
            requires_password_change=True,
        )
        
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        
        # TODO: Send activation email if requested
        
        result = {
            "student_id": student.student_id,
            "username": student.username,
            "email": student.email,
            "status": student.account_status.value,
            "created_at": student.created_at,
        }
        
        if not send_activation_email:
            result["temporary_password"] = temp_password
        
        return result
    
    def get_student(self, student_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get student details"""
        query = self.db.query(StudentAccount).filter(StudentAccount.student_id == student_id)
        
        if tenant_id:
            query = query.filter(StudentAccount.tenant_id == tenant_id)
        
        student = query.first()
        if not student:
            raise NotFoundError("Student not found")
        
        return {
            "student_id": student.student_id,
            "username": student.username,
            "email": student.email,
            "grade_level": student.grade_level,
            "account_status": student.account_status.value,
            "created_at": student.created_at,
            "last_login": student.last_login,
            "requires_password_change": student.requires_password_change,
        }
    
    def list_students(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List students"""
        query = self.db.query(StudentAccount).filter(StudentAccount.tenant_id == tenant_id)
        
        if status:
            query = query.filter(StudentAccount.account_status == AccountStatus(status))
        
        if search:
            query = query.filter(
                (StudentAccount.username.ilike(f"%{search}%")) |
                (StudentAccount.email.ilike(f"%{search}%"))
            )
        
        students = query.order_by(StudentAccount.created_at.desc()).all()
        
        result = []
        for student in students:
            result.append({
                "student_id": student.student_id,
                "username": student.username,
                "email": student.email,
                "grade_level": student.grade_level,
                "account_status": student.account_status.value,
                "created_at": student.created_at,
            })
        
        return {
            "students": result,
            "total": len(result),
        }

