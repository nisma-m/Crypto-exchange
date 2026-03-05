from datetime import datetime


def create_transaction_document(
    user_id: str,
    currency: str,
    amount: float,
    tx_type: str
):

    return {
        "user_id": user_id,
        "currency": currency,
        "amount": amount,

        "type": tx_type,
        "status": "pending",

        "tx_hash": None,

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }