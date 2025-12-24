
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Any
from datetime import datetime, timedelta, timezone
import secrets

from app.database import get_session
from app.models import (
    User,
    RefreshToken,
    OTPVerification,
    AuditLog,
    AuditAction,
    AccessLink
)
from app.deps import get_current_user
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.config import settings
from app.email import send_otp_email
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Request Models
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_verified: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/hour")
async def register(
    request: Request,
    user_in: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user and send an email verification OTP.
    """
    # Check if user exists
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    # Create user
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_verified=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate OTP
    otp = secrets.token_hex(3).upper() # 6 chars
    otp_record = OTPVerification(
        user_id=user.id,
        otp_code=otp,
        purpose="email_verification",
        expires_at=settings.OTP_EXPIRE_MINUTES if hasattr(settings, 'OTP_EXPIRE_MINUTES') else datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    session.add(otp_record)
    session.commit()

    # Send Email (Simulated)
    await send_otp_email(user.email, otp)

    # Audit Log
    client_host = request.client.host if request.client else "unknown"
    audit = AuditLog(
        user_id=user.id,
        action=AuditAction.REGISTER,
        ip_address=client_host
    )
    session.add(audit)
    session.commit()

    return user

@router.post("/verify-email")
@limiter.limit("5/15minute")
async def verify_email(
    request: Request,
    verify_in: OTPVerify,
    session: Session = Depends(get_session)
):
    """
    Verify user's email address using the OTP code.
    """
    user = session.exec(select(User).where(User.email == verify_in.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_record = session.exec(
        select(OTPVerification)
        .where(OTPVerification.user_id == user.id)
        .where(OTPVerification.purpose == "email_verification")
        .where(OTPVerification.is_used == False)
        .where(OTPVerification.otp_code == verify_in.otp)
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Ensure expires_at is timezone aware
    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    # Mark verified
    user.is_verified = True
    otp_record.is_used = True
    session.add(user)
    session.add(otp_record)

    audit = AuditLog(user_id=user.id, action=AuditAction.VERIFY_EMAIL)
    session.add(audit)

    session.commit()
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token)
@limiter.limit("5/15minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return Access/Refresh tokens.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)

    # Store refresh token
    db_refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    session.add(db_refresh)

    # Audit
    session.add(AuditLog(user_id=user.id, action=AuditAction.LOGIN_SUCCESS))
    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)

    session.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_in: RefreshRequest,
    session: Session = Depends(get_session)
):
    """
    Refresh access token using a valid refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token signature
    try:
        payload = jwt.decode(refresh_in.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check if token exists in DB and is not revoked
    db_token = session.exec(
        select(RefreshToken)
        .where(RefreshToken.token == refresh_in.refresh_token)
        .where(RefreshToken.is_revoked == False)
    ).first()

    if not db_token:
        raise credentials_exception

    # Check expiry
    if db_token.expires_at < datetime.now(timezone.utc):
        raise credentials_exception

    # Revoke old token
    db_token.is_revoked = True
    session.add(db_token)

    # Create new tokens
    access_token = create_access_token(subject=email)
    new_refresh_token = create_refresh_token(subject=email)

    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        new_db_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        session.add(new_db_token)
        session.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Log out the current user (Revoke session/refresh token).
    """
    # In a JWT stateless system, we can't strictly "invalidate" the access token without a blacklist.
    # But we can revoke the refresh token if provided, or log the logout action.
    # A robust implementation would require sending the refresh token to be revoked.
    # For MVP, we just log the action.

    session.add(AuditLog(user_id=current_user.id, action=AuditAction.LOGOUT))
    session.commit()
    return {"message": "Logged out"}

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Initiate password reset flow by sending an OTP to the email.
    """
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        # Don't reveal user existence
        return {"message": "If this email exists, a reset code has been sent."}

    # Generate Reset OTP
    otp = secrets.token_hex(3).upper()
    otp_record = OTPVerification(
        user_id=user.id,
        otp_code=otp,
        purpose="password_reset",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    session.add(otp_record)
    session.commit()

    # Send Email
    await send_otp_email(user.email, otp)

    return {"message": "If this email exists, a reset code has been sent."}

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Reset password using the OTP received via email.
    """
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_record = session.exec(
        select(OTPVerification)
        .where(OTPVerification.user_id == user.id)
        .where(OTPVerification.purpose == "password_reset")
        .where(OTPVerification.is_used == False)
        .where(OTPVerification.otp_code == request.otp)
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Ensure expires_at is timezone aware
    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    # Reset Password
    user.password_hash = get_password_hash(request.new_password)
    otp_record.is_used = True
    session.add(user)
    session.add(otp_record)

    session.add(AuditLog(user_id=user.id, action=AuditAction.PASSWORD_RESET))
    session.commit()

    return {"message": "Password reset successfully"}

@router.get("/oauth/google")
async def google_login():
    """
    Return the Google OAuth login URL.
    """
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/api/auth/oauth/google/callback&scope=openid%20email%20profile"
    }

@router.get("/oauth/google/callback")
async def google_callback(code: str, session: Session = Depends(get_session)):
    """
    Handle Google OAuth callback. (MVP Stub)
    """
    # MVP Stub: We would exchange code for token here.
    # Since we can't really test this without a real Google App, we'll return a stub error or mock.
    if settings.GOOGLE_CLIENT_ID is None:
         raise HTTPException(status_code=501, detail="Google OAuth not configured")

    return {"message": "Google OAuth callback received. Implementation requires valid credentials.", "code": code}
