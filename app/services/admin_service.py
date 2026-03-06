from app.database import users_collection, transactions_collection


async def get_all_users():
    users = []

    # password and 2FA secret hide pannuvom
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

    result = await users_collection.delete_one(
        {"user_id": user_id}
    )

    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}

    return {"message": "User not found"}