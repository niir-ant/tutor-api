"""
Tenant Admin endpoints - updated for new model structure
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

from src.core.database import get_db
from src.core.dependencies import require_tenant_admin
from src.services.student import StudentService
from src.services.tutor import TutorService
from src.services.tenant import TenantService
from src.models.database import (
    StudentTutorAssignment, UserAccount, UserSubjectRole, 
    TenantAdminAccount
)
from src.models.user import AccountStatus, UserRole, AssignmentStatus
from datetime import datetime

router = APIRouter()


class CreateStudentRequest(BaseModel):
    username: str
    email: str
    grade_level: Optional[int] = None
    send_activation_email: bool = False


class CreateTutorRequest(BaseModel):
    username: str
    email: str
    name: Optional[str] = None
    send_activation_email: bool = False


class AssignStudentRequest(BaseModel):
    student_id: UUID
    tutor_id: UUID


class BulkAssignRequest(BaseModel):
    tutor_id: UUID
    student_ids: List[UUID]


@router.get("/accounts", status_code=status.HTTP_200_OK)
async def list_accounts(
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """List accounts within tenant (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    accounts = []
    
    if not role or role == "student":
        student_service = StudentService(db)
        result = student_service.list_students(tenant_id=tenant_id, status=status, search=search)
        accounts.extend(result["students"])
    
    if not role or role == "tutor":
        tutor_service = TutorService(db)
        result = tutor_service.list_tutors(tenant_id=tenant_id, status=status, search=search)
        accounts.extend(result["tutors"])
    
    return {
        "accounts": accounts,
        "total": len(accounts),
    }


@router.get("/accounts/{account_id}", status_code=status.HTTP_200_OK)
async def get_account(
    account_id: UUID,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Get account details (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    
    # Query user account
    user = db.query(UserAccount).filter(
        and_(
            UserAccount.user_id == account_id,
            UserAccount.tenant_id == tenant_id
        )
    ).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    # Determine role from subject roles
    subject_role = db.query(UserSubjectRole).filter(
        and_(
            UserSubjectRole.user_id == user.user_id,
            UserSubjectRole.status == AssignmentStatus.ACTIVE
        )
    ).first()
    
    # Check if tenant admin
    tenant_admin = db.query(TenantAdminAccount).filter(
        TenantAdminAccount.user_id == user.user_id
    ).first()
    
    if tenant_admin:
        role = "tenant_admin"
    elif subject_role:
        role = subject_role.role.value
    else:
        role = "unknown"
    
        return {
        "account_id": str(user.user_id),
        "username": user.username,
        "email": user.email,
        "role": role,
        "status": user.account_status.value,
        }


@router.put("/accounts/{account_id}/status", status_code=status.HTTP_200_OK)
async def update_account_status(
    account_id: UUID,
    status: str = Body(...),
    reason: Optional[str] = Body(None),
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Update account status (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    
    account = db.query(UserAccount).filter(
        and_(
            UserAccount.user_id == account_id,
            UserAccount.tenant_id == tenant_id
        )
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
        account.account_status = AccountStatus(status)
        db.commit()
    return {"account_id": str(account_id), "status": status}


@router.post("/students", status_code=status.HTTP_201_CREATED)
async def create_student(
    request: CreateStudentRequest,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Create student account (tenant admin only)"""
    student_service = StudentService(db)
    tenant_id = UUID(current_user["tenant_id"])
    created_by = UUID(current_user["user_id"])
    
    result = student_service.create_student(
        tenant_id=tenant_id,
        username=request.username,
        email=request.email,
        grade_level=request.grade_level,
        created_by=created_by,
        send_activation_email=request.send_activation_email,
    )
    
    return result


@router.post("/tutors", status_code=status.HTTP_201_CREATED)
async def create_tutor(
    request: CreateTutorRequest,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Create tutor account (tenant admin only)"""
    tutor_service = TutorService(db)
    tenant_id = UUID(current_user["tenant_id"])
    created_by = UUID(current_user["user_id"])
    
    result = tutor_service.create_tutor(
        tenant_id=tenant_id,
        username=request.username,
        email=request.email,
        name=request.name,
        created_by=created_by,
        send_activation_email=request.send_activation_email,
    )
    
    return result


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
async def assign_student_to_tutor(
    request: AssignStudentRequest,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Assign student to tutor (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    assigned_by = UUID(current_user["user_id"])
    
    # Verify student and tutor exist and are in the same tenant
    student = db.query(UserAccount).filter(
        and_(
            UserAccount.user_id == request.student_id,
            UserAccount.tenant_id == tenant_id
        )
    ).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    tutor = db.query(UserAccount).filter(
        and_(
            UserAccount.user_id == request.tutor_id,
            UserAccount.tenant_id == tenant_id
        )
    ).first()
    
    if not tutor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")
    
    # Check if assignment already exists
    existing = db.query(StudentTutorAssignment).filter(
        and_(
        StudentTutorAssignment.student_id == request.student_id,
        StudentTutorAssignment.tutor_id == request.tutor_id,
        StudentTutorAssignment.tenant_id == tenant_id,
            StudentTutorAssignment.status == AssignmentStatus.ACTIVE
        )
    ).first()
    
    if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment already exists")
    
    # Create assignment (need subject_id - for now use first subject)
    # TODO: Make subject_id required or get from request
    from src.models.database import Subject
    subject = db.query(Subject).filter(Subject.status == "active").first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active subjects found")
    
    assignment = StudentTutorAssignment(
        tenant_id=tenant_id,
        subject_id=subject.subject_id,
        student_id=request.student_id,
        tutor_id=request.tutor_id,
        status=AssignmentStatus.ACTIVE,
        assigned_by=assigned_by,
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return {
        "assignment_id": str(assignment.assignment_id),
        "student_id": str(request.student_id),
        "tutor_id": str(request.tutor_id),
        "status": assignment.status.value,
        "assigned_at": assignment.assigned_at,
    }


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_200_OK)
async def remove_assignment(
    assignment_id: UUID,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Remove student-tutor assignment (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    
    assignment = db.query(StudentTutorAssignment).filter(
        and_(
        StudentTutorAssignment.assignment_id == assignment_id,
            StudentTutorAssignment.tenant_id == tenant_id
        )
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    
    assignment.status = AssignmentStatus.INACTIVE
    assignment.deactivated_at = datetime.utcnow()
    assignment.deactivated_by = UUID(current_user["user_id"])
    
    db.commit()
    
    return {
        "assignment_id": str(assignment_id),
        "status": "deactivated",
    }


@router.post("/assignments/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_assign_students(
    request: BulkAssignRequest,
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Bulk assign students to tutor (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    assigned_by = UUID(current_user["user_id"])
    
    # Get first active subject (TODO: Make subject_id required)
    from src.models.database import Subject
    subject = db.query(Subject).filter(Subject.status == "active").first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active subjects found")
    
    assignments = []
    errors = []
    
    for student_id in request.student_ids:
        # Check if assignment already exists
        existing = db.query(StudentTutorAssignment).filter(
            and_(
                StudentTutorAssignment.student_id == student_id,
                StudentTutorAssignment.tutor_id == request.tutor_id,
                StudentTutorAssignment.tenant_id == tenant_id,
                StudentTutorAssignment.status == AssignmentStatus.ACTIVE
            )
        ).first()
        
        if existing:
            errors.append(f"Assignment already exists for student {student_id}")
            continue
        
        assignment = StudentTutorAssignment(
            tenant_id=tenant_id,
            subject_id=subject.subject_id,
            student_id=student_id,
            tutor_id=request.tutor_id,
            status=AssignmentStatus.ACTIVE,
            assigned_by=assigned_by,
        )
        db.add(assignment)
        assignments.append(assignment)
    
    db.commit()
    
    return {
        "created": len(assignments),
        "errors": errors,
        "assignments": [
            {
                "assignment_id": str(a.assignment_id),
                "student_id": str(a.student_id),
                "tutor_id": str(a.tutor_id),
            }
            for a in assignments
        ],
    }


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_statistics(
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Get tenant statistics (tenant admin only)"""
    tenant_id = UUID(current_user["tenant_id"])
    tenant_service = TenantService(db)
    stats = tenant_service.get_tenant_statistics(tenant_id)
    return stats
