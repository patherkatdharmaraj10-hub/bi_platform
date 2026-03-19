import re
from typing import Dict, List, Set, Tuple

from sqlalchemy import select, text

from core.config import settings
from core.database import AsyncSessionLocal, Base, engine
from core.security import hash_password
from models.customer import Customer  # noqa: F401
from models.inventory import Inventory, InventoryTransaction  # noqa: F401
from models.sales import Product, Sale  # noqa: F401
from models.user import User, UserRole

REQUIRED_TABLES: Tuple[str, ...] = (
    "users",
    "products",
    "sales",
    "customers",
    "inventory",
    "inventory_transactions",
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _database_username() -> str:
    # Keep parsing lightweight; expected URL format includes '://user:pass@'.
    tail = settings.DATABASE_URL.split("://", 1)[-1]
    creds = tail.split("@", 1)[0]
    username = creds.split(":", 1)[0]
    return username.strip()


async def ensure_user_schema() -> Dict[str, str]:
    username = _database_username()
    if not _IDENTIFIER_RE.match(username):
        return {
            "schema": "public",
            "status": "skipped",
            "reason": "username not a valid SQL identifier",
        }

    async with engine.begin() as conn:
        await conn.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{username}" AUTHORIZATION "{username}"')
        )

    return {
        "schema": username,
        "status": "ok",
    }


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Keep existing environments compatible by adding profile columns if missing.
        await conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS phone_number VARCHAR"))
        await conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS job_title VARCHAR"))
        await conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS department VARCHAR"))


async def seed_default_users() -> List[str]:
    created: List[str] = []
    defaults = [
        {
            "email": "admin@bi.com",
            "full_name": "Admin User",
            "password": "admin123",
            "role": UserRole.admin,
            "is_premium": True,
        },
        {
            "email": "analyst@bi.com",
            "full_name": "Data Analyst",
            "password": "analyst123",
            "role": UserRole.analyst,
            "is_premium": False,
        },
        {
            "email": "viewer@bi.com",
            "full_name": "View Only",
            "password": "viewer123",
            "role": UserRole.viewer,
            "is_premium": False,
        },
    ]

    async with AsyncSessionLocal() as db:
        for item in defaults:
            exists = await db.execute(select(User).where(User.email == item["email"]))
            if exists.scalar_one_or_none():
                continue

            db.add(
                User(
                    email=item["email"],
                    full_name=item["full_name"],
                    hashed_password=hash_password(item["password"]),
                    role=item["role"],
                    is_premium=item["is_premium"],
                )
            )
            created.append(item["email"])

        await db.commit()

    return created


async def get_database_status() -> Dict[str, object]:
    async with AsyncSessionLocal() as db:
        rows = await db.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema = ANY (current_schemas(true))
                """
            )
        )
        existing_tables: Set[str] = {r.table_name for r in rows.fetchall()}

        missing_tables = [t for t in REQUIRED_TABLES if t not in existing_tables]

        user_count = 0
        if "users" in existing_tables:
            count_row = await db.execute(text("SELECT COUNT(*) AS c FROM users"))
            user_count = int(count_row.scalar() or 0)

    return {
        "required_tables": list(REQUIRED_TABLES),
        "missing_tables": missing_tables,
        "is_ready": len(missing_tables) == 0,
        "existing_table_count": len(existing_tables),
        "user_count": user_count,
    }


async def bootstrap_database(ensure_schema_first: bool, seed_defaults: bool) -> Dict[str, object]:
    schema_result: Dict[str, str] = {"status": "skipped", "schema": "public"}
    if ensure_schema_first:
        schema_result = await ensure_user_schema()

    before = await get_database_status()
    await create_tables()

    created_users: List[str] = []
    if seed_defaults:
        created_users = await seed_default_users()

    after = await get_database_status()

    return {
        "schema": schema_result,
        "before": before,
        "after": after,
        "created_users": created_users,
    }
