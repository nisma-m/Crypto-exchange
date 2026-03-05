from pydantic import BaseModel, Field

class TradeResponse(BaseModel):
    trade_id: str = Field(..., description="Unique trade ID")
    symbol: str = Field(..., description="Trading pair, e.g., BTC/USD")
    buy_order_id: str = Field(..., description="Buy order ID")
    sell_order_id: str = Field(..., description="Sell order ID")
    quantity: float = Field(..., description="Quantity traded")
    price: float = Field(..., description="Price per unit")
    total: float = Field(..., description="Total value of the trade")
    buyer_id: str = Field(..., description="User ID of the buyer")
    seller_id: str = Field(..., description="User ID of the seller")
    fee: float = Field(..., description="Trading fee charged")
    created_at: str = Field(..., description="Timestamp of the trade")