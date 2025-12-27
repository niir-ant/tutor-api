"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_tenant, get_current_user
from src.core.security import verify_password, create_access_token, create_refresh_token
from src.core.config import settings
from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    AuthStatusResponse,
    UserInfo,
)
from src.services.auth import AuthService
from datetime import timedelta

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    domain: Optional[str] = Query(None),
    x_tenant_domain: Optional[str] = Header(None, alias="X-Tenant-Domain"),
    db: Session = Depends(get_db),
):
    """
    User login endpoint
    """
    # Resolve tenant (optional for system admins)
    tenant_domain = request.domain or domain or x_tenant_domain
    
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(
        username=request.username,
        password=request.password,
        domain=tenant_domain,  # Can be None for system admins
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create tokens (even if password change is required - user is authenticated)
    # Frontend will check requires_password_change flag and redirect accordingly
    token_data = {
        "sub": str(user["user_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "tenant_id": str(user["tenant_id"]) if user.get("tenant_id") else None,
        "user_type": user.get("user_type", "tenant_user"),  # "tenant_user" or "system_admin"
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data=token_data)
    
    return LoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=user,
        requires_password_change=user.get("requires_password_change", False),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: dict = Depends(lambda: {}),  # TODO: Implement token revocation
):
    """
    User logout endpoint
    """
    # TODO: Implement token revocation
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token
    """
    from src.core.security import decode_token
    
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "tenant_id": payload.get("tenant_id"),
            "user_type": payload.get("user_type", "tenant_user"),
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/change-password", response_model=ChangePasswordResponse, status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change password (first login or update)
    """
    from src.core.dependencies import get_current_user
    from uuid import UUID
    
    auth_service = AuthService(db)
    result = auth_service.change_password(
        user_id=UUID(current_user["user_id"]),
        user_type=current_user.get("user_type", "tenant_user"),
        current_password=request.current_password,
        new_password=request.new_password,
        confirm_password=request.confirm_password,
    )
    
    return ChangePasswordResponse(
        message=result["message"],
        requires_password_change=result.get("requires_password_change", False),
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Request password reset OTP
    """
    auth_service = AuthService(db)
    result = auth_service.request_password_reset(request.email)
    
    return ForgotPasswordResponse(
        message=result["message"],
        otp_expires_in=settings.OTP_EXPIRATION_SECONDS,
    )


@router.post("/reset-password", response_model=ResetPasswordResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reset password with OTP
    """
    auth_service = AuthService(db)
    result = auth_service.reset_password_with_otp(
        email=request.email,
        otp=request.otp,
        new_password=request.new_password,
        confirm_password=request.confirm_password,
    )
    
    return ResetPasswordResponse(
        message=result["message"],
        access_token=result.get("access_token"),
        token_type=result.get("token_type"),
    )


@router.post("/resend-otp", response_model=ResendOTPResponse, status_code=status.HTTP_200_OK)
async def resend_otp(
    request: ResendOTPRequest,
    db: Session = Depends(get_db),
):
    """
    Resend OTP for password reset
    """
    auth_service = AuthService(db)
    result = auth_service.resend_otp(request.email)
    
    return ResendOTPResponse(
        message=result["message"],
        otp_expires_in=settings.OTP_EXPIRATION_SECONDS,
    )


@router.get("/status", response_model=AuthStatusResponse, status_code=status.HTTP_200_OK)
async def get_auth_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current authentication status and password change requirement.
    Frontend should call this on app initialization to determine which screen to show.
    """
    from uuid import UUID
    from src.models.database import UserAccount, SystemAdminAccount
    
    user_type = current_user.get("user_type", "tenant_user")
    user_id = UUID(current_user["user_id"])
    
    # Get user from database to check requires_password_change
    if user_type == "system_admin":
        user = db.query(SystemAdminAccount).filter(
            SystemAdminAccount.admin_id == user_id
        ).first()
    else:
        user = db.query(UserAccount).filter(
            UserAccount.user_id == user_id
        ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Build user info
    user_info = UserInfo(
        user_id=UUID(current_user["user_id"]),
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        tenant_id=UUID(current_user["tenant_id"]) if current_user.get("tenant_id") else None,
        grade_level=current_user.get("grade_level"),
        requires_password_change=user.requires_password_change,
        account_status=user.account_status.value if hasattr(user.account_status, 'value') else str(user.account_status),
    )
    
    return AuthStatusResponse(
        authenticated=True,
        requires_password_change=user.requires_password_change,
        user=user_info,
    )

