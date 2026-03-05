from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):

    await manager.connect(user_id, websocket)

    try:

        while True:

            data = await websocket.receive_text()

            await manager.send_personal_message(
                user_id,
                {
                    "type": "ping",
                    "message": data
                }
            )

    except WebSocketDisconnect:

        manager.disconnect(user_id, websocket)
