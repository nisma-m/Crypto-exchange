# crypto_exchange/app/trading/services/order_book_service.py
from typing import List, Dict
from app.trading.models.trade_model import create_trade_document
from app.trading.websocket.trading_connection_manager import manager, normalize_symbol

# In-memory order books
order_books: Dict[str, Dict[str, List]] = {}

# -----------------------------
# Add order to order book
# -----------------------------
async def add_order_to_book(order: dict):
    symbol = normalize_symbol(order["symbol"])  # always normalize
    order["symbol"] = symbol  # update order with normalized symbol
    side = order["side"]

    if symbol not in order_books:
        order_books[symbol] = {"bids": [], "asks": []}

    if side == "buy":
        order_books[symbol]["bids"].append(order)
        order_books[symbol]["bids"].sort(key=lambda x: (-x["price"], x["created_at"]))
    else:
        order_books[symbol]["asks"].append(order)
        order_books[symbol]["asks"].sort(key=lambda x: (x["price"], x["created_at"]))

    # Notify WebSocket clients
    await manager.broadcast_order_book(symbol, order_books[symbol])

# -----------------------------
# Match orders
# -----------------------------
async def match_order(order: Dict) -> List[Dict]:
    """
    Match a new order with opposite side orders.
    Returns list of trades.
    """
    symbol = normalize_symbol(order["symbol"])  # normalize here too
    order["symbol"] = symbol  # update order

    side = order["side"]
    trades: List[Dict] = []

    if symbol not in order_books:
        return trades

    bids = order_books[symbol]["bids"]
    asks = order_books[symbol]["asks"]
    opposite = asks if side == "buy" else bids

    i = 0
    while i < len(opposite) and order["quantity"] > 0:
        opp = opposite[i]
        match_price = opp["price"] if order["type"] != "market" else opp["price"]

        if (side == "buy" and order["price"] >= match_price) or \
           (side == "sell" and order["price"] <= match_price) or \
           order["type"] == "market":

            traded_qty = min(order["quantity"], opp["quantity"] - opp["filled_quantity"])
            if traded_qty <= 0:
                i += 1
                continue

            # Update filled quantities
            order["filled_quantity"] += traded_qty
            opp["filled_quantity"] += traded_qty
            order["status"] = "filled" if order["filled_quantity"] >= order["quantity"] else "partially_filled"
            opp["status"] = "filled" if opp["filled_quantity"] >= opp["quantity"] else "partially_filled"

            # Create trade document
            trade = create_trade_document(
                buy_order_id=order["order_id"] if side=="buy" else opp["order_id"],
                sell_order_id=opp["order_id"] if side=="buy" else order["order_id"],
                symbol=symbol,
                quantity=traded_qty,
                price=match_price,
                buyer_id=order["user_id"] if side=="buy" else opp["user_id"],
                seller_id=opp["user_id"] if side=="buy" else order["user_id"],
                fee_rate=order["fee_rate"]
            )
            trades.append(trade)

            # Remove filled orders
            if opp["status"] == "filled":
                opposite.pop(i)
            else:
                i += 1
            if order["status"] == "filled":
                break
        else:
            break

    return trades