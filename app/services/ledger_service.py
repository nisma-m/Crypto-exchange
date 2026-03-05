from app.database import ledger_collection
from app.models.ledger_model import create_ledger_entry


async def record_ledger_entry(
    user_id: str,
    currency: str,
    amount: float,
    entry_type: str,
    reference_id: str
):

    entry = create_ledger_entry(
        user_id,
        currency,
        amount,
        entry_type,
        reference_id
    )

    await ledger_collection.insert_one(entry)

    return entry