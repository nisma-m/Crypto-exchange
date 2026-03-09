from fastapi import FastAPI, WebSocket
from app.api import auth_routes, wallet_routes, transaction_routes, security_routes, admin_routes, admin_ws, ws_routes, admin_auth_routes
from app.trading.routes.trading_routes import router as trading_routes
from app.trading.websocket.trading_ws_routes import router as trading_ws_router

app = FastAPI(title="Crypto Exchange Backend")

# ------------------------------
# API Routes
# ------------------------------
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(wallet_routes.router, prefix="/wallet")
app.include_router(transaction_routes.router, prefix="/transactions")
app.include_router(security_routes.router, prefix="/security")
app.include_router(trading_routes, prefix="/trading")
app.include_router(admin_routes.router)
app.include_router(admin_auth_routes.router)

# ------------------------------
# WebSocket Routes
# ------------------------------
app.include_router(trading_ws_router)
app.include_router(admin_ws.router)

@app.websocket("/ws/{user_id}")
async def websocket(user_id: str, websocket: WebSocket):
    await ws_routes.websocket_endpoint(websocket, user_id)

@app.get("/")
async def root():
    return {"message": "Crypto Exchange Backend Running"}