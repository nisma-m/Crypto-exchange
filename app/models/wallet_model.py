from datetime import datetime
import uuid


def create_wallet_document(user_id: str, currency: str):

    address = None

    if currency in ["BTC", "ETH", "USDT"]:
        address = f"mock_{currency}_{uuid.uuid4().hex[:10]}"

    return {
        "user_id": user_id,
        "currency": currency,

        "balance": 0.0,
        "locked_balance": 0.0,

        "deposit_address": address,

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }