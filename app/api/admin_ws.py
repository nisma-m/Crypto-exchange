from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

# Active connections list
connections: list[WebSocket] = []

@router.websocket("/ws/admin-alerts")
async def admin_alerts(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    connections.append(websocket)
    print("WebSocket connected, total:", len(connections))

    try:
        while True:
            # Keep the connection alive
            await asyncio.sleep(1000)
    except WebSocketDisconnect:
        # Remove connection on disconnect
        if websocket in connections:
            connections.remove(websocket)
        print("WebSocket disconnected, total:", len(connections))


async def broadcast_alert(message: dict):
    # Debug print active connections count
    print("ACTIVE CONNECTIONS:", len(connections))

    # Send message to all active connections
    for conn in connections:
        try:
            await conn.send_text(json.dumps(message))
        except Exception as e:
            print("Error sending to connection:", e)