from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import jwt

from app.database import db
from app.core.security import verify_password, hash_password
from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -----------------------------
# Register
# -----------------------------
@router.post("/register")
async def register(email: str, password: str):
    existing = await db.admins.find_one({"username": email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(password)

    result = await db.admins.insert_one({
        "username": email,
        "password_hash": hashed_pw,
        "role": "super_admin",
        "is_suspended": False,
        "created_at": datetime.utcnow()
    })

    return {
        "message": "User registered successfully",
        "data": {
            "id": str(result.inserted_id),
            "username": email
        }
    }


# -----------------------------
# Login
# -----------------------------
@router.post("/login")
async def login(email: str, password: str):
    admin = await db.admins.find_one({"username": email})

    if not admin or not verify_password(password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if admin.get("is_suspended"):
        raise HTTPException(status_code=403, detail="Account suspended by admin")

    payload = {
        "sub": str(admin["_id"]),
        "role": admin["role"],
        "exp": datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer"
        }
    }