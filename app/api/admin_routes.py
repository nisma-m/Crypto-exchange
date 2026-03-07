from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import io, csv, json

from app.services import admin_service
from app.database import users_collection, db
from app.services.admin_service import create_test_withdrawal, approve_withdrawal, reject_withdrawal
from app.schemas.admin_schema import MessageResponse
from app.api.admin_ws import broadcast_alert

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# -----------------------------
# User Routes
# -----------------------------

@router.get("/users", operation_id="get_all_users_service")
async def get_all_users():
    return await admin_service.get_all_users()

@router.get("/transactions/service", operation_id="get_all_transactions_service")
async def get_all_transactions():
    return await admin_service.get_all_transactions()

@router.put("/suspend/{user_id}", operation_id="suspend_user_service")
async def suspend_user(user_id: str):
    return await admin_service.suspend_user(user_id)

@router.put("/edit-user/{user_id}", operation_id="edit_user_service")
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

@router.put("/unsuspend/{user_id}", operation_id="unsuspend_user_service")
async def unsuspend_user(user_id: str):
    return await admin_service.unsuspend_user(user_id)

@router.delete("/delete-user/{user_id}", operation_id="delete_user_service")
async def delete_user(user_id: str):
    return await admin_service.delete_user(user_id)

# -----------------------------
# Deposit Routes
# -----------------------------

@router.get("/deposits/pending", operation_id="get_pending_deposits_service")
async def get_pending_deposits():
    return await admin_service.get_pending_deposits()

@router.put("/deposit/approve/{transaction_id}", operation_id="approve_deposit_service")
async def approve_deposit(transaction_id: str, admin_id: str):
    result = await admin_service.approve_deposit(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Broadcast alert after approval
    await broadcast_alert({
        "event": "deposit_approved",
        "transaction_id": transaction_id
    })
    return {"message": "Deposit approved successfully"}

@router.put("/deposit/reject/{transaction_id}", operation_id="reject_deposit_service")
async def reject_deposit(transaction_id: str, admin_id: str):
    result = await admin_service.reject_deposit(transaction_id, admin_id)
    if result:
        return {"message": "Deposit rejected successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")

# -----------------------------
# Test Withdrawal
# -----------------------------

@router.post("/seed-test-withdrawal", response_model=MessageResponse, operation_id="seed_test_withdrawal_service")
async def seed_test_withdrawal():
    tx_id = await create_test_withdrawal()
    return {"message": f"Test withdrawal {tx_id} created"}

# -----------------------------
# Withdrawal Approval
# -----------------------------

@router.put("/withdrawal/approve/{transaction_id}", response_model=MessageResponse, operation_id="approve_withdrawal_service")
async def approve_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...)):
    result = await approve_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot approve withdrawal")
    return {"message": "Withdrawal approved successfully"}

@router.put("/withdrawal/reject/{transaction_id}", response_model=MessageResponse, operation_id="reject_withdrawal_service")
async def reject_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...)):
    result = await reject_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Withdrawal rejected successfully"}

# -----------------------------
# Trades
# -----------------------------

@router.get("/trades", operation_id="get_all_trades_service")
async def get_all_trades():
    return await admin_service.get_all_trades()

@router.get("/trades/export", operation_id="export_trades_service")
async def export_trades():
    trades = await admin_service.get_all_trades()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id","symbol","price","quantity","side","timestamp"])
    for trade in trades:
        writer.writerow([
            trade.get("user_id"),
            trade.get("symbol"),
            trade.get("price"),
            trade.get("quantity"),
            trade.get("side"),
            trade.get("timestamp")
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition":"attachment; filename=trade_report.csv"}
    )

@router.get("/transactions/db", operation_id="get_transactions_db")
def get_transactions():
    transactions = []
    for tx in db.transactions.find():
        tx["_id"] = str(tx["_id"])
        transactions.append(tx)
    return transactions

@router.get("/stats", operation_id="admin_stats_service")
async def admin_stats():
    total_users = await db.users.count_documents({})
    total_wallets = await db.wallets.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    total_trades = await db.trades.count_documents({})
    pending_deposits = await db.transactions.count_documents({"type": "deposit","status": "pending"})
    pending_withdrawals = await db.transactions.count_documents({"type": "withdrawal","status": "pending"})
    return {
        "total_users": total_users,
        "total_wallets": total_wallets,
        "total_transactions": total_transactions,
        "total_trades": total_trades,
        "pending_deposits": pending_deposits,
        "pending_withdrawals": pending_withdrawals
    }

# -----------------------------
# Test Alert
# -----------------------------

@router.get("/test-alert", operation_id="test_alert_service")
async def test_alert():
    await broadcast_alert({
        "event": "test_alert",
        "message": "WebSocket working!"
    })
    return {"status": "alert sent"}

@router.put("/deposit/approve/{transaction_id}", operation_id="approve_deposit_service")
async def approve_deposit(transaction_id: str, admin_id: str):
    result = await admin_service.approve_deposit(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Broadcast alert after approval
    await broadcast_alert({
        "event": "deposit_approved",
        "transaction_id": transaction_id,
        "message": "Deposit approved successfully"
    })

    return {"message": "Deposit approved successfully"}

