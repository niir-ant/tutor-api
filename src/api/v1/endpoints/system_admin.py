"""
System Admin endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from uuid import UUID
from typing import Optional, Any, Dict

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
from src.models.database import (
    SystemAdminAccount, TenantAdminAccount, UserAccount, 
    UserSubjectRole, QuizSession
)
from src.core.security import get_password_hash
from src.models.user import UserRole, AccountStatus, AssignmentStatus

router = APIRouter()


def _pydantic_to_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """Convert Pydantic model to dict, handling both v1 and v2"""
    if obj is None:
        return None
    # Pydantic v2 uses model_dump()
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    # Pydantic v1 uses dict() (deprecated but kept for backward compatibility)
    if hasattr(obj, 'dict'):
        return obj.dict()
    # Already a dict or other type
    if isinstance(obj, dict):
        return obj
    return obj


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
        contact_info=_pydantic_to_dict(request.contact_info),
        settings=_pydantic_to_dict(request.settings),
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
    tenant_service = TenantService(db)
    
    result = tenant_service.update_tenant(
        tenant_id=tenant_id,
        name=request.name,
        description=request.description,
        domains=request.domains,
        primary_domain=request.primary_domain,
        contact_info=_pydantic_to_dict(request.contact_info),
        settings=_pydantic_to_dict(request.settings),
    )
    
    return result


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
    # Check if username or email already exists in this tenant
    existing = db.query(UserAccount).filter(
        and_(
            or_(
                UserAccount.username == username,
                UserAccount.email == email
            ),
            UserAccount.tenant_id == tenant_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists in this tenant")
    
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
        account_status=AccountStatus.PENDING_ACTIVATION,
        requires_password_change=True,
        created_by=UUID(current_user["user_id"]),
    )
    
    db.add(user)
    db.flush()  # Get user_id
    
    # Create tenant admin account
    admin = TenantAdminAccount(
        user_id=user.user_id,
        tenant_id=tenant_id,
        name=name or username,
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    result = {
        "admin_id": str(admin.tenant_admin_id),
        "user_id": str(user.user_id),
        "tenant_id": str(tenant_id),
        "username": user.username,
        "email": user.email,
        "role": UserRole.TENANT_ADMIN.value,
        "status": user.account_status.value,
        "created_at": user.created_at,
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
    
    # Get tenant users (students, tutors, tenant admins)
    if not role or role in ["student", "tutor", "tenant_admin"]:
        query = db.query(UserAccount)
        
        if status:
            query = query.filter(UserAccount.account_status == AccountStatus(status))
        
        if search:
            query = query.filter(
                or_(
                    UserAccount.username.ilike(f"%{search}%"),
                    UserAccount.email.ilike(f"%{search}%")
                )
            )
        
        users = query.all()
        
        for user in users:
            # Determine role
            tenant_admin = db.query(TenantAdminAccount).filter(
                TenantAdminAccount.user_id == user.user_id
            ).first()
            
            if tenant_admin:
                user_role = "tenant_admin"
                name = tenant_admin.name
            else:
                # Get role from subject roles
                subject_role = db.query(UserSubjectRole).filter(
                    and_(
                        UserSubjectRole.user_id == user.user_id,
                        UserSubjectRole.status == AssignmentStatus.ACTIVE
                    )
                ).first()
                
                if subject_role:
                    user_role = subject_role.role.value
                else:
                    user_role = "unknown"
                
                name = user.username
            
            # Filter by role if specified
            if role and user_role != role:
                continue
            
            accounts.append({
                "account_id": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "name": name,
                "role": user_role,
                "tenant_id": str(user.tenant_id),
                "status": user.account_status.value,
                "created_at": user.created_at,
                "last_login": user.last_login,
            })
    
    # Get system admins
    if not role or role == "system_admin":
        query = db.query(SystemAdminAccount)
        
        if status:
            query = query.filter(SystemAdminAccount.account_status == AccountStatus(status))
        
        if search:
            query = query.filter(
                or_(
                    SystemAdminAccount.username.ilike(f"%{search}%"),
                    SystemAdminAccount.email.ilike(f"%{search}%"),
                    SystemAdminAccount.name.ilike(f"%{search}%")
                )
            )
        
        admins = query.all()
        for admin in admins:
            accounts.append({
                "account_id": str(admin.admin_id),
                "username": admin.username,
                "email": admin.email,
                "name": admin.name,
                "role": admin.role.value,
                "tenant_id": None,
                "status": admin.account_status.value,
                "created_at": admin.created_at,
                "last_login": admin.last_login,
            })
    
    return {
        "accounts": accounts,
        "total": len(accounts),
    }


@router.get("/accounts/{account_id}", status_code=status.HTTP_200_OK)
async def get_account_details(
    account_id: UUID,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get account details (system admin only)"""
    # Try to find account in UserAccount (tenant-scoped users)
    user = db.query(UserAccount).filter(UserAccount.user_id == account_id).first()
    if user:
        # Determine role
        tenant_admin = db.query(TenantAdminAccount).filter(
            TenantAdminAccount.user_id == user.user_id
        ).first()
        
        if tenant_admin:
            role = "tenant_admin"
            name = tenant_admin.name
        else:
            # Get role from subject roles
            subject_role = db.query(UserSubjectRole).filter(
                and_(
                    UserSubjectRole.user_id == user.user_id,
                    UserSubjectRole.status == AssignmentStatus.ACTIVE
                )
            ).first()
            
            if subject_role:
                role = subject_role.role.value
            else:
                role = "unknown"
            
            name = user.username
        
        return {
            "account_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": name,
            "role": role,
            "tenant_id": str(user.tenant_id),
            "status": user.account_status.value,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    
    # Try SystemAdminAccount
    admin = db.query(SystemAdminAccount).filter(SystemAdminAccount.admin_id == account_id).first()
    if admin:
        return {
            "account_id": str(admin.admin_id),
            "username": admin.username,
            "email": admin.email,
            "name": admin.name,
            "role": admin.role.value,
            "tenant_id": None,
            "status": admin.account_status.value,
            "created_at": admin.created_at,
            "last_login": admin.last_login,
        }
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


@router.put("/accounts/{account_id}/status", status_code=status.HTTP_200_OK)
async def update_account_status(
    account_id: UUID,
    status: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Update account status (system admin only)"""
    # Try to find account in UserAccount (tenant-scoped users)
    account = db.query(UserAccount).filter(UserAccount.user_id == account_id).first()
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": str(account_id), "status": status, "updated_at": account.updated_at}
    
    # Try SystemAdminAccount
    account = db.query(SystemAdminAccount).filter(SystemAdminAccount.admin_id == account_id).first()
    if account:
        account.account_status = AccountStatus(status)
        db.commit()
        return {"account_id": str(account_id), "status": status, "updated_at": account.updated_at}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_system_statistics(
    current_user: dict = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """Get system-wide statistics (system admin only)"""
    from sqlalchemy import func
    
    # Count students (users with student role)
    total_students = db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
        and_(
            UserSubjectRole.role == UserRole.STUDENT,
            UserSubjectRole.status == AssignmentStatus.ACTIVE
        )
    ).scalar() or 0
    
    # Count tutors (users with tutor role)
    total_tutors = db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
        and_(
            UserSubjectRole.role == UserRole.TUTOR,
            UserSubjectRole.status == AssignmentStatus.ACTIVE
        )
    ).scalar() or 0
    
    # Count tenant admins
    total_tenant_admins = db.query(func.count(TenantAdminAccount.tenant_admin_id)).scalar() or 0
    
    # Count system admins
    total_system_admins = db.query(func.count(SystemAdminAccount.admin_id)).scalar() or 0
    
    total_admins = total_tenant_admins + total_system_admins
    
    # Count active sessions (sessions with status IN_PROGRESS)
    from src.models.user import SessionStatus
    active_sessions = db.query(func.count(QuizSession.session_id)).filter(
        QuizSession.status == SessionStatus.IN_PROGRESS
    ).scalar() or 0
    
    # Count total sessions
    total_sessions = db.query(func.count(QuizSession.session_id)).scalar() or 0
    
    return {
        "users": {
            "total_students": total_students,
            "total_tutors": total_tutors,
            "total_tenant_admins": total_tenant_admins,
            "total_system_admins": total_system_admins,
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
            "total_sessions": total_sessions,
            "total_questions": 0,
            "total_messages": 0,
            "active_sessions": active_sessions,
        },
    }
