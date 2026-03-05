from datetime import datetime
from uuid import uuid4

def create_trade_document(
    buy_order_id: str,
    sell_order_id: str,
    symbol: str,
    quantity: float,
    price: float,
    buyer_id: str,
    seller_id: str,
    fee_rate: float = 0.001
) -> dict:
    """
    Create a trade document when two orders are matched.
    """
    trade_id = str(uuid4())
    fee = quantity * price * fee_rate

    return {
        "trade_id": trade_id,
        "symbol": symbol.upper(),
        "buy_order_id": buy_order_id,
        "sell_order_id": sell_order_id,
        "quantity": quantity,
        "price": price,
        "total": quantity * price,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "fee": fee,
        "created_at": datetime.utcnow()
    }