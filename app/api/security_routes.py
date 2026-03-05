from fastapi import APIRouter
from app.core.twofa import verify_2fa

router = APIRouter(prefix="/security", tags=["Security"])


@router.post("/verify-2fa")
async def verify(secret: str, code: str):

    result = verify_2fa(secret, code)

    return {
        "valid": result
    }