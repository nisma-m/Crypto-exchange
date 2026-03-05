# app/api/ws_routes.py
from fastapi import WebSocket

active_connections = {}  # user_id -> WebSocket

async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # You can handle messages from client if needed
    except Exception:
        pass
    finally:
        del active_connections[user_id]
        await websocket.close()