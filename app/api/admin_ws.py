from app.database import db
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import List

router = APIRouter()

# Active connections list
connections: List[WebSocket] = []

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

@router.websocket("/ws/admin-stats")
async def admin_stats_ws(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print("Stats WebSocket connected, total:", len(connections))

    try:
        while True:
            stats = {
                "total_users": await db.users.count_documents({}),
                "total_wallets": await db.wallets.count_documents({}),
                "total_transactions": await db.transactions.count_documents({}),
                "total_trades": await db.trades.count_documents({}),
                "pending_deposits": await db.transactions.count_documents({"type": "deposit", "status": "pending"}),
                "pending_withdrawals": await db.transactions.count_documents({"type": "withdrawal", "status": "pending"})
            }
            await websocket.send_json(stats)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)
        print("Stats WebSocket disconnected, total:", len(connections))