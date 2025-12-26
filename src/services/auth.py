"""
Authentication service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from src.models.database import StudentAccount, TutorAccount, AdministratorAccount, PasswordResetOTP
from src.core.security import verify_password, get_password_hash, generate_otp, create_access_token
from src.core.config import settings
from src.core.exceptions import NotFoundError, BadRequestError, UnauthorizedError
from src.services.tenant import TenantService


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tenant_service = TenantService(db)
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user by username/email and password
        """
        # Resolve tenant
        tenant = self.tenant_service.resolve_tenant_by_domain(domain)
        if not tenant:
            return None
        
        tenant_id = tenant["tenant_id"]
        
        # Try to find user in student accounts
        user = self.db.query(StudentAccount).filter(
            (StudentAccount.username == username) | (StudentAccount.email == username),
            StudentAccount.tenant_id == tenant_id,
        ).first()
        
        user_type = "student"
        
        # Try tutor accounts
        if not user:
            user = self.db.query(TutorAccount).filter(
                (TutorAccount.username == username) | (TutorAccount.email == username),
                TutorAccount.tenant_id == tenant_id,
            ).first()
            user_type = "tutor"
        
        # Try admin accounts
        if not user:
            user = self.db.query(AdministratorAccount).filter(
                (AdministratorAccount.username == username) | (AdministratorAccount.email == username),
            ).first()
            user_type = "admin"
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return None
        
        # Check account status
        if user.account_status.value not in ["active", "pending_activation"]:
            return None
        
        # Return user info
        return {
            "user_id": user.student_id if user_type == "student" else (
                user.tutor_id if user_type == "tutor" else user.admin_id
            ),
            "username": user.username,
            "email": user.email,
            "role": user_type,
            "tenant_id": tenant_id if user_type != "admin" or hasattr(user, "tenant_id") else None,
            "grade_level": getattr(user, "grade_level", None),
            "requires_password_change": user.requires_password_change,
            "account_status": user.account_status.value,
        }
    
    def change_password(
        self,
        user_id: UUID,
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
        
        # Find user (simplified - should check user type)
        user = self.db.query(StudentAccount).filter(StudentAccount.student_id == user_id).first()
        if not user:
            user = self.db.query(TutorAccount).filter(TutorAccount.tutor_id == user_id).first()
        if not user:
            user = self.db.query(AdministratorAccount).filter(AdministratorAccount.admin_id == user_id).first()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password if provided
        if current_password and not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.requires_password_change = False
        if user.account_status.value == "pending_activation":
            user.account_status = "active"
        
        self.db.commit()
        
        return {
            "message": "Password changed successfully",
            "requires_password_change": False,
        }
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset OTP
        """
        # Find user by email
        user = self.db.query(StudentAccount).filter(StudentAccount.email == email).first()
        user_type = "student"
        user_id = None
        
        if not user:
            user = self.db.query(TutorAccount).filter(TutorAccount.email == email).first()
            user_type = "tutor"
        
        if not user:
            user = self.db.query(AdministratorAccount).filter(AdministratorAccount.email == email).first()
            user_type = "admin"
        
        if not user:
            # Don't reveal if email exists (security)
            return {
                "message": "If the email exists, an OTP has been sent",
            }
        
        user_id = user.student_id if user_type == "student" else (
            user.tutor_id if user_type == "tutor" else user.admin_id
        )
        
        # Generate OTP
        otp = generate_otp()
        otp_hash = get_password_hash(otp)
        
        # Create OTP record
        otp_record = PasswordResetOTP(
            student_id=user_id if user_type == "student" else None,
            tutor_id=user_id if user_type == "tutor" else None,
            admin_id=user_id if user_type == "admin" else None,
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
            PasswordResetOTP.email == email,
            PasswordResetOTP.used == False,
            PasswordResetOTP.expires_at > datetime.utcnow(),
        ).order_by(PasswordResetOTP.created_at.desc()).first()
        
        if not otp_record:
            raise BadRequestError("Invalid or expired OTP")
        
        # Verify OTP
        if not verify_password(otp, otp_record.otp_code_hash):
            raise BadRequestError("Invalid OTP")
        
        # Find user
        user = None
        if otp_record.student_id:
            user = self.db.query(StudentAccount).filter(StudentAccount.student_id == otp_record.student_id).first()
        elif otp_record.tutor_id:
            user = self.db.query(TutorAccount).filter(TutorAccount.tutor_id == otp_record.tutor_id).first()
        elif otp_record.admin_id:
            user = self.db.query(AdministratorAccount).filter(AdministratorAccount.admin_id == otp_record.admin_id).first()
        
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
        token_data = {
            "sub": str(user_id := (user.student_id if hasattr(user, "student_id") else (
                user.tutor_id if hasattr(user, "tutor_id") else user.admin_id
            ))),
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

