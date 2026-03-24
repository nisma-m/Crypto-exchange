from fastapi import HTTPException
from app.database import users_collection
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.core.twofa import generate_2fa_secret
from app.models.user_model import create_user_document
from app.services.wallet_service import create_wallet


async def register_user(email: str, password: str):
    try:
        # check existing user
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            return {"error": "User already exists"}

        # hash password
        hashed_password = hash_password(password)

        # create user
        user = {
            "email": email,
            "password": hashed_password
        }

        await users_collection.insert_one(user)

        return {"email": email}

    except Exception as e:
        return {"error": str(e)}

    # create default wallets
    await create_wallet(user_id, "BTC")
    await create_wallet(user_id, "ETH")
    await create_wallet(user_id, "USDT")
    await create_wallet(user_id, "USD")

    return {
        "user_id": user_id,
        "twofa_secret": secret
    }


async def login_user(email: str, password: str):

    user = await users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 👇 check if account suspended
    if user.get("is_suspended") == True:
        raise HTTPException(status_code=403, detail="Account suspended by admin")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    user_id = str(user["_id"])

    token = create_access_token(user_id)

    return {
        "user_id": user_id,
        "access_token": token
    }