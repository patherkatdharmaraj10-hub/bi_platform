import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.database import AsyncSessionLocal
from core.security import hash_password, verify_password
from sqlalchemy import text


async def reset():
    EMAIL    = "admin@bi.com"
    PASSWORD = "admin123"

    hashed = hash_password(PASSWORD)
    verified = verify_password(PASSWORD, hashed)
    print(f"Hash verify: {verified}")

    async with AsyncSessionLocal() as db:
        await db.execute(
            text("UPDATE users SET hashed_password = :h WHERE email = :e"),
            {"h": hashed, "e": EMAIL}
        )
        await db.commit()
        print(f"✅ Password reset!")
        print(f"   Email:    {EMAIL}")
        print(f"   Password: {PASSWORD}")


asyncio.run(reset())