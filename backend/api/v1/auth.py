# =============================================================================
# FILE: C:\bi-platform\backend\api\v1\auth.py
# =============================================================================
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from models.user import User, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Request/Response Models ───────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Literal["admin", "user"] = "user"


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    full_name: str
    email: str


def _normalize_role(role: UserRole | str) -> str:
    value = role.value if hasattr(role, "value") else str(role)
    return "admin" if value == "admin" else "user"


def _to_storage_role(role: Literal["admin", "user"]) -> UserRole:
    return UserRole.admin if role == "admin" else UserRole.analyst


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
        role=_to_storage_role(user_data.role),
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
        role=_normalize_role(user.role),
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
        "role": _normalize_role(user.role),
    }
