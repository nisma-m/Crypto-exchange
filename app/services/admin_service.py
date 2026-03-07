from bson import ObjectId
from app.database import users_collection, transactions_collection
import datetime
import uuid

# -----------------------------
# User Management
# -----------------------------

async def get_all_users():
    users = []
    async for user in users_collection.find({}, {"password": 0, "twofa_secret": 0}):
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

async def get_all_transactions():
    transactions = []
    async for tx in transactions_collection.find():
        tx["_id"] = str(tx["_id"])
        transactions.append(tx)
    return transactions

async def suspend_user(user_id: str):
    result = await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"is_suspended": True}}
    )
    if result.modified_count == 0:
        return {"message": "User not found"}
    return {"message": "User suspended successfully"}

async def unsuspend_user(user_id: str):
    result = await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"is_suspended": False}}
    )
    if result.modified_count == 1:
        return {"message": "User unsuspended successfully"}
    return {"message": "User not found"}

async def delete_user(user_id: str):
    result = await users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}

# -----------------------------
# Deposit Approval Logic
# -----------------------------

async def get_pending_deposits():
    deposits = []
    async for tx in transactions_collection.find({"type": "deposit", "status": "pending"}):
        tx["_id"] = str(tx["_id"])
        deposits.append(tx)
    return deposits

async def approve_deposit(transaction_id: str, admin_id: str):
    result = await transactions_collection.update_one(
        {"transaction_id": transaction_id, "status": "pending"},
        {"$set": {
            "status": "approved",
            "approved_by": admin_id,
            "approved_at": datetime.datetime.utcnow()
        }}
    )
    return result.modified_count == 1

async def reject_deposit(transaction_id: str, admin_id: str):
    result = await transactions_collection.update_one(
        {"transaction_id": transaction_id, "status": "pending"},
        {"$set": {
            "status": "rejected",
            "approved_by": admin_id,
            "approved_at": datetime.datetime.utcnow()
        }}
    )
    return result.modified_count == 1

# -----------------------------
# Test Withdrawal
# -----------------------------

async def create_test_withdrawal():
    tx_id = f"tx_withdraw_{uuid.uuid4().hex[:8]}"
    await transactions_collection.insert_one({
        "transaction_id": tx_id,
        "user_id": "user_test",
        "type": "withdrawal",
        "amount": 500,
        "status": "pending",
        "created_at": datetime.datetime.utcnow(),
        "approved_by": None,
        "approved_at": None
    })
    return tx_id

# -----------------------------
# Withdrawal Approval Logic
# -----------------------------

async def approve_withdrawal(transaction_id: str, admin_id: str):
    withdrawal = await transactions_collection.find_one({
        "transaction_id": transaction_id,
        "type": "withdrawal",
        "status": "pending"
    })

    if not withdrawal:
        return False

    user = await users_collection.find_one({"user_id": withdrawal["user_id"]})
    if not user:
        return False

    balance = user.get("balance", 0)
    if balance < withdrawal["amount"]:
        return False

    await users_collection.update_one(
        {"user_id": withdrawal["user_id"]},
        {"$set": {"balance": balance - withdrawal["amount"]}}
    )

    await transactions_collection.update_one(
        {"transaction_id": transaction_id},
        {"$set": {
            "status": "approved",
            "approved_by": admin_id,
            "approved_at": datetime.datetime.utcnow()
        }}
    )

    return True

async def reject_withdrawal(transaction_id: str, admin_id: str):
    result = await transactions_collection.update_one(
        {"transaction_id": transaction_id, "type": "withdrawal", "status": "pending"},
        {"$set": {
            "status": "rejected",
            "approved_by": admin_id,
            "approved_at": datetime.datetime.utcnow()
        }}
    )
    return result.modified_count > 0