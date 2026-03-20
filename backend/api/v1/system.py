from datetime import datetime
from typing import Dict, List
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
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
    role: Literal["admin", "user"] = "user"
    password: str = "changeme123"


class UserUpdateRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: Literal["admin", "user"]


class ToggleActiveRequest(BaseModel):
    is_active: bool


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
    {"feature": "View Dashboard", "admin": True, "user": True},
    {"feature": "View Sales Analytics", "admin": True, "user": True},
    {"feature": "View Inventory", "admin": True, "user": True},
    {"feature": "View Customers", "admin": True, "user": True},
    {"feature": "ML Forecasting", "admin": True, "user": True},
    {"feature": "AI Chatbot", "admin": True, "user": True},
    {"feature": "Export CSV / PDF", "admin": True, "user": True},
    {"feature": "Create Reports", "admin": True, "user": True},
    {"feature": "Manage Users", "admin": True, "user": False},
    {"feature": "System Settings", "admin": True, "user": False},
    {"feature": "View Audit Logs", "admin": True, "user": False},
    {"feature": "API Access", "admin": True, "user": True},
]


def _normalize_role(role: UserRole | str) -> str:
    value = role.value if hasattr(role, "value") else str(role)
    return "admin" if value == "admin" else "user"


def _to_storage_role(role: Literal["admin", "user"]) -> UserRole:
    return UserRole.admin if role == "admin" else UserRole.analyst


DEFAULT_SYSTEM_CONFIG: Dict[str, object] = {
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


def _system_bool_keys() -> set[str]:
    return {
        "enableNotifications",
        "enableAuditLog",
        "enableTwoFactor",
        "enableChatbot",
        "enableForecasting",
    }


async def _ensure_system_config_table(db: AsyncSession) -> None:
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS system_config (
            config_key VARCHAR(100) PRIMARY KEY,
            config_value TEXT NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))


def _parse_stored_config(raw: Dict[str, str]) -> Dict[str, object]:
    merged = dict(DEFAULT_SYSTEM_CONFIG)
    bool_keys = _system_bool_keys()

    for key, value in raw.items():
        if key in bool_keys:
            merged[key] = str(value).lower() in {"true", "1", "yes", "on"}
        else:
            merged[key] = str(value)

    return merged


async def _load_system_config(db: AsyncSession) -> Dict[str, object]:
    await _ensure_system_config_table(db)
    result = await db.execute(text("""
        SELECT config_key, config_value
        FROM system_config
    """))
    rows = result.fetchall()

    if not rows:
        # Seed defaults once so subsequent reads are fully DB-driven.
        for key, value in DEFAULT_SYSTEM_CONFIG.items():
            await db.execute(text("""
                INSERT INTO system_config (config_key, config_value, updated_at)
                VALUES (:key, :value, NOW())
                ON CONFLICT (config_key)
                DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = NOW()
            """), {
                "key": key,
                "value": str(value).lower() if isinstance(value, bool) else str(value),
            })
        return dict(DEFAULT_SYSTEM_CONFIG)

    stored = {str(r.config_key): str(r.config_value) for r in rows}
    return _parse_stored_config(stored)


async def _save_system_config(db: AsyncSession, payload: Dict[str, object]) -> Dict[str, object]:
    await _ensure_system_config_table(db)
    bool_keys = _system_bool_keys()

    for key, value in payload.items():
        stored_value = str(value).lower() if key in bool_keys else str(value)
        await db.execute(text("""
            INSERT INTO system_config (config_key, config_value, updated_at)
            VALUES (:key, :value, NOW())
            ON CONFLICT (config_key)
            DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = NOW()
        """), {
            "key": key,
            "value": stored_value,
        })

    return await _load_system_config(db)


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
    role_value = _normalize_role(user.role)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role_value,
        "is_active": bool(user.is_active),
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
        role=_to_storage_role(payload.role),
        is_active=True,
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
    user.role = _to_storage_role(payload.role)
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
async def get_system_config(
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await _load_system_config(db)


@router.put("/config")
async def update_system_config(
    payload: SystemConfigRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await _save_system_config(db, payload.model_dump())
