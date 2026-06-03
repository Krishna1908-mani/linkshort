import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import admins_collection, create_indexes
from app.security import hash_password

settings = get_settings()


async def seed_admin():
    await create_indexes()
    email = settings.admin_email.lower()
    existing = await admins_collection.find_one({"email": email})
    if existing:
        print(f"Admin already exists: {email}")
        return
    await admins_collection.insert_one({
        "email": email,
        "password_hash": hash_password(settings.admin_password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
    })
    print("Admin created successfully")
    print(f"Email: {email}")
    print(f"Password: {settings.admin_password}")


if __name__ == "__main__":
    asyncio.run(seed_admin())
