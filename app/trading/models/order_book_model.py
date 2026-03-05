# crypto_exchange/app/trading/models/order_book_model.py
from datetime import datetime
from typing import Dict

def create_order_book_document(symbol: str) -> Dict:
    """
    Initialize order book for a trading pair.
    """
    return {
        "symbol": symbol.upper(),
        "bids": [],  # list of [price, quantity, order_id]
        "asks": [],  # list of [price, quantity, order_id]
        "updated_at": datetime.utcnow()
    }