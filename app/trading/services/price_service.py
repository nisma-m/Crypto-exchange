# crypto_exchange/app/trading/services/price_service.py
from app.database import trading_trades_collection
from datetime import datetime

async def get_last_price(symbol: str) -> float:
    """
    Return last traded price for a symbol.
    """
    last_trade = await trading_trades_collection.find({"symbol": symbol}).sort("created_at",-1).to_list(1)
    if not last_trade:
        return 0.0
    return last_trade[0]["price"]

async def get_candle(symbol: str, interval: str):
    """
    Generate OHLC candle for given interval.
    """
    # For simplicity, just return last trade price as candle
    last_trade = await trading_trades_collection.find({"symbol": symbol}).sort("created_at",-1).to_list(1)
    if not last_trade:
        return None
    trade = last_trade[0]
    return {
        "symbol": symbol,
        "interval": interval,
        "open": trade["price"],
        "high": trade["price"],
        "low": trade["price"],
        "close": trade["price"],
        "volume": trade["quantity"],
        "timestamp": datetime.utcnow()
    }