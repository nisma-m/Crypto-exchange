from app.websocket.connection_manager import manager


async def notify_deposit(user_id: str, currency: str, amount: float):

    await manager.send_personal_message(
        user_id,
        {
            "type": "deposit",
            "currency": currency,
            "amount": amount,
            "message": f"{amount} {currency} deposited"
        }
    )


async def notify_withdrawal(user_id: str, currency: str, amount: float):

    await manager.send_personal_message(
        user_id,
        {
            "type": "withdrawal",
            "currency": currency,
            "amount": amount,
            "message": f"{amount} {currency} withdrawn"
        }
    )


async def notify_trade(user_id: str, pair: str, side: str, amount: float):

    await manager.send_personal_message(
        user_id,
        {
            "type": "trade",
            "pair": pair,
            "side": side,
            "amount": amount,
            "message": f"Trade executed: {side} {amount} {pair}"
        }
    )


async def notify_security(user_id: str, message: str):

    await manager.send_personal_message(
        user_id,
        {
            "type": "security",
            "message": message
        }
    )