from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import StreamingResponse
import io, csv
from app.core.jwt import get_current_admin

from app.services import admin_service
from app.database import users_collection, db
from app.services.admin_service import create_test_withdrawal, approve_withdrawal, reject_withdrawal
from app.schemas.admin_schema import MessageResponse
from app.api.admin_ws import broadcast_alert
from app.models.activity_log import create_activity_log

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# -----------------------------
# User Routes
# -----------------------------

@router.get("/users", operation_id="get_all_users_service")
async def get_all_users(current_admin: dict = Depends(get_current_admin)):
    return await admin_service.get_all_users()

@router.put("/suspend/{user_id}", operation_id="suspend_user_service")
async def suspend_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    if current_admin["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Only super_admin can suspend users."
        )
    result = await admin_service.suspend_user(user_id)
    await create_activity_log(
        admin_id=current_admin["sub"],
        action="SUSPEND_USER",
        description=f"Admin suspended user {user_id}",
        target_user_id=user_id
    )
    return result

@router.put("/unsuspend/{user_id}", operation_id="unsuspend_user_service")
async def unsuspend_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    if current_admin["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Only super_admin can unsuspend users."
        )
    result = await admin_service.unsuspend_user(user_id)
    await create_activity_log(
        admin_id=current_admin["sub"],
        action="UNSUSPEND_USER",
        description=f"Admin unsuspended user {user_id}",
        target_user_id=user_id
    )
    return result

@router.delete("/delete-user/{user_id}", operation_id="delete_user_service")
async def delete_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    if current_admin["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Only super_admin can delete users."
        )
    result = await admin_service.delete_user(user_id)
    await create_activity_log(
        admin_id=current_admin["sub"],
        action="DELETE_USER",
        description=f"Admin deleted user {user_id}",
        target_user_id=user_id
    )
    return result

@router.put("/edit-user/{user_id}", operation_id="edit_user_service")
async def edit_user(user_id: str, email: str = None, kyc_verified: bool = None, current_admin: dict = Depends(get_current_admin)):
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

# -----------------------------
# Deposit Routes
# -----------------------------

@router.get("/deposits/pending", operation_id="get_pending_deposits_service")
async def get_pending_deposits(current_admin: dict = Depends(get_current_admin)):
    return await admin_service.get_pending_deposits()

@router.put("/deposit/approve/{transaction_id}", operation_id="approve_deposit_service")
async def approve_deposit(transaction_id: str, admin_id: str, current_admin: dict = Depends(get_current_admin)):
    result = await admin_service.approve_deposit(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await broadcast_alert({
        "event": "deposit_approved",
        "transaction_id": transaction_id,
        "message": "Deposit approved successfully"
    })
    return {"message": "Deposit approved successfully"}

@router.put("/deposit/reject/{transaction_id}", operation_id="reject_deposit_service")
async def reject_deposit(transaction_id: str, admin_id: str, current_admin: dict = Depends(get_current_admin)):
    result = await admin_service.reject_deposit(transaction_id, admin_id)
    if result:
        return {"message": "Deposit rejected successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")

# -----------------------------
# Test Withdrawal
# -----------------------------

@router.post("/seed-test-withdrawal", response_model=MessageResponse)
async def seed_test_withdrawal(current_admin: dict = Depends(get_current_admin)):
    tx_id = await create_test_withdrawal()
    return {"message": f"Test withdrawal {tx_id} created"}

# -----------------------------
# Withdrawal Approval
# -----------------------------

@router.put("/withdrawal/approve/{transaction_id}", response_model=MessageResponse)
async def approve_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...), current_admin: dict = Depends(get_current_admin)):
    result = await approve_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot approve withdrawal")
    return {"message": "Withdrawal approved successfully"}

@router.put("/withdrawal/reject/{transaction_id}", response_model=MessageResponse)
async def reject_withdrawal_endpoint(transaction_id: str, admin_id: str = Query(...), current_admin: dict = Depends(get_current_admin)):
    result = await reject_withdrawal(transaction_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Withdrawal rejected successfully"}

# -----------------------------
# Trades
# -----------------------------

@router.get("/trades", operation_id="get_all_trades_service")
async def get_all_trades(current_admin: dict = Depends(get_current_admin)):
    return await admin_service.get_all_trades()

@router.get("/trades/export", operation_id="export_trades_service")
async def export_trades(current_admin: dict = Depends(get_current_admin)):
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

# -----------------------------
# Transactions from DB
# -----------------------------

@router.get("/transactions/db")
async def get_transactions(current_admin: dict = Depends(get_current_admin)):
    transactions = []
    async for tx in db.transactions.find():
        tx["_id"] = str(tx["_id"])
        transactions.append(tx)
    return transactions

# -----------------------------
# Admin Stats
# -----------------------------

@router.get("/stats", operation_id="admin_stats_service")
async def admin_stats(current_admin: dict = Depends(get_current_admin)):
    total_users = await db.users.count_documents({})
    total_wallets = await db.wallets.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    total_trades = await db.trades.count_documents({})
    pending_deposits = await db.transactions.count_documents({
        "type": "deposit",
        "status": "pending"
    })
    pending_withdrawals = await db.transactions.count_documents({
        "type": "withdrawal",
        "status": "pending"
    })
    return {
        "total_users": total_users,
        "total_wallets": total_wallets,
        "total_transactions": total_transactions,
        "total_trades": total_trades,
        "pending_deposits": pending_deposits,
        "pending_withdrawals": pending_withdrawals
    }

# -----------------------------
# WebSocket Test Alert
# -----------------------------

@router.get("/test-alert", operation_id="test_alert_service")
async def test_alert(current_admin: dict = Depends(get_current_admin)):
    await broadcast_alert({
        "event": "test_alert",
        "message": "WebSocket working!"
    })
    return {"status": "alert sent"}

# -----------------------------
# Activity Logs
# -----------------------------

@router.get("/activity-logs")
async def get_activity_logs(current_admin: dict = Depends(get_current_admin)):
    logs = await db.activity_logs.find().sort("created_at", -1).to_list(length=100)
    # Convert ObjectId to string
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs