# =============================================================================
# FILE: C:\bi-platform\backend\api\v1\auth.py
# =============================================================================
import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, EmailStr
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from models.user import User, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ── In-memory OTP store (works perfectly for demo) ────────────────────────
otp_store = {}


# ── Request/Response Models ───────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.viewer


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    full_name: str
    email: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


# ── Register ──────────────────────────────────────────────────────────────
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.flush()
    await db.commit()
    return {
        "id": user.id,
        "email": user.email,
        "message": "User created successfully"
    }


# ── Login ─────────────────────────────────────────────────────────────────
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    token = create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )


# ── Get Current User ──────────────────────────────────────────────────────
@router.get("/me")
async def get_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    from core.security import decode_access_token
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_premium": user.is_premium,
    }


# ── Forgot Password — Step 1: Send OTP ───────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check email exists and generate OTP."""
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found with this email address"
        )

    # Generate 6 digit OTP
    otp = ''.join(random.choices(string.digits, k=6))

    # Store OTP with 10 minute expiry
    otp_store[request.email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10),
        "user_id": user.id,
    }

    # Print OTP to backend terminal (demo mode)
    print(f"\n{'='*50}")
    print(f"  PASSWORD RESET OTP")
    print(f"  Email : {request.email}")
    print(f"  OTP   : {otp}")
    print(f"  Expiry: 10 minutes")
    print(f"{'='*50}\n")

    return {
        "message": f"OTP sent successfully to {request.email}",
        "otp": otp,  # Shown in frontend for demo
        "expires_in": "10 minutes",
    }


# ── Forgot Password — Step 2: Verify OTP ─────────────────────────────────
@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify the OTP entered by user."""
    stored = otp_store.get(request.email)

    if not stored:
        raise HTTPException(
            status_code=400,
            detail="No OTP found for this email. Please request a new one."
        )

    if datetime.utcnow() > stored["expires"]:
        del otp_store[request.email]
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    if stored["otp"] != request.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP. Please check and try again."
        )

    return {
        "message": "OTP verified successfully",
        "verified": True,
    }


# ── Forgot Password — Step 3: Reset Password ─────────────────────────────
@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password after OTP verification."""

    # Verify OTP again for security
    stored = otp_store.get(request.email)

    if not stored:
        raise HTTPException(
            status_code=400,
            detail="No OTP found. Please start the reset process again."
        )

    if datetime.utcnow() > stored["expires"]:
        del otp_store[request.email]
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    if stored["otp"] != request.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP."
        )

    # Find user in database
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash new password and update database
    new_hashed = hash_password(request.new_password)
    await db.execute(
        text("UPDATE users SET hashed_password = :pwd WHERE email = :email"),
        {"pwd": new_hashed, "email": request.email}
    )
    await db.commit()

    # Delete used OTP so it cannot be reused
    del otp_store[request.email]

    print(f"\n✅ Password reset successful for: {request.email}\n")

    return {
        "message": "Password reset successfully! You can now login with your new password.",
        "email": request.email,
    }