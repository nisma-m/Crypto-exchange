from fastapi import FastAPI, WebSocket

# Core API routes
from app.api import (
    auth_routes,
    wallet_routes,
    transaction_routes,
    security_routes,
    admin_routes,
    admin_auth_routes,
    ws_routes,
    market_bot_routes,
)

# WebSockets
from app.websocket.routes import router as websocket_router
from app.websocket import market_bot_ws

# Trading module
from app.trading.routes.trading_routes import router as trading_routes
from app.trading.websocket.trading_ws_routes import router as trading_ws_router

# ------------------------------
# CREATE APP
# ------------------------------
app = FastAPI(title="Crypto Exchange Backend")


# ------------------------------
# API ROUTES
# ------------------------------
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(wallet_routes.router, prefix="/wallet")
app.include_router(transaction_routes.router, prefix="/transactions")
app.include_router(security_routes.router, prefix="/security")
app.include_router(trading_routes, prefix="/trading")
app.include_router(admin_routes.router)
app.include_router(admin_auth_routes.router)

# Market Bot Routes
app.include_router(market_bot_routes.router)


# ------------------------------
# WEBSOCKET ROUTES
# ------------------------------
app.include_router(websocket_router)
app.include_router(trading_ws_router)
app.include_router(market_bot_ws.router)


# ------------------------------
# WebSocket endpoint
# ------------------------------
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await ws_routes.websocket_endpoint(websocket, user_id)


# ------------------------------
# ROOT
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Crypto Exchange Backend Running"}