"""
System Admin endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import require_system_admin
from src.schemas.tenant import (
    TenantListResponse,
    TenantDetailResponse,
    CreateTenantRequest,
    UpdateTenantRequest,
    TenantStatusRequest,
    AddDomainRequest,
    AddDomainResponse,
    TenantStatisticsResponse,
)
from src.services.tenant import TenantService
from src.services.student import StudentService
from src.services.tutor import TutorService
from src.models.database import AdministratorAccount, StudentAccount, TutorAccount
from src.core.security import get_password_hash
from src.models.user import UserRole, AccountStatus

router = APIRouter()


@router.get("/tenants", response_model=TenantListResponse, status_code=status.HTTP_200_OK)
async def list_tenants(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """List all tenants (system admin only)"""
    tenant_service = TenantService(db)
    result = tenant_service.list_tenants(status=status, search=search)
    return TenantListResponse(**result)


@router.post("/tenants", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: CreateTenantRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Create tenant (system admin only)"""
    tenant_service = TenantService(db)
    created_by = UUID(current_user["user_id"])
    
    result = tenant_service.create_tenant(
        tenant_code=request.tenant_code,
        name=request.name,
        description=request.description,
        domains=request.domains,
        primary_domain=request.primary_domain,
        contact_info=request.contact_info.dict() if hasattr(request.contact_info, 'dict') else request.contact_info,
        settings=request.settings.dict() if hasattr(request.settings, 'dict') else request.settings,
        created_by=created_by,
    )
    
    return result


@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse, status_code=status.HTTP_200_OK)
async def get_tenant(
    tenant_id: UUID,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get tenant details (system admin only)"""
    tenant_service = TenantService(db)
    result = tenant_service.get_tenant(tenant_id)
    return TenantDetailResponse(**result)


@router.put("/tenants/{tenant_id}", status_code=status.HTTP_200_OK)
async def update_tenant(
    tenant_id: UUID,
    request: UpdateTenantRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Update tenant (system admin only)"""
    # TODO: Implement update logic
    return {"message": "Update not yet implemented"}


@router.put("/tenants/{tenant_id}/status", status_code=status.HTTP_200_OK)
async def update_tenant_status(
    tenant_id: UUID,
    request: TenantStatusRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Update tenant status (system admin only)"""
    tenant_service = TenantService(db)
    result = tenant_service.update_tenant_status(tenant_id, request.status, request.reason)
    return result


@router.get("/tenants/{tenant_id}/statistics", response_model=TenantStatisticsResponse, status_code=status.HTTP_200_OK)
async def get_tenant_statistics(
    tenant_id: UUID,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get tenant statistics (system admin only)"""
    tenant_service = TenantService(db)
    result = tenant_service.get_tenant_statistics(tenant_id)
    return TenantStatisticsResponse(**result)


@router.post("/tenants/{tenant_id}/domains", response_model=AddDomainResponse, status_code=status.HTTP_201_CREATED)
async def add_domain(
    tenant_id: UUID,
    request: AddDomainRequest,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Add domain to tenant (system admin only)"""
    tenant_service = TenantService(db)
    result = tenant_service.add_domain(tenant_id, request.domain, request.is_primary)
    return AddDomainResponse(**result)


@router.post("/tenants/{tenant_id}/admins", status_code=status.HTTP_201_CREATED)
async def create_tenant_admin(
    tenant_id: UUID,
    username: str,
    email: str,
    name: Optional[str] = None,
    send_activation_email: bool = False,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Create tenant admin account (system admin only)"""
    # Check if username or email already exists
    existing = db.query(AdministratorAccount).filter(
        (AdministratorAccount.username == username) | (AdministratorAccount.email == email),
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    # Generate temporary password
    import secrets
    temp_password = secrets.token_urlsafe(12)
    password_hash = get_password_hash(temp_password)
    
    admin = AdministratorAccount(
        tenant_id=tenant_id,
        username=username,
        email=email,
        password_hash=password_hash,
        name=name,
        role=UserRole.TENANT_ADMIN,
        account_status=AccountStatus.PENDING_ACTIVATION,
        requires_password_change=True,
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    result = {
        "admin_id": admin.admin_id,
        "tenant_id": tenant_id,
        "username": admin.username,
        "email": admin.email,
        "role": admin.role.value,
        "status": admin.account_status.value,
        "created_at": admin.created_at,
    }
    
    if not send_activation_email:
        result["temporary_password"] = temp_password
    
    return result


@router.get("/accounts", status_code=status.HTTP_200_OK)
async def list_accounts(
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """List all accounts (system admin only)"""
    accounts = []
    
    # Get students
    if not role or role == "student":
        query = db.query(StudentAccount)
        if status:
            query = query.filter(StudentAccount.account_status == AccountStatus(status))
        if search:
            query = query.filter(
                (StudentAccount.username.ilike(f"%{search}%")) |
                (StudentAccount.email.ilike(f"%{search}%"))
            )
        students = query.all()
        for student in students:
            accounts.append({
                "account_id": student.student_id,
                "username": student.username,
                "email": student.email,
                "name": student.username,
                "role": "student",
                "status": student.account_status.value,
                "created_at": student.created_at,
                "last_login": student.last_login,
            })
    
    # Get tutors
    if not role or role == "tutor":
        query = db.query(TutorAccount)
        if status:
            query = query.filter(TutorAccount.account_status == AccountStatus(status))
        if search:
            query = query.filter(
                (TutorAccount.username.ilike(f"%{search}%")) |
                (TutorAccount.email.ilike(f"%{search}%")) |
                (TutorAccount.name.ilike(f"%{search}%"))
            )
        tutors = query.all()
        for tutor in tutors:
            accounts.append({
                "account_id": tutor.tutor_id,
                "username": tutor.username,
                "email": tutor.email,
                "name": tutor.name or tutor.username,
                "role": "tutor",
                "status": tutor.account_status.value,
                "created_at": tutor.created_at,
                "last_login": tutor.last_login,
            })
    
    # Get admins
    if not role or role == "admin":
        query = db.query(AdministratorAccount)
        if status:
            query = query.filter(AdministratorAccount.account_status == AccountStatus(status))
        if search:
            query = query.filter(
                (AdministratorAccount.username.ilike(f"%{search}%")) |
                (AdministratorAccount.email.ilike(f"%{search}%")) |
                (AdministratorAccount.name.ilike(f"%{search}%"))
            )
        admins = query.all()
        for admin in admins:
            accounts.append({
                "account_id": admin.admin_id,
                "username": admin.username,
                "email": admin.email,
                "name": admin.name or admin.username,
                "role": admin.role.value,
                "status": admin.account_status.value,
                "created_at": admin.created_at,
                "last_login": admin.last_login,
            })
    
    return {
        "accounts": accounts,
        "total": len(accounts),
    }


@router.put("/accounts/{account_id}/status", status_code=status.HTTP_200_OK)
async def update_account_status(
    account_id: UUID,
    status: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Update account status (system admin only)"""
    # Try to find account in different tables
    account = db.query(StudentAccount).filter(StudentAccount.student_id == account_id).first()
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": account_id, "status": status, "updated_at": account.updated_at}
    
    account = db.query(TutorAccount).filter(TutorAccount.tutor_id == account_id).first()
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": account_id, "status": status, "updated_at": account.updated_at}
    
    account = db.query(AdministratorAccount).filter(AdministratorAccount.admin_id == account_id).first()
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": account_id, "status": status, "updated_at": account.updated_at}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_system_statistics(
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get system-wide statistics (system admin only)"""
    from sqlalchemy import func
    
    total_students = db.query(func.count(StudentAccount.student_id)).scalar() or 0
    total_tutors = db.query(func.count(TutorAccount.tutor_id)).scalar() or 0
    total_admins = db.query(func.count(AdministratorAccount.admin_id)).scalar() or 0
    
    return {
        "users": {
            "total_students": total_students,
            "total_tutors": total_tutors,
            "total_admins": total_admins,
            "active_accounts": 0,  # TODO: Calculate
            "inactive_accounts": 0,  # TODO: Calculate
        },
        "subjects": {
            "total": 0,  # TODO: Calculate
            "active": 0,
            "inactive": 0,
        },
        "activity": {
            "total_sessions": 0,
            "total_questions": 0,
            "total_messages": 0,
            "active_sessions": 0,
        },
    }
