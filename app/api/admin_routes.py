# crypto_exchange/app/api/admin_routes.py
from fastapi import APIRouter, HTTPException, Query
from app.services import admin_service
from app.database import users_collection
from app.services.admin_service import create_test_withdrawal, approve_withdrawal, reject_withdrawal
from app.schemas.admin_schema import MessageResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# -----------------------------
# User Routes
# -----------------------------

@router.get("/users")
async def get_all_users():
    return await admin_service.get_all_users()

@router.get("/transactions")
async def get_all_transactions():
    return await admin_service.get_all_transactions()

@router.put("/suspend/{user_id}")
async def suspend_user(user_id: str):
    return await admin_service.suspend_user(user_id)

@router.put("/unsuspend/{user_id}")
async def unsuspend_user(user_id: str):
    return await admin_service.unsuspend_user(user_id)

@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    return await admin_service.delete_user(user_id)

# -----------------------------
# Deposit Routes
# -----------------------------

@router.get("/deposits/pending")
async def get_pending_deposits():
    return await admin_service.get_pending_deposits()

@router.put("/deposit/approve/{transaction_id}")
async def approve_deposit(transaction_id: str, admin_id: str):
    result = await admin_service.approve_deposit(transaction_id, admin_id)
    if result:
        return {"message": "Deposit approved successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/deposit/reject/{transaction_id}")
async def reject_deposit(transaction_id: str, admin_id: str):
    result = await admin_service.reject_deposit(transaction_id, admin_id)
    if result:
        return {"message": "Deposit rejected successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")

# -----------------------------
# Test Withdrawal
# -----------------------------

@router.post("/seed-test-withdrawal", response_model=MessageResponse)
async def seed_test_withdrawal():
    tx_id = await create_test_withdrawal()
    return {"message": f"Test withdrawal {tx_id} created"}

# -----------------------------
# Withdrawal Approval
# -----------------------------

@router.put("/withdrawal/approve/{transaction_id}", response_model=MessageResponse)
async def approve_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...)):
    result = await approve_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot approve withdrawal (insufficient funds or not found)")
    return {"message": "Withdrawal approved successfully"}

@router.put("/withdrawal/reject/{transaction_id}", response_model=MessageResponse)
async def reject_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...)):
    result = await reject_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Withdrawal rejected successfully"}