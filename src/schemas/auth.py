"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str
    domain: Optional[str] = None


class UserInfo(BaseModel):
    """User information"""
    user_id: UUID
    username: str
    email: str
    role: str
    tenant_id: Optional[UUID] = None
    grade_level: Optional[int] = None
    requires_password_change: bool
    account_status: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str
    user: UserInfo
    requires_password_change: bool = False  # Flag to indicate if password change is required


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: Optional[str] = None
    new_password: str
    confirm_password: str


class ChangePasswordResponse(BaseModel):
    """Change password response"""
    message: str
    requires_password_change: bool


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Forgot password response"""
    message: str
    otp_expires_in: int


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


class ResetPasswordResponse(BaseModel):
    """Reset password response"""
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class ResendOTPRequest(BaseModel):
    """Resend OTP request"""
    email: EmailStr


class ResendOTPResponse(BaseModel):
    """Resend OTP response"""
    message: str
    otp_expires_in: int


class AuthStatusResponse(BaseModel):
    """Authentication status response"""
    authenticated: bool
    requires_password_change: bool = False
    user: Optional[UserInfo] = None

