from fastapi import APIRouter
from app.services.market_bot_service import (
    generate_orders,
    update_config,
    get_bot_analytics,
    get_bot_logs,
    run_bot_loop,
    stop_bot
)

import asyncio

router = APIRouter(
    prefix="/bot",
    tags=["Market Bot"]
)

# Manual run
@router.post("/run")
async def run_once():
    return await generate_orders()

# Start auto bot
@router.post("/start")
async def start_bot():
    asyncio.create_task(run_bot_loop())
    return {"message": "Bot started"}

# Stop bot
@router.post("/stop")
async def stop():
    return await stop_bot()

# Config
@router.post("/config")
async def config(spread: float, volume: float):
    return await update_config(spread, volume)

# Analytics
@router.get("/analytics")
async def analytics():
    return await get_bot_analytics()

# Logs
@router.get("/logs")
async def logs():
    return await get_bot_logs()