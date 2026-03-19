from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.db_bootstrap import bootstrap_database, get_database_status
from core.security import hash_password
from core.security import decode_access_token
from models.user import User, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class InitRequest(BaseModel):
    ensure_schema: bool = True
    seed_default_users: bool = True


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.viewer
    is_premium: bool = False
    password: str = "changeme123"


class UserUpdateRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    is_premium: bool


class ToggleActiveRequest(BaseModel):
    is_active: bool


class TogglePremiumRequest(BaseModel):
    is_premium: bool


class PasswordChangeRequest(BaseModel):
    new_password: str


class SystemConfigRequest(BaseModel):
    siteName: str
    maxLoginAttempts: str
    sessionTimeout: str
    enableNotifications: bool
    enableAuditLog: bool
    enableTwoFactor: bool
    dataRefreshInterval: str
    maxExportRows: str
    enableChatbot: bool
    enableForecasting: bool


PERMISSIONS: List[Dict[str, object]] = [
    {"feature": "View Dashboard", "admin": True, "analyst": True, "viewer": True},
    {"feature": "View Sales Analytics", "admin": True, "analyst": True, "viewer": True},
    {"feature": "View Inventory", "admin": True, "analyst": True, "viewer": True},
    {"feature": "View Customers", "admin": True, "analyst": True, "viewer": False},
    {"feature": "ML Forecasting", "admin": True, "analyst": True, "viewer": False},
    {"feature": "Anomaly Detection", "admin": True, "analyst": True, "viewer": False},
    {"feature": "AI Chatbot", "admin": True, "analyst": True, "viewer": True},
    {"feature": "Export CSV / PDF", "admin": True, "analyst": True, "viewer": False},
    {"feature": "Create Reports", "admin": True, "analyst": True, "viewer": False},
    {"feature": "Manage Users", "admin": True, "analyst": False, "viewer": False},
    {"feature": "System Settings", "admin": True, "analyst": False, "viewer": False},
    {"feature": "View Audit Logs", "admin": True, "analyst": False, "viewer": False},
    {"feature": "API Access", "admin": True, "analyst": True, "viewer": False},
    {"feature": "Premium Features", "admin": True, "analyst": False, "viewer": False},
]


SYSTEM_CONFIG: Dict[str, object] = {
    "siteName": "BI Platform",
    "maxLoginAttempts": "5",
    "sessionTimeout": "60",
    "enableNotifications": True,
    "enableAuditLog": True,
    "enableTwoFactor": False,
    "dataRefreshInterval": "30",
    "maxExportRows": "10000",
    "enableChatbot": True,
    "enableForecasting": True,
}


async def get_admin_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")

    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return user


def _serialize_user(user: User) -> Dict[str, object]:
    created = user.created_at.date().isoformat() if user.created_at else None
    last_login = user.updated_at.isoformat() if user.updated_at else "Never"
    role_value = user.role.value if hasattr(user.role, "value") else str(user.role)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role_value,
        "is_active": bool(user.is_active),
        "is_premium": bool(user.is_premium),
        "last_login": last_login,
        "created": created,
    }


@router.get("/db/status")
async def db_status(_: User = Depends(get_admin_user)):
    return await get_database_status()


@router.post("/db/initialize")
async def db_initialize(payload: InitRequest, _: User = Depends(get_admin_user)):
    return await bootstrap_database(
        ensure_schema_first=payload.ensure_schema,
        seed_defaults=payload.seed_default_users,
    )


@router.get("/users")
async def list_users(
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.id.asc()))
    users = result.scalars().all()
    return [_serialize_user(u) for u in users]


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True,
        is_premium=payload.is_premium,
    )
    db.add(user)
    await db.flush()
    return _serialize_user(user)


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.execute(select(User).where(User.email == payload.email, User.id != user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    user.email = payload.email
    user.full_name = payload.full_name
    user.role = payload.role
    user.is_premium = payload.is_premium
    user.updated_at = datetime.utcnow()
    await db.flush()
    return _serialize_user(user)


@router.patch("/users/{user_id}/active")
async def set_user_active(
    user_id: int,
    payload: ToggleActiveRequest,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if admin_user.id == user_id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = payload.is_active
    user.updated_at = datetime.utcnow()
    await db.flush()
    return _serialize_user(user)


@router.patch("/users/{user_id}/premium")
async def set_user_premium(
    user_id: int,
    payload: TogglePremiumRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_premium = payload.is_premium
    user.updated_at = datetime.utcnow()
    await db.flush()
    return _serialize_user(user)


@router.post("/users/{user_id}/password")
async def change_user_password(
    user_id: int,
    payload: PasswordChangeRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    user.updated_at = datetime.utcnow()
    await db.flush()
    return {"message": "Password changed successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if admin_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    return {"message": "User deleted successfully"}


@router.get("/permissions")
async def get_permissions(_: User = Depends(get_admin_user)):
    return PERMISSIONS


@router.get("/config")
async def get_system_config(_: User = Depends(get_admin_user)):
    return SYSTEM_CONFIG


@router.put("/config")
async def update_system_config(
    payload: SystemConfigRequest,
    _: User = Depends(get_admin_user),
):
    SYSTEM_CONFIG.update(payload.model_dump())
    return SYSTEM_CONFIG
