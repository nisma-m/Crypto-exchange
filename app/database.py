from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DATABASE_NAME]

# ------------------------------
# Core collections
# ------------------------------
users_collection = db["users"]
wallets_collection = db["wallets"]
transactions_collection = db["transactions"]
ledger_collection = db["ledger"]

# ------------------------------
# Trading collections
# ------------------------------
trading_orders_collection = db["trading_orders"]
trading_trades_collection = db["trading_trades"]
trading_candles_collection = db["trading_candles"]

# ------------------------------
# Indexes
# ------------------------------
async def create_indexes():
    await users_collection.create_index("email", unique=True)
    await wallets_collection.create_index(
        [("user_id", 1), ("currency", 1)],
        unique=True
    )
    await trading_orders_collection.create_index("order_id", unique=True)
    await trading_trades_collection.create_index("trade_id", unique=True)