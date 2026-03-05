# crypto_exchange/app/trading/models/market_data_model.py
from datetime import datetime
from typing import Dict

def create_candle_document(
    symbol: str,
    interval: str,   # e.g., '1m', '5m', '1h'
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    volume: float
) -> Dict:
    """
    Candlestick data for price charts.
    """
    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
        "volume": volume,
        "timestamp": datetime.utcnow()
    }