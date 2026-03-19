import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import AsyncSessionLocal
from sqlalchemy import text
from core.security import hash_password


async def change_password(email: str, new_password: str):
    hashed = hash_password(new_password)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT id, full_name FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if not user:
            print(f"❌ User {email} not found!")
            return

        await db.execute(
            text("""
                UPDATE users
                SET hashed_password = :pwd
                WHERE email = :email
            """),
            {"pwd": hashed, "email": email}
        )
        await db.commit()
        print("✅ Password changed successfully!")
        print(f"   Name:     {user.full_name}")
        print(f"   Email:    {email}")
        print(f"   Password: {new_password}")


if __name__ == "__main__":
    # ── Change these two values ───────────────────────────
    EMAIL        = "admin@bi.com"
    NEW_PASSWORD = "MyNewPassword135"
    # ─────────────────────────────────────────────────────

    asyncio.run(change_password(EMAIL, NEW_PASSWORD))