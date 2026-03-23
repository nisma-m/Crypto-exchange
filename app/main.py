# crypto_exchange/app/main.py

from fastapi import FastAPI, WebSocket

# Core API routes
from app.api import auth_routes, wallet_routes, transaction_routes, security_routes, admin_routes
from app.websocket.routes import router as websocket_router
from app.api import ws_routes

# Trading module
from app.trading.routes.trading_routes import router as trading_routes
from app.trading.websocket.trading_ws_routes import router as trading_ws_router

# Market Bot (YOUR MODULE)
from app.api import market_bot_routes
from app.websocket import market_bot_ws


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

# ✅ Market Bot Routes
app.include_router(market_bot_routes.router)


# ------------------------------
# WEBSOCKET ROUTES
# ------------------------------
app.include_router(websocket_router)       # General WebSocket
app.include_router(trading_ws_router)      # Trading WebSocket

# ✅ Market Bot WebSocket
app.include_router(market_bot_ws.router)


# ------------------------------
# OLD WS (DO NOT REMOVE)
# ------------------------------
@app.websocket("/ws/{user_id}")
async def websocket(user_id: str, websocket: WebSocket):
    await ws_routes.websocket_endpoint(websocket, user_id)


# ------------------------------
# ROOT
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Crypto Exchange Backend Running"}