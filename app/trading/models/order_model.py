from datetime import datetime
from typing import Literal
from uuid import uuid4

def create_order_document(
    user_id: str,
    symbol: str,
    side: Literal["buy", "sell"],
    order_type: Literal["limit", "market", "stop-limit"],
    quantity: float,
    price: float = 0.0,
    stop_price: float = 0.0,
    fee_rate: float = 0.001  # default 0.1% fee
) -> dict:
    """
    Create a new order document for the order book.
    """
    return {
        "order_id": str(uuid4()),
        "user_id": user_id,
        "symbol": symbol.upper(),  # e.g., BTC/USD
        "side": side,              # 'buy' or 'sell'
        "type": order_type,        # 'limit', 'market', 'stop-limit'
        "quantity": quantity,      # total quantity
        "price": price,            # price per unit (0 for market orders)
        "stop_price": stop_price,  # for stop-limit orders
        "filled_quantity": 0.0,    # how much has been executed
        "status": "open",          # open, partially_filled, filled, canceled
        "fee_rate": fee_rate,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }