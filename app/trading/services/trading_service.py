# crypto_exchange/app/trading/services/trading_service.py
from datetime import datetime
from typing import List
from app.trading.models.order_model import create_order_document
from app.trading.models.trade_model import create_trade_document
from app.trading.services.order_book_service import add_order_to_book, match_order
from app.database import trading_orders_collection, trading_trades_collection

# -----------------------------
# Order Placement
# -----------------------------
async def place_order(
    user_id: str,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = 0.0,
    stop_price: float = 0.0,
    fee_rate: float = 0.001
):
    """
    Place an order and add to order book.
    Market orders are immediately matched.
    """
    # 1️⃣ Create order document
    order = create_order_document(user_id, symbol, side, order_type, quantity, price, stop_price, fee_rate)

    # 2️⃣ Save to database
    result = await trading_orders_collection.insert_one(order)
    order["_id"] = str(result.inserted_id)

    # 3️⃣ Add order to in-memory order book
    await add_order_to_book(order)

    # 4️⃣ Try to match orders
    trades: List[dict] = await match_order(order)

    # 5️⃣ Save trades
    for trade in trades:
        await trading_trades_collection.insert_one(trade)

    return {
        "order": order,
        "trades": trades
    }


# from datetime import datetime
# from typing import Dict, List
# from decimal import Decimal, ROUND_DOWN
# from app.database import orders_collection, trades_collection, wallets_collection, ledger_collection
# from app.models.order_model import create_order_document
# from app.models.trade_model import create_trade_document
# from app.websocket.connection_manager import manager

# # ------------------------------
# # WebSocket Notification
# # ------------------------------
# async def notify_user(user_id: str, message: str):
#     await manager.send_personal_message(user_id, {
#         "type": "trade_notification",
#         "message": message
#     })

# # ------------------------------
# # Ledger Entry
# # ------------------------------
# async def record_ledger_entry(user_id: str, currency: str, amount: float, entry_type: str, reference_id: str) -> Dict:
#     entry = {
#         "user_id": user_id,
#         "currency": currency,
#         "amount": amount,
#         "type": entry_type,  # credit/debit
#         "reference_id": reference_id,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
#     await ledger_collection.insert_one(entry)
#     return entry

# # ------------------------------
# # Place Order
# # ------------------------------
# async def place_order(order_data: Dict) -> Dict:
#     """
#     Insert a new order and attempt to match it.
#     order_data: Dict with user_id, symbol, side, type, quantity, price, stop_price
#     """
#     # 1️⃣ Insert order
#     order = create_order_document(**order_data)
#     result = await orders_collection.insert_one(order)
#     order["_id"] = str(result.inserted_id)

#     # 2️⃣ Attempt to match orders
#     trades = await match_order(order)

#     return {
#         "order": order,
#         "trades": trades
#     }

# # ------------------------------
# # Order Matching Engine
# # ------------------------------
# async def match_order(new_order: Dict) -> List[Dict]:
#     """
#     Simple order matching engine.
#     Matches limit/market orders against opposite side orders.
#     """
#     trades = []

#     # Find opposite side orders for the same symbol that are not fully filled
#     side_to_match = "sell" if new_order["side"] == "buy" else "buy"

#     # For simplicity: only match limit/market orders
#     query = {
#         "symbol": new_order["symbol"],
#         "side": side_to_match,
#         "status": "open"
#     }

#     if new_order["type"] == "limit":
#         if new_order["side"] == "buy":
#             query["price"] = {"$lte": new_order["price"]}
#         else:
#             query["price"] = {"$gte": new_order["price"]}

#     orders_cursor = orders_collection.find(query).sort("created_at", 1)
#     opposite_orders = await orders_cursor.to_list(length=50)

#     remaining_qty = Decimal(str(new_order["quantity"]))

#     for opp_order in opposite_orders:
#         opp_qty = Decimal(str(opp_order["quantity"]))
#         if remaining_qty <= 0:
#             break

#         traded_qty = min(remaining_qty, opp_qty)
#         trade_price = Decimal(str(opp_order["price"])) if opp_order["type"] == "limit" else Decimal(str(new_order["price"]))
#         trade_price = trade_price.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

#         # Create trade document
#         trade_doc = create_trade_document(
#             symbol=new_order["symbol"],
#             buy_order_id=new_order["_id"] if new_order["side"] == "buy" else opp_order["_id"],
#             sell_order_id=new_order["_id"] if new_order["side"] == "sell" else opp_order["_id"],
#             quantity=float(traded_qty),
#             price=float(trade_price),
#             buyer_id=new_order["user_id"] if new_order["side"] == "buy" else opp_order["user_id"],
#             seller_id=new_order["user_id"] if new_order["side"] == "sell" else opp_order["user_id"],
#             fee=0.001  # 0.1% fee for now
#         )
#         result = await trades_collection.insert_one(trade_doc)
#         trade_doc["_id"] = str(result.inserted_id)
#         trades.append(trade_doc)

#         # Update wallets
#         await wallets_collection.update_one(
#             {"user_id": trade_doc["buyer_id"], "currency": new_order["symbol"].split("/")[0]},
#             {"$inc": {"balance": float(traded_qty)}, "$set": {"updated_at": datetime.utcnow()}}
#         )
#         await wallets_collection.update_one(
#             {"user_id": trade_doc["seller_id"], "currency": new_order["symbol"].split("/")[0]},
#             {"$inc": {"balance": -float(traded_qty)}, "$set": {"updated_at": datetime.utcnow()}}
#         )

#         # Record ledger
#         await record_ledger_entry(trade_doc["buyer_id"], new_order["symbol"].split("/")[0], float(traded_qty), "credit", trade_doc["_id"])
#         await record_ledger_entry(trade_doc["seller_id"], new_order["symbol"].split("/")[0], float(traded_qty), "debit", trade_doc["_id"])

#         # Notify users
#         await notify_user(trade_doc["buyer_id"], f"Bought {float(traded_qty)} {new_order['symbol']} at {float(trade_price)}")
#         await notify_user(trade_doc["seller_id"], f"Sold {float(traded_qty)} {new_order['symbol']} at {float(trade_price)}")

#         remaining_qty -= traded_qty

#         # Update opposite order quantity
#         new_opp_qty = float(opp_qty - traded_qty)
#         if new_opp_qty <= 0:
#             await orders_collection.update_one({"_id": opp_order["_id"]}, {"$set": {"status": "filled"}})
#         else:
#             await orders_collection.update_one({"_id": opp_order["_id"]}, {"$set": {"quantity": new_opp_qty}})

#     # Update new_order status
#     await orders_collection.update_one(
#         {"_id": new_order["_id"]},
#         {"$set": {"quantity": float(remaining_qty), "status": "filled" if remaining_qty <= 0 else "open"}}
#     )

#     return trades

# # ------------------------------
# # Get Order Book
# # ------------------------------
# async def get_order_book(symbol: str) -> Dict:
#     """
#     Return current bids and asks for a symbol
#     """
#     bids_cursor = orders_collection.find({"symbol": symbol, "side": "buy", "status": "open"}).sort("price", -1)
#     asks_cursor = orders_collection.find({"symbol": symbol, "side": "sell", "status": "open"}).sort("price", 1)

#     bids = await bids_cursor.to_list(length=50)
#     asks = await asks_cursor.to_list(length=50)

#     return {
#         "symbol": symbol,
#         "bids": bids,
#         "asks": asks
#     }