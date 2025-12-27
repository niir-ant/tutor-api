"""
FastAPI dependencies - updated for new model structure
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.database import get_db
from src.core.security import decode_token
from src.core.exceptions import UnauthorizedError, ForbiddenError
from src.models.user import UserRole, AccountStatus
from src.models.database import UserAccount, SystemAdminAccount, TenantAdminAccount, UserSubjectRole
from src.services.tenant import TenantService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid authentication credentials")
    
    # Determine user type from payload or query database
    user_type = payload.get("user_type", "tenant_user")  # Default to tenant_user
    
    # Get user from database based on type
    if user_type == "system_admin":
        user = db.query(SystemAdminAccount).filter(
            SystemAdminAccount.admin_id == UUID(user_id)
        ).first()
        
        if not user:
            raise UnauthorizedError("User not found")
        
        return {
            "user_id": str(user.admin_id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "tenant_id": None,  # System admins don't have tenant_id
            "grade_level": None,
            "user_type": "system_admin",
        }
    else:
        # Tenant user
        user = db.query(UserAccount).filter(
            UserAccount.user_id == UUID(user_id)
        ).first()
        
        if not user:
            raise UnauthorizedError("User not found")
        
        # Determine role
        tenant_admin = db.query(TenantAdminAccount).filter(
            TenantAdminAccount.user_id == user.user_id
        ).first()
        
        if tenant_admin:
            role = UserRole.TENANT_ADMIN.value
        else:
            # Get role from subject roles
            subject_role = db.query(UserSubjectRole).filter(
                UserSubjectRole.user_id == user.user_id
            ).first()
            
            if subject_role:
                role = subject_role.role.value
            else:
                role = UserRole.STUDENT.value  # Default
        
        # Get grade level from student profile
        grade_level = None
        if role == UserRole.STUDENT.value:
            from src.models.database import StudentSubjectProfile
            profile = db.query(StudentSubjectProfile).filter(
                StudentSubjectProfile.user_id == user.user_id
            ).first()
            if profile:
                grade_level = profile.grade_level
        
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "role": role,
            "tenant_id": str(user.tenant_id),
            "grade_level": grade_level,
            "user_type": "tenant_user",
        }


async def get_current_tenant(
    domain: Optional[str] = Query(None),
    x_tenant_domain: Optional[str] = Header(None, alias="X-Tenant-Domain"),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """
    Resolve tenant from domain parameter
    """
    tenant_domain = domain or x_tenant_domain
    if not tenant_domain:
        return None
    
    tenant_service = TenantService(db)
    tenant = tenant_service.resolve_tenant_by_domain(tenant_domain)
    return tenant


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency to require specific role(s)
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in [role.value for role in allowed_roles]:
            raise ForbiddenError(f"Access denied. Required roles: {allowed_roles}")
        return current_user
    return role_checker


def require_system_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require system admin role"""
    if current_user.get("role") != UserRole.SYSTEM_ADMIN.value:
        raise ForbiddenError("System admin access required")
    return current_user


def require_tenant_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require tenant admin role"""
    role = current_user.get("role")
    if role not in [UserRole.TENANT_ADMIN.value, UserRole.SYSTEM_ADMIN.value]:
        raise ForbiddenError("Tenant admin access required")
    return current_user


def require_tutor_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require tutor or admin role"""
    role = current_user.get("role")
    allowed_roles = [
        UserRole.TUTOR.value,
        UserRole.TENANT_ADMIN.value,
        UserRole.SYSTEM_ADMIN.value,
    ]
    if role not in allowed_roles:
        raise ForbiddenError("Tutor or admin access required")
    return current_user
