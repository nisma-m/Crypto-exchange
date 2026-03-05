# app/scripts/seed_candles.py
import asyncio
from datetime import datetime
from app.database import trading_candles_collection

async def seed_candles():
    # Example BTC-USD candle
    candle = {
        "symbol": "BTC-USD",
        "interval": "1m",
        "open": 30000,
        "high": 30100,
        "low": 29950,
        "close": 30050,
        "volume": 12.5,
        "timestamp": datetime.utcnow()
    }

    await trading_candles_collection.insert_one(candle)
    print("Inserted candle:", candle)

if __name__ == "__main__":
    asyncio.run(seed_candles())