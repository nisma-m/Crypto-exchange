from fastapi import APIRouter, WebSocket
import asyncio
from app.services.market_bot_service import generate_orders

router = APIRouter()

@router.websocket("/ws/bot")
async def bot_ws(websocket: WebSocket):
    await websocket.accept()
    print("✅ BOT WS CONNECTED")

    while True:
        data = await generate_orders()
        await websocket.send_json(data)
        await asyncio.sleep(5)