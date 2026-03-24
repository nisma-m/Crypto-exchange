import asyncio
from app.services.market_bot_service import generate_orders

async def run_bot():
    while True:
        await generate_orders()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bot())