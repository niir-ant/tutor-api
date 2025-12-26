"""
Tenant Admin endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

from src.core.database import get_db
from src.core.dependencies import require_tenant_admin
from src.services.student import StudentService
from src.services.tutor import TutorService
from src.services.tenant import TenantService
from src.models.database import StudentTutorAssignment, StudentAccount, TutorAccount
from src.models.user import AccountStatus
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
    
    # Try student
    student = db.query(StudentAccount).filter(
        StudentAccount.student_id == account_id,
        StudentAccount.tenant_id == tenant_id,
    ).first()
    if student:
        return {
            "account_id": student.student_id,
            "username": student.username,
            "email": student.email,
            "role": "student",
            "status": student.account_status.value,
        }
    
    # Try tutor
    tutor = db.query(TutorAccount).filter(
        TutorAccount.tutor_id == account_id,
        TutorAccount.tenant_id == tenant_id,
    ).first()
    if tutor:
        return {
            "account_id": tutor.tutor_id,
            "username": tutor.username,
            "email": tutor.email,
            "role": "tutor",
            "status": tutor.account_status.value,
        }
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


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
    
    account = db.query(StudentAccount).filter(
        StudentAccount.student_id == account_id,
        StudentAccount.tenant_id == tenant_id,
    ).first()
    
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": account_id, "status": status}
    
    account = db.query(TutorAccount).filter(
        TutorAccount.tutor_id == account_id,
        TutorAccount.tenant_id == tenant_id,
    ).first()
    
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": account_id, "status": status}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


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
    
    # Verify student and tutor belong to tenant
    student = db.query(StudentAccount).filter(
        StudentAccount.student_id == request.student_id,
        StudentAccount.tenant_id == tenant_id,
    ).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    tutor = db.query(TutorAccount).filter(
        TutorAccount.tutor_id == request.tutor_id,
        TutorAccount.tenant_id == tenant_id,
    ).first()
    
    if not tutor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")
    
    # Check if assignment already exists
    existing = db.query(StudentTutorAssignment).filter(
        StudentTutorAssignment.student_id == request.student_id,
        StudentTutorAssignment.tutor_id == request.tutor_id,
        StudentTutorAssignment.tenant_id == tenant_id,
    ).first()
    
    if existing:
        if existing.status == "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment already exists")
        else:
            existing.status = "active"
            db.commit()
            return {"assignment_id": existing.assignment_id, "status": "active"}
    
    # Create assignment
    assignment = StudentTutorAssignment(
        tenant_id=tenant_id,
        student_id=request.student_id,
        tutor_id=request.tutor_id,
        status="active",
        assigned_by=assigned_by,
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return {
        "assignment_id": assignment.assignment_id,
        "student_id": request.student_id,
        "tutor_id": request.tutor_id,
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
        StudentTutorAssignment.assignment_id == assignment_id,
        StudentTutorAssignment.tenant_id == tenant_id,
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    
    assignment.status = "inactive"
    assignment.deactivated_at = datetime.utcnow()
    assignment.deactivated_by = UUID(current_user["user_id"])
    
    db.commit()
    
    return {
        "assignment_id": assignment_id,
        "status": "removed",
        "removed_at": assignment.deactivated_at,
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
    
    assignments = []
    failed = []
    
    for student_id in request.student_ids:
        try:
            # Verify student belongs to tenant
            student = db.query(StudentAccount).filter(
                StudentAccount.student_id == student_id,
                StudentAccount.tenant_id == tenant_id,
            ).first()
            
            if not student:
                failed.append({"student_id": student_id, "reason": "Student not found"})
                continue
            
            # Check if assignment exists
            existing = db.query(StudentTutorAssignment).filter(
                StudentTutorAssignment.student_id == student_id,
                StudentTutorAssignment.tutor_id == request.tutor_id,
                StudentTutorAssignment.tenant_id == tenant_id,
            ).first()
            
            if existing:
                if existing.status == "active":
                    failed.append({"student_id": student_id, "reason": "Already assigned"})
                    continue
                else:
                    existing.status = "active"
                    assignments.append(existing)
                    continue
            
            assignment = StudentTutorAssignment(
                tenant_id=tenant_id,
                student_id=student_id,
                tutor_id=request.tutor_id,
                status="active",
                assigned_by=assigned_by,
            )
            db.add(assignment)
            assignments.append(assignment)
        except Exception as e:
            failed.append({"student_id": student_id, "reason": str(e)})
    
    db.commit()
    
    return {
        "tutor_id": request.tutor_id,
        "assigned_count": len(assignments),
        "failed_assignments": failed,
        "assignments": [{"assignment_id": a.assignment_id, "student_id": a.student_id} for a in assignments],
    }


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_tenant_statistics(
    current_user: dict = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
):
    """Get tenant statistics (tenant admin only)"""
    tenant_service = TenantService(db)
    tenant_id = UUID(current_user["tenant_id"])
    
    result = tenant_service.get_tenant_statistics(tenant_id)
    return result
