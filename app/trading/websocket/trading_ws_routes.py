# crypto_exchange\app\trading\websocket\trading_ws_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.trading.websocket.trading_connection_manager import manager
from asyncio import sleep

router = APIRouter()

@router.websocket("/ws/trading/{user_id}")
async def trading_websocket(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for trading updates:
    - Order book updates
    - Trade notifications
    - Price updates
    """
    await manager.connect(user_id, websocket)


    try:
        while True:
            # Example: broadcast order book snapshot every second
            order_book_data = get_order_book_snapshot()  # your function
            await manager.send_personal_message(user_id, {
                "type": "order_book",
                "data": order_book_data
            })
            await sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    # try:
    #     while True:
    #         # Receive ping or messages from frontend
    #         data = await websocket.receive_text()
    #         # Echo ping back
    #         await websocket.send_json({
    #             "type": "ping",
    #             "message": data
    #         })
    # except WebSocketDisconnect:
    #     manager.disconnect(user_id, websocket)