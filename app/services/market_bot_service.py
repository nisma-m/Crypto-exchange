import random
import asyncio
from datetime import datetime
from app.database import trading_orders_collection

BOT_CONFIG = {
    "spread": 2,
    "volume": 1,
    "running": False
}

# ------------------------------
# Generate Orders
# ------------------------------
async def generate_orders(symbol="BTCUSDT"):

    base_price = random.uniform(95, 105)

    buy_price = round(base_price - BOT_CONFIG["spread"], 2)
    sell_price = round(base_price + BOT_CONFIG["spread"], 2)

    buy_order = {
        "order_id": f"BOT_BUY_{random.randint(1000,9999)}",
        "symbol": symbol,
        "price": buy_price,
        "side": "buy",
        "quantity": BOT_CONFIG["volume"],
        "created_at": str(datetime.utcnow())
    }

    sell_order = {
        "order_id": f"BOT_SELL_{random.randint(1000,9999)}",
        "symbol": symbol,
        "price": sell_price,
        "side": "sell",
        "quantity": BOT_CONFIG["volume"],
        "created_at": str(datetime.utcnow())
    }

    buy_res = await trading_orders_collection.insert_one(buy_order)
    sell_res = await trading_orders_collection.insert_one(sell_order)

    buy_order["_id"] = str(buy_res.inserted_id)
    sell_order["_id"] = str(sell_res.inserted_id)

    profit = sell_price - buy_price

    # Save profit
    await trading_orders_collection.insert_one({
        "type": "bot_profit",
        "profit": profit,
        "created_at": str(datetime.utcnow())
    })

    # Save log
    await trading_orders_collection.insert_one({
        "type": "bot_log",
        "message": f"Generated buy {buy_price} & sell {sell_price}",
        "created_at": str(datetime.utcnow())
    })

    return {
        "buy": buy_order,
        "sell": sell_order,
        "profit": profit
    }

# ------------------------------
# Update Config
# ------------------------------
async def update_config(spread: float, volume: float):
    BOT_CONFIG["spread"] = spread
    BOT_CONFIG["volume"] = volume
    return {"config": BOT_CONFIG}

# ------------------------------
# Analytics
# ------------------------------
async def get_bot_analytics():
    total_profit = 0
    total_trades = 0

    async for item in trading_orders_collection.find({"type": "bot_profit"}):
        total_profit += item.get("profit", 0)
        total_trades += 1

    return {
        "total_profit": total_profit,
        "total_trades": total_trades
    }

# ------------------------------
# Logs
# ------------------------------
async def get_bot_logs():
    logs = []
    async for log in trading_orders_collection.find({"type": "bot_log"}):
        log["_id"] = str(log["_id"])
        logs.append(log)
    return logs

# ------------------------------
# AUTO BOT LOOP
# ------------------------------
async def run_bot_loop():
    BOT_CONFIG["running"] = True

    while BOT_CONFIG["running"]:
        await generate_orders()
        await asyncio.sleep(5)  # every 5 sec

async def stop_bot():
    BOT_CONFIG["running"] = False
    return {"message": "Bot stopped"}