import asyncio
import json
import uuid

import websockets

from tournament.tournament_manager import TournamentManager
from network.connection_manager import ConnectionManager
from network.message_router import handle_message
from data.player_store import PlayerStore, InvalidCredentialsError, UsernameTakenError

tournament_manager = TournamentManager()
connection_manager = ConnectionManager()
player_store = PlayerStore()


async def _handle_login(websocket):
    """Waits for the client's first message, expects {"type": "LOGIN", ...}.
    Returns the logged-in username, or None if login failed (caller should
    already have closed the socket by the time this returns None)."""
    try:
        raw = await websocket.recv()
        data = json.loads(raw)
    except (websockets.exceptions.ConnectionClosed, json.JSONDecodeError):
        return None

    if data.get("type") != "LOGIN":
        await websocket.send(json.dumps({"type": "LOGIN_ERROR", "reason": "expected LOGIN as first message"}))
        await websocket.close()
        return None

    username = data.get("username")
    password = data.get("password")

    try:
        if player_store.player_exists(username):
            player_store.verify_password(username, password)
        else:
            player_store.create_player(username, password)
    except (InvalidCredentialsError, UsernameTakenError) as exc:
        await websocket.send(json.dumps({"type": "LOGIN_ERROR", "reason": str(exc)}))
        await websocket.close()
        return None

    rating = player_store.get_rating(username)
    await websocket.send(json.dumps({"type": "LOGIN_OK", "username": username, "rating": rating}))
    return username


async def handler(websocket):
    username = await _handle_login(websocket)
    if username is None:
        return

    player_id = str(uuid.uuid4())
    connection_manager.register(player_id, websocket)
    connection_manager.set_username(player_id, username)
    try:
        async for raw_message in websocket:
            await handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket)
    finally:
        connection_manager.unregister(player_id)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server listening on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())