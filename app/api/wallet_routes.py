from fastapi import APIRouter
from app.services.wallet_service import create_wallet, get_user_wallets
from app.schemas.wallet_schema import WalletCreateRequest

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.post("/create")
async def create(data: WalletCreateRequest):

    wallet = await create_wallet(data.user_id, data.currency)

    return {
        "message": "Wallet created",
        "wallet": wallet
    }


@router.get("/{user_id}")
async def wallets(user_id: str):

    wallets = await get_user_wallets(user_id)

    return wallets