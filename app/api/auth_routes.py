from fastapi import APIRouter, HTTPException
from app.services.auth_service import register_user, login_user

# ❌ REMOVE prefix="/auth"
router = APIRouter(tags=["Authentication"])


@router.post("/register")
async def register(email: str, password: str):

    result = await register_user(email, password)

    # optional error handling
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "User registered successfully",
        "data": result
    }


@router.post("/login")
async def login(email: str, password: str):

    result = await login_user(email, password)

    # handle error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "Login successful",
        "data": result
    }