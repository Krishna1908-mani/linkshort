from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from ..database import admins_collection
from ..schemas import LoginRequest, TokenResponse
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    admin = await admins_collection.find_one({"email": payload.email.lower()})
    if not admin or not verify_password(payload.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    await admins_collection.update_one(
        {"_id": admin["_id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    token = create_access_token(payload.email.lower(), admin.get("role", "admin"))
    return TokenResponse(access_token=token)
