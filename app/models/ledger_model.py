from datetime import datetime


def create_ledger_entry(
    user_id: str,
    currency: str,
    amount: float,
    entry_type: str,
    reference_id: str
):

    return {
        "user_id": user_id,
        "currency": currency,

        "amount": amount,

        "entry_type": entry_type,

        "reference_id": reference_id,

        "created_at": datetime.utcnow()
    }