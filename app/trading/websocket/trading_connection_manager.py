# crypto_exchange\app\trading\websocket\trading_connection_manager.py
from typing import Dict, List
from fastapi import WebSocket

class TradingConnectionManager:
    """
    Manage WebSocket connections for trading module.
    Supports multiple users connected at once.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: dict):
        """
        Send a message to a specific user.
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected users.
        """
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_json(message)

    # -----------------------------
    # Broadcast Order Book Updates
    # -----------------------------
    async def broadcast_order_book(self, symbol: str, order_book: dict):
        """
        Broadcast the updated order book for a symbol to all connected users.
        """
        message = {
            "type": "order_book_update",
            "symbol": symbol,
            "order_book": order_book
        }
        await self.broadcast(message)

# Example normalization function
def normalize_symbol(symbol: str) -> str:
    return symbol.upper().replace("/", "-")

# Single instance
manager = TradingConnectionManager()