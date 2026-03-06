from app.database import users_collection, transactions_collection


async def get_all_users():
    users = []
    
    # password exclude pannuvom
    async for user in users_collection.find({}, {"password": 0,"twofa_secret": 0}):
        user["_id"] = str(user["_id"])
        users.append(user)

    return users


async def get_all_transactions():
    transactions = []

    async for tx in transactions_collection.find():
        tx["_id"] = str(tx["_id"])
        transactions.append(tx)

    return transactions