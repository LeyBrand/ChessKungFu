import asyncio
import json
import uuid

import websockets

from tournament.tournament_manager import TournamentManager
from tournament.matchmaker import Matchmaker
from tournament.disconnect_timer import DisconnectTimer
from network.connection_manager import ConnectionManager
from network.message_router import handle_message
from network.broadcaster import broadcast_snapshot
from network.protocol import (
    make_match_not_found_message,
    make_opponent_disconnected_message,
    make_opponent_reconnected_message,
)
from data.player_store import PlayerStore, InvalidCredentialsError, UsernameTakenError

TIMEOUT_CHECK_INTERVAL_SEC = 1

tournament_manager = TournamentManager()
connection_manager = ConnectionManager()
player_store = PlayerStore()
matchmaker = Matchmaker()
disconnect_timer = DisconnectTimer()
_disconnected_seats = {}  # (room_id, color) -> username, only while a timer is pending


async def _handle_login(websocket):
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


def _find_pending_reconnect(username):
    for (room_id, color), pending_username in _disconnected_seats.items():
        if pending_username == username:
            return room_id, color
    return None


async def _notify_opponent(room_id, color, message):
    player_ids = tournament_manager.get_player_ids(room_id)
    opponent_color = "black" if color == "white" else "white"
    opponent_id = player_ids.get(opponent_color)
    if opponent_id is None:
        return
    ws = connection_manager.get_websocket(opponent_id)
    if ws is not None:
        await ws.send(message)


async def handler(websocket):
    username = await _handle_login(websocket)
    if username is None:
        return

    player_id = str(uuid.uuid4())
    connection_manager.register(player_id, websocket)
    connection_manager.set_username(player_id, username)

    reconnect_seat = _find_pending_reconnect(username)
    if reconnect_seat is not None:
        room_id, color = reconnect_seat
        disconnect_timer.cancel(room_id, color)
        del _disconnected_seats[(room_id, color)]
        tournament_manager.reseat(room_id, color, player_id)
        connection_manager.join_room(room_id, player_id)
        await _notify_opponent(room_id, color, make_opponent_reconnected_message())

    try:
        async for raw_message in websocket:
            await handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket,
                                  matchmaker, player_store)
    finally:
        seat = tournament_manager.find_seat(player_id)
        if seat is not None:
            room_id, color = seat
            if not tournament_manager.get_snapshot(room_id)["is_game_over"]:
                disconnect_timer.start(room_id, color)
                _disconnected_seats[(room_id, color)] = username
                await _notify_opponent(room_id, color, make_opponent_disconnected_message(20))

        matchmaker.cancel(player_id)
        connection_manager.unregister(player_id)


async def _matchmaking_timeout_loop():
    while True:
        await asyncio.sleep(TIMEOUT_CHECK_INTERVAL_SEC)
        timed_out = matchmaker.check_timeouts()
        for player_id in timed_out:
            ws = connection_manager.get_websocket(player_id)
            if ws is not None:
                await ws.send(make_match_not_found_message())


async def _disconnect_timeout_loop():
    while True:
        await asyncio.sleep(TIMEOUT_CHECK_INTERVAL_SEC)
        expired = disconnect_timer.check_expired()
        for room_id, color in expired:
            _disconnected_seats.pop((room_id, color), None)
            tournament_manager.resign(room_id, color)
            snapshot = tournament_manager.get_snapshot(room_id)
            await broadcast_snapshot(room_id, snapshot, connection_manager)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server listening on ws://localhost:8765")
        asyncio.create_task(_matchmaking_timeout_loop())
        asyncio.create_task(_disconnect_timeout_loop())
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())