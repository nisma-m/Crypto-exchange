# app/trading/models/candle_model.py
from pydantic import BaseModel
from datetime import datetime

class Candle(BaseModel):
    symbol: str
    interval: str          # "1m", "5m", "1h", etc.
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime