# crypto_exchange/app/trading/routes/trading_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.trading.services.trading_service import place_order
from app.trading.services.order_book_service import order_books
from app.trading.services.price_service import get_last_price, get_candle
from app.database import trading_trades_collection

router = APIRouter(prefix="/trading", tags=["Trading"])

# Example normalization function
def normalize_symbol(symbol: str) -> str:
    return symbol.upper().replace("/", "-")
# -----------------------------
# Request Schemas
# -----------------------------
class PlaceOrderRequest(BaseModel):
    user_id: str
    symbol: str
    side: str                   # "buy" or "sell"
    type: str                   # "limit", "market", "stop-limit"
    quantity: float
    price: Optional[float] = 0.0
    stop_price: Optional[float] = 0.0

# -----------------------------
# Response Schemas
# -----------------------------
class OrderBookResponse(BaseModel):
    symbol: str
    bids: List[dict]
    asks: List[dict]

class LastPriceResponse(BaseModel):
    symbol: str
    last_price: float

class CandleResponse(BaseModel):
    symbol: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime

class TradeResponse(BaseModel):
    trade_id: str
    symbol: str
    buy_order_id: str
    sell_order_id: str
    quantity: float
    price: float
    total: float
    buyer_id: str
    seller_id: str
    fee: float
    created_at: datetime

# -----------------------------
# Place an order
# -----------------------------
@router.post("/order")
async def create_order(request: PlaceOrderRequest):
    try:
        result = await place_order(
            user_id=request.user_id,
            symbol=request.symbol.upper(),
            side=request.side.lower(),
            order_type=request.type.lower(),
            quantity=request.quantity,
            price=request.price,
            stop_price=request.stop_price
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# Get Order Book
# -----------------------------
# trading_routes.py
@router.get("/order-book/{symbol}", response_model=OrderBookResponse)
async def get_order_book(symbol: str):
    norm_symbol = normalize_symbol(symbol)
    if norm_symbol not in order_books:
        return {"symbol": symbol, "bids": [], "asks": []}
    return {"symbol": symbol, "bids": order_books[norm_symbol]["bids"], "asks": order_books[norm_symbol]["asks"]}
# -----------------------------
# Get Last Price
# -----------------------------
@router.get("/price/{symbol}", response_model=LastPriceResponse)
async def last_price(symbol: str):
    norm_symbol = normalize_symbol(symbol)
    price = await get_last_price(norm_symbol)
    return {"symbol": symbol.upper(), "last_price": price}


# -----------------------------
# Get OHLC Candle
# -----------------------------
from app.trading.models.candle_model import Candle
from app.database import trading_candles_collection


@router.get("/candle/{symbol}", response_model=Candle)
async def candle(symbol: str, interval: str = "1m"):
    norm_symbol = normalize_symbol(symbol)
    candle_data = await trading_candles_collection.find_one({
        "symbol": norm_symbol,
        "interval": interval
    })
    if not candle_data:
        raise HTTPException(status_code=404, detail="No data available")
    
    return Candle(**candle_data)


# -----------------------------
# Get Recent Trades
# -----------------------------
@router.get("/trades/{symbol}", response_model=List[TradeResponse])
async def recent_trades(symbol: str, limit: int = Query(50)):
    norm_symbol = normalize_symbol(symbol)
    trades = await trading_trades_collection.find({"symbol": norm_symbol}) \
        .sort("created_at", -1) \
        .to_list(limit)
    return trades