
connections = {}


async def register_connection(user_id, websocket):

    connections[user_id] = websocket


async def send_notification(user_id, message):

    ws = connections.get(user_id)

    if ws:
        await ws.send_json(message)