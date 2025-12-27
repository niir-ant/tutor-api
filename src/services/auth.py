"""
Authentication service - updated for new model structure
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID

from src.models.database import (
    UserAccount, SystemAdminAccount, PasswordResetOTP, 
    UserSubjectRole, TenantAdminAccount
)
from src.core.security import verify_password, get_password_hash, generate_otp, create_access_token
from src.core.config import settings
from src.core.exceptions import NotFoundError, BadRequestError, UnauthorizedError
from src.services.tenant import TenantService
from src.models.user import UserRole, AccountStatus


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tenant_service = TenantService(db)
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        domain: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user by username/email and password
        
        For tenant-scoped users, domain is required.
        For system admins, domain is optional (they can use any domain or none).
        """
        user = None
        user_type = None
        tenant_id = None
        
        # If domain provided, try tenant-scoped users first
        if domain:
            tenant = self.tenant_service.resolve_tenant_by_domain(domain)
            if tenant:
                tenant_id = tenant["tenant_id"]
                
                # Try to find user in user_accounts (tenant-scoped)
                user = self.db.query(UserAccount).filter(
                    and_(
                        or_(
                            UserAccount.username == username,
                            UserAccount.email == username
                        ),
                        UserAccount.tenant_id == tenant_id
                    )
                ).first()
                
                if user:
                    user_type = "tenant_user"
        
        # If not found and domain provided, or if no domain, try system admin
        if not user:
            user = self.db.query(SystemAdminAccount).filter(
                or_(
                    SystemAdminAccount.username == username,
                    SystemAdminAccount.email == username
                )
            ).first()
            
            if user:
                user_type = "system_admin"
                tenant_id = None  # System admins don't have tenant_id
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return None
        
        # Check account status
        # Handle enum conversion - SQLAlchemy might return enum or string
        if hasattr(user.account_status, 'value'):
            account_status = user.account_status.value
        elif isinstance(user.account_status, str):
            account_status = user.account_status
        else:
            account_status = str(user.account_status)
        
        if account_status not in ["active", "pending_activation"]:
            return None
        
        # Determine role
        if user_type == "system_admin":
            role = UserRole.SYSTEM_ADMIN.value
        elif user_type == "tenant_user":
            # Check if user is a tenant admin
            tenant_admin = self.db.query(TenantAdminAccount).filter(
                TenantAdminAccount.user_id == user.user_id
            ).first()
            
            if tenant_admin:
                role = UserRole.TENANT_ADMIN.value
            else:
                # Check subject roles to determine if student or tutor
                # For login, we'll use the first active role found, or default to student
                from src.models.user import AssignmentStatus
                subject_role = self.db.query(UserSubjectRole).filter(
                    and_(
                        UserSubjectRole.user_id == user.user_id,
                        UserSubjectRole.status == AssignmentStatus.ACTIVE
                    )
                ).first()
                
                if subject_role:
                    # Handle enum - could be enum instance or value
                    if hasattr(subject_role.role, 'value'):
                        role = subject_role.role.value
                    else:
                        role = str(subject_role.role)
                else:
                    # No subject role assigned yet - default to student
                    role = UserRole.STUDENT.value
        else:
            return None
        
        # Get grade level from student profile if available
        grade_level = None
        if role == UserRole.STUDENT.value:
            # Get grade level from first student profile
            from src.models.database import StudentSubjectProfile
            profile = self.db.query(StudentSubjectProfile).filter(
                StudentSubjectProfile.user_id == user.user_id
            ).first()
            if profile:
                grade_level = profile.grade_level
        
        # Return user info
        user_id = user.user_id if user_type == "tenant_user" else user.admin_id
        
        return {
            "user_id": str(user_id),
            "username": user.username,
            "email": user.email,
            "role": role,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "grade_level": grade_level,
            "requires_password_change": user.requires_password_change,
            "account_status": account_status,
            "user_type": user_type,  # "tenant_user" or "system_admin"
        }
    
    def change_password(
        self,
        user_id: UUID,
        user_type: str,  # "tenant_user" or "system_admin"
        current_password: Optional[str],
        new_password: str,
        confirm_password: str,
    ) -> Dict[str, Any]:
        """
        Change user password
        """
        if new_password != confirm_password:
            raise BadRequestError("Passwords do not match")
        
        if len(new_password) < settings.PASSWORD_MIN_LENGTH:
            raise BadRequestError(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters")
        
        # Find user based on type
        if user_type == "system_admin":
            user = self.db.query(SystemAdminAccount).filter(
                SystemAdminAccount.admin_id == user_id
            ).first()
        else:
            user = self.db.query(UserAccount).filter(
                UserAccount.user_id == user_id
            ).first()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password if provided
        if current_password and not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.requires_password_change = False
        
        # Update account status if pending activation
        if user.account_status == AccountStatus.PENDING_ACTIVATION:
            user.account_status = AccountStatus.ACTIVE
        
        self.db.commit()
        
        return {
            "message": "Password changed successfully",
            "requires_password_change": False,
        }
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset OTP
        """
        # Find user by email - try tenant users first
        user = self.db.query(UserAccount).filter(UserAccount.email == email).first()
        user_type = "tenant_user"
        user_id = None
        
        if not user:
            user = self.db.query(SystemAdminAccount).filter(
                SystemAdminAccount.email == email
            ).first()
            user_type = "system_admin"
        
        if not user:
            # Don't reveal if email exists (security)
            return {
                "message": "If the email exists, an OTP has been sent",
            }
        
        user_id = user.user_id if user_type == "tenant_user" else user.admin_id
        
        # Generate OTP
        otp = generate_otp()
        otp_hash = get_password_hash(otp)
        
        # Create OTP record (only for tenant users - system admins use user_id)
        otp_record = PasswordResetOTP(
            user_id=user_id if user_type == "tenant_user" else None,
            email=email,
            otp_code_hash=otp_hash,
            expires_at=datetime.utcnow() + timedelta(seconds=settings.OTP_EXPIRATION_SECONDS),
        )
        
        self.db.add(otp_record)
        self.db.commit()
        
        # TODO: Send email with OTP
        # For now, in development, log it
        print(f"OTP for {email}: {otp}")  # Remove in production
        
        return {
            "message": "If the email exists, an OTP has been sent",
        }
    
    def reset_password_with_otp(
        self,
        email: str,
        otp: str,
        new_password: str,
        confirm_password: str,
    ) -> Dict[str, Any]:
        """
        Reset password using OTP
        """
        if new_password != confirm_password:
            raise BadRequestError("Passwords do not match")
        
        # Find valid OTP
        otp_record = self.db.query(PasswordResetOTP).filter(
            and_(
            PasswordResetOTP.email == email,
            PasswordResetOTP.used == False,
                PasswordResetOTP.expires_at > datetime.utcnow()
            )
        ).order_by(PasswordResetOTP.created_at.desc()).first()
        
        if not otp_record:
            raise BadRequestError("Invalid or expired OTP")
        
        # Verify OTP
        if not verify_password(otp, otp_record.otp_code_hash):
            raise BadRequestError("Invalid OTP")
        
        # Find user
        user = None
        user_type = None
        
        if otp_record.user_id:
            # Tenant user
            user = self.db.query(UserAccount).filter(
                UserAccount.user_id == otp_record.user_id
            ).first()
            user_type = "tenant_user"
        else:
            # System admin - find by email
            user = self.db.query(SystemAdminAccount).filter(
                SystemAdminAccount.email == email
            ).first()
            user_type = "system_admin"
        
        if not user:
            raise NotFoundError("User not found")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.requires_password_change = False
        
        # Mark OTP as used
        otp_record.used = True
        otp_record.used_at = datetime.utcnow()
        
        self.db.commit()
        
        # Create access token
        user_id = user.user_id if user_type == "tenant_user" else user.admin_id
        token_data = {
            "sub": str(user_id),
            "username": user.username,
            "email": user.email,
        }
        access_token = create_access_token(data=token_data)
        
        return {
            "message": "Password reset successfully",
            "access_token": access_token,
            "token_type": "Bearer",
        }
    
    def resend_otp(self, email: str) -> Dict[str, Any]:
        """
        Resend OTP for password reset
        """
        return self.request_password_reset(email)
