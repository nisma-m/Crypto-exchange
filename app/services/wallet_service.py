from app.database import wallets_collection
from app.models.wallet_model import create_wallet_document


async def create_wallet(user_id: str, currency: str):

    existing_wallet = await wallets_collection.find_one({
        "user_id": user_id,
        "currency": currency
    })

    if existing_wallet:
        existing_wallet["_id"] = str(existing_wallet["_id"])
        return existing_wallet

    wallet = create_wallet_document(user_id, currency)

    result = await wallets_collection.insert_one(wallet)

    wallet["_id"] = str(result.inserted_id)

    return wallet


async def get_user_wallets(user_id: str):

    wallets = await wallets_collection.find(
        {"user_id": user_id}
    ).to_list(100)

    # convert ObjectId for each wallet
    for wallet in wallets:
        wallet["_id"] = str(wallet["_id"])

    return wallets