from pydantic import BaseModel, Field, validator
from typing import Literal, Optional

class OrderCreateRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user placing the order")
    symbol: str = Field(..., description="Trading pair, e.g., BTC/USD")
    side: Literal["buy", "sell"] = Field(..., description="Buy or sell order")
    type: Literal["limit", "market", "stop-limit"] = Field(..., description="Order type")
    quantity: float = Field(..., gt=0, description="Quantity of asset to trade")
    price: Optional[float] = Field(0.0, ge=0, description="Price per unit (for limit/stop-limit)")
    stop_price: Optional[float] = Field(0.0, ge=0, description="Stop price for stop-limit orders")

    @validator("price", always=True)
    def price_required_for_limit(cls, v, values):
        if values.get("type") in ["limit", "stop-limit"] and v <= 0:
            raise ValueError("Price must be > 0 for limit or stop-limit orders")
        return v

    @validator("stop_price", always=True)
    def stop_price_required_for_stop_limit(cls, v, values):
        if values.get("type") == "stop-limit" and v <= 0:
            raise ValueError("Stop price must be > 0 for stop-limit orders")
        return v