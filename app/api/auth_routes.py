from fastapi import APIRouter
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(email: str, password: str):

    result = await register_user(email, password)

    return {
        "message": "User registered successfully",
        "data": result
    }


@router.post("/login")
async def login(email: str, password: str):

    token = await login_user(email, password)

    return {
        "message": "Login successful",
        "data": token
    }