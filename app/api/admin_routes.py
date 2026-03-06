from fastapi import APIRouter
from app.services import admin_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/users")
async def get_all_users():
    return await admin_service.get_all_users()


@router.get("/transactions")
async def get_all_transactions():
    return await admin_service.get_all_transactions()