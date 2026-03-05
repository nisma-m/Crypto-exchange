# app/services/transaction_service.py

from datetime import datetime
from typing import Dict, List

from app.database import transactions_collection, wallets_collection, ledger_collection
from app.models.transaction_model import create_transaction_document
from app.models.ledger_model import create_ledger_entry
from app.websocket.connection_manager import manager

# ------------------------------
# Real-time WebSocket notifier
# ------------------------------
async def notify_user(user_id: str, message: str):
    """
    Send a real-time notification to a connected user via WebSocket.
    """
    await manager.send_personal_message(user_id, {
        "type": "notification",
        "message": message
    })

# ------------------------------
# Ledger entry
# ------------------------------
async def record_ledger_entry(
    user_id: str,
    currency: str,
    amount: float,
    entry_type: str,
    reference_id: str
) -> Dict:
    """
    Create a ledger entry for accounting purposes.
    """
    entry = create_ledger_entry(user_id, currency, amount, entry_type, reference_id)
    await ledger_collection.insert_one(entry)
    return entry

# ------------------------------
# Deposit
# ------------------------------
async def create_deposit(user_id: str, currency: str, amount: float) -> Dict:
    """
    Create a deposit transaction, update wallet balance, ledger, and notify user.
    """
    # 1️⃣ Create transaction
    tx = create_transaction_document(
        user_id=user_id,
        currency=currency,
        amount=amount,
        tx_type="deposit"
    )

    # Mark completed for dev purposes
    tx["status"] = "completed"

    result = await transactions_collection.insert_one(tx)
    tx["_id"] = str(result.inserted_id)

    # 2️⃣ Update wallet balance
    await wallets_collection.update_one(
        {"user_id": user_id, "currency": currency},
        {"$inc": {"balance": amount}, "$set": {"updated_at": datetime.utcnow()}}
    )

    # 3️⃣ Record ledger entry
    await record_ledger_entry(user_id, currency, amount, "credit", tx["_id"])

    # 4️⃣ Notify user
    await notify_user(user_id, f"Deposit of {amount} {currency} completed")

    return tx

# ------------------------------
# Withdraw
# ------------------------------
async def create_withdraw(user_id: str, currency: str, amount: float) -> Dict:
    """
    Create a withdrawal transaction, deduct wallet balance, record ledger, and notify user.
    """
    # 1️⃣ Check wallet balance
    wallet = await wallets_collection.find_one({"user_id": user_id, "currency": currency})
    if not wallet:
        raise Exception("Wallet not found")
    if wallet["balance"] < amount:
        raise Exception("Insufficient balance")

    # 2️⃣ Create transaction
    tx = create_transaction_document(
        user_id=user_id,
        currency=currency,
        amount=amount,
        tx_type="withdraw"
    )
    tx["status"] = "completed"  # Dev: mark completed, in prod could be "pending"

    result = await transactions_collection.insert_one(tx)
    tx["_id"] = str(result.inserted_id)

    # 3️⃣ Deduct wallet balance
    await wallets_collection.update_one(
        {"user_id": user_id, "currency": currency},
        {"$inc": {"balance": -amount}, "$set": {"updated_at": datetime.utcnow()}}
    )

    # 4️⃣ Record ledger entry
    await record_ledger_entry(user_id, currency, amount, "debit", tx["_id"])

    # 5️⃣ Notify user
    await notify_user(user_id, f"Withdrawal of {amount} {currency} completed")

    return tx

# ------------------------------
# Transaction History
# ------------------------------
async def get_user_transactions(user_id: str) -> List[Dict]:
    """
    Fetch all transactions for a user.
    """
    txs = await transactions_collection.find({"user_id": user_id}).to_list(length=100)
    for tx in txs:
        tx["_id"] = str(tx["_id"])
    return txs