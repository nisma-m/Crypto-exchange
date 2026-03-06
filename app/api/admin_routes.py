from fastapi import APIRouter
from app.services import admin_service
from app.database import users_collection

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


@router.put("/suspend/{user_id}")
async def suspend_user(user_id: str):
    return await admin_service.suspend_user(user_id)


@router.put("/edit-user/{user_id}")
async def edit_user(user_id: str, email: str = None, kyc_verified: bool = None):

    update_data = {}

    if email is not None:
        update_data["email"] = email

    if kyc_verified is not None:
        update_data["kyc_verified"] = kyc_verified

    if not update_data:
        return {"message": "No fields provided"}

    result = await users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )

    if result.modified_count == 1:
        return {"message": "User updated successfully"}

    return {"message": "User not found"}


@router.put("/unsuspend/{user_id}")
async def unsuspend_user(user_id: str):
    return await admin_service.unsuspend_user(user_id)


@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    return await admin_service.delete_user(user_id)