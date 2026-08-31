"""
Authentication API routes.

Handles user signup, login, logout, password reset, and session management.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models as m
from app.schemas.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignUpRequest,
    UserResponse,
)
from app.services.security import (
    create_access_token,
    decode_token,
    hash_password,
    validate_email,
    validate_password_strength,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In a production app, you'd store password reset tokens in a database or cache
# with expiration. For now, we'll use a simple in-memory store.
_password_reset_tokens: dict[str, dict] = {}


def get_current_user(
    db: Session = Depends(get_db), 
    auth_token: Optional[str] = Cookie(None)
) -> Optional[m.User]:
    """
    Get the current authenticated user from cookie.
    
    Returns None if not authenticated.
    """
    if not auth_token:
        return None
    
    payload = decode_token(auth_token)
    if not payload or "user_id" not in payload:
        return None
    
    user = db.query(m.User).filter(m.User.id == payload["user_id"]).first()
    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    Validates:
    - Email format
    - Email uniqueness
    - Password strength
    
    Returns the created user.
    """
    # Validate email format
    if not validate_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if email already exists
    existing_user = db.query(m.User).filter(m.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, issues = validate_password_strength(payload.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements: " + "; ".join(issues)
        )
    
    # Create user
    user = m.User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate a user and create a session via cookie.
    
    Returns:
        - User information
        - Sets authentication cookie (HttpOnly, Secure)
    """
    # Find user by email
    user = db.query(m.User).filter(m.User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    token = create_access_token(data={"user_id": user.id, "email": user.email})
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.post("/logout")
def logout(response: Response):
    """Clear authentication cookie."""
    response.delete_cookie(
        key="auth_token",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    auth_token: Optional[str] = Cookie(None)
):
    """
    Get current authenticated user information.
    
    Requires valid authentication cookie.
    """
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(auth_token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(m.User).filter(m.User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    """
    Initiate password reset flow.
    
    For security, always returns success message regardless of whether
    email exists in database. In production, would send reset email.
    """
    # Note: In production, you would:
    # 1. Find user by email
    # 2. Generate secure reset token
    # 3. Store token in database with expiration
    # 4. Send email with reset link
    # 5. Return generic message
    
    # For development, we'll just acknowledge the request
    return {
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using reset token.
    
    Note: This is a placeholder implementation. In production:
    - Validate token from reset link
    - Check token expiration
    - Verify user still exists
    - Update password
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset via email is not yet configured"
    )
