from fastapi import APIRouter
from app.services.transaction_service import (
    create_deposit,
    create_withdraw,
    get_user_transactions
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/deposit")
async def deposit(user_id: str, currency: str, amount: float):

    tx = await create_deposit(user_id, currency, amount)

    return {
        "message": "Deposit request created",
        "transaction": tx
    }


@router.post("/withdraw")
async def withdraw(user_id: str, currency: str, amount: float):

    tx = await create_withdraw(user_id, currency, amount)

    return {
        "message": "Withdrawal request created",
        "transaction": tx
    }


@router.get("/{user_id}")
async def history(user_id: str):

    txs = await get_user_transactions(user_id)

    return txs