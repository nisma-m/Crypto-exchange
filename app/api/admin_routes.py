from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
import io, csv
from io import StringIO
from app.core.jwt import get_current_admin
from app.services import admin_service
from app.database import users_collection, db
from app.services.admin_service import create_test_withdrawal, approve_withdrawal, reject_withdrawal
from app.schemas.admin_schema import MessageResponse
from app.api.admin_ws import broadcast_alert
from app.models.activity_log import create_activity_log
from app.core.roles import require_role
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import APIRouter, Depends
from app.core.roles import role_required
import traceback



router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

async def check_suspicious_withdrawal(user_id: str, amount: float):
    # Threshold: withdrawals > 50,000 flagged
    if amount > 50000:
        alert = {
            "type": "suspicious_withdrawal",
            "message": f"User {user_id} attempted withdrawal of {amount}",
            "status": "active",
            "timestamp": datetime.utcnow()
        }
        await db.alerts.insert_one(alert)


# -----------------------------
# User Routes
# -----------------------------

@router.get("/users", operation_id="get_all_users_service", dependencies=[Depends(require_role(["super_admin", "support_admin"]))])
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

@router.delete("/delete-user/{user_id}", operation_id="delete_user_service", dependencies=[Depends(require_role(["super_admin"]))])
async def delete_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
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


@router.put("/withdrawal/approve/{transaction_id}")
async def approve_withdrawal(
    transaction_id: str,
    admin_id: str,
    current_admin: dict = Depends(role_required("super_admin"))
):
    result = await admin_service.approve_withdrawal(transaction_id, admin_id)

    if not result:
        raise HTTPException(status_code=400, detail="Cannot approve withdrawal")

    return {"message": "Withdrawal approved successfully"}

# -----------------------------
# WITHDRAWAL REJECT ✅ FIXED
# -----------------------------
@router.put("/withdrawal/reject/{transaction_id}")
async def reject_withdrawal(
    transaction_id: str,
    admin_id: str,
    current_admin: dict = Depends(role_required("super_admin"))
):
    result = await admin_service.reject_withdrawal(transaction_id, admin_id)

    if not result:
        raise HTTPException(status_code=400, detail="Cannot reject withdrawal")

    return {"message": "Withdrawal rejected successfully"}
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
# Transactions
# -----------------------------

@router.get("/transactions/db")
async def get_transactions(current_admin: dict = Depends(get_current_admin)):
    transactions = []
    async for tx in db.transactions.find():
        tx["_id"] = str(tx["_id"])
        transactions.append(tx)
    return transactions

@router.get("/transactions/filter", operation_id="filter_transactions_service")
async def filter_transactions(
    type: str = None,
    status: str = None,
    user_id: str = None,
    current_admin: dict = Depends(get_current_admin)
):
    query = {}
    if type:
        query["type"] = type
    if status:
        query["status"] = status
    if user_id:
        query["user_id"] = user_id

    transactions = []
    async for tx in db.transactions.find(query):
        tx["_id"] = str(tx["_id"])  # Convert ObjectId to string
        transactions.append(tx)
    return transactions

@router.get("/transactions/export", operation_id="export_transactions_service")
async def export_transactions(current_admin: dict = Depends(get_current_admin)):
    try:
        transactions = []
        async for tx in db.transactions.find({}):
            tx["_id"] = str(tx["_id"])
            tx["user_id"] = str(tx.get("user_id", ""))
            tx["type"] = str(tx.get("type", ""))
            tx["status"] = str(tx.get("status", ""))
            tx["amount"] = str(tx.get("amount", ""))
            
            created_at = tx.get("created_at")
            if isinstance(created_at, datetime):
                tx["created_at"] = created_at.isoformat()
            else:
                tx["created_at"] = str(created_at or "")
            
            transactions.append(tx)

        output = StringIO()
        fieldnames = ["_id", "user_id", "type", "status", "amount", "created_at"]
        # ✅ ignore extra fields in the dict
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for tx in transactions:
            writer.writerow(tx)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions.csv"}
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
    
# -----------------------------
# Stats & Activity Logs
# -----------------------------

@router.get("/stats", operation_id="admin_stats_service", dependencies=[Depends(require_role(["super_admin", "auditor"]))])
async def admin_stats(current_admin: dict = Depends(get_current_admin)):
    total_users = await db.users.count_documents({})
    total_wallets = await db.wallets.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    return {
        "total_users": total_users,
        "total_wallets": total_wallets,
        "total_transactions": total_transactions,
    }

@router.get(
    "/activity/export",
    operation_id="export_activity_logs",
    dependencies=[Depends(require_role(["super_admin", "auditor"]))]
)
async def export_activity_logs(
    current_admin: dict = Depends(get_current_admin),
    from_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    action: str = Query(None, description="Filter by action type"),
    admin_id: str = Query(None, description="Filter by admin ID")
):
    query = {}

    # ✅ Safe date parsing
    if from_date or to_date:
        query["timestamp"] = {}
        try:
            if from_date:
                query["timestamp"]["$gte"] = datetime.strptime(from_date, "%Y-%m-%d")
            if to_date:
                query["timestamp"]["$lte"] = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if action:
        query["action"] = action
    if admin_id:
        query["admin_id"] = admin_id

    logs = []
    try:
        async for log in db.activity_logs.find(query):
            log["_id"] = str(log["_id"])
            log.setdefault("admin_id", "")
            log.setdefault("action", "")
            log.setdefault("target", "")
            log.setdefault("timestamp", "")
            logs.append(log)
    except Exception as e:
        # ✅ Catch DB errors clearly
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not logs:
        raise HTTPException(status_code=404, detail="No activity logs found for given filters")

    output = StringIO()
    fieldnames = ["_id", "admin_id", "action", "target", "timestamp"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for log in logs:
        writer.writerow({key: log.get(key, "") for key in fieldnames})
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=activity_logs.csv"}
    )

@router.get("/transactions", operation_id="list_transactions", dependencies=[Depends(require_role(["super_admin", "auditor"]))])
async def list_transactions(
    type: str = Query(None, description="Filter by transaction type (deposit/withdrawal)"),
    status: str = Query(None, description="Filter by status (pending/approved/rejected)"),
    user_id: str = Query(None, description="Filter by user ID"),
    from_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(None, description="End date in YYYY-MM-DD format")
):
    query = {}

    if type:
        query["type"] = type
    if status:
        query["status"] = status
    if user_id:
        query["user_id"] = user_id

    if from_date or to_date:
        query["timestamp"] = {}
        try:
            if from_date:
                query["timestamp"]["$gte"] = datetime.strptime(from_date, "%Y-%m-%d")
            if to_date:
                query["timestamp"]["$lte"] = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    transactions = []
    try:
        async for tx in db.transactions.find(query):
            tx["_id"] = str(tx["_id"])
            transactions.append(tx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found for given filters")

    return transactions

@router.get("/transactions/export")
async def export_transactions(current_admin: dict = Depends(get_current_admin)):
    transactions = await admin_service.get_all_transactions()

    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["_id", "user_id", "type", "status", "amount", "created_at"]
    )
    writer.writeheader()

    for tx in transactions:
        writer.writerow(tx)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )

@router.get("/users", operation_id="list_users", dependencies=[Depends(require_role(["super_admin", "moderator"]))])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by username or email")
):
    query = {}
    if search:
        query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]

    users = []
    try:
        async for user in db.users.find(query).skip(skip).limit(limit):
            user["_id"] = str(user["_id"])
            users.append(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    return users


@router.get("/users/export", operation_id="export_users", dependencies=[Depends(require_role(["super_admin", "moderator"]))])
async def export_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: str = Query(None, description="Search by username or email")
):
    query = {}
    if search:
        query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]

    users = []
    try:
        async for user in db.users.find(query).skip(skip).limit(limit):
            user["_id"] = str(user["_id"])
            users.append(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    output = StringIO()
    fieldnames = ["_id", "username", "email", "status", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for user in users:
        writer.writerow({key: user.get(key, "") for key in fieldnames})
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )

@router.get("/admin/alerts", operation_id="get_system_alerts", dependencies=[Depends(require_role(["super_admin", "moderator"]))])
async def get_system_alerts():
    alerts = []
    try:
        async for alert in db.alerts.find({}).sort("timestamp", -1):
            alert["_id"] = str(alert["_id"])
            alerts.append(alert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")

    return alerts

@router.post("/admin/alerts/resolve/{alert_id}", operation_id="resolve_alert", dependencies=[Depends(require_role(["super_admin"]))])
async def resolve_alert(alert_id: str):
    try:
        result = await db.alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"status": "resolved", "resolved_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert resolved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

