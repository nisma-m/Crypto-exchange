from fastapi import APIRouter, HTTPException, Form
from datetime import datetime

from app.database import db
from app.core.security import verify_password, hash_password
from app.services.auth_service import register_user, login_user

# -----------------------------
# Router
# -----------------------------
router = APIRouter(tags=["Authentication"])


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
# Login (Service-based - CLEAN OPTION 3)
# -----------------------------
@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    result = await login_user(username, password)

    # handle service error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "Login successful",
        "data": result
    }