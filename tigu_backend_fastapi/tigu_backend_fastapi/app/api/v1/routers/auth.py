from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.base import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User, UserSession, Company, CompanyUser
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest
)
from app.schemas.user import UserResponse, CompanyResponse
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    verify_token, generate_password_reset_token, verify_password_reset_token
)
from app.core.config import settings
import secrets
import uuid

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user and company
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create company first
    # Generate unique company code
    company_code = f"COMP{datetime.utcnow().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"
    
    company = Company(
        company_code=company_code,
        company_name={"zh-CN": user_data.company_name, "en-US": user_data.company_name},
        company_type=user_data.company_type,
        business_license=user_data.business_license,
        tax_number=user_data.tax_number,
        is_active=True,
        is_verified=False
    )
    db.add(company)
    db.flush()  # Get company ID
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        auth_provider="email",
        default_company_id=company.id,
        is_active=True,
        password_changed_at=datetime.utcnow()
    )
    db.add(user)
    db.flush()  # Get user ID
    
    # Associate user with company
    company_user = CompanyUser(
        company_id=company.id,
        user_id=user.id,
        role="admin",  # First user is admin
        is_active=True
    )
    db.add(company_user)
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(session)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "default_company_id": user.default_company_id
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login with email and password
    """
    # Get user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed attempts"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(session)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "default_company_id": user.default_company_id
        }
    )

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = verify_token(refresh_data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "default_company_id": user.default_company_id
            }
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user (invalidate current session)
    """
    # In a real implementation, you would invalidate the specific session
    # For now, we'll just return success
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all sessions
    """
    # Deactivate all user sessions
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    return {"message": "Successfully logged out from all sessions"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update allowed fields
    if "full_name" in profile_data:
        current_user.full_name = profile_data["full_name"]
    if "phone" in profile_data:
        current_user.phone = profile_data["phone"]
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        # In a real implementation, you would send this token via email
        # For now, we'll just return success
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token
    """
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    return {"message": "Password reset successfully"} 