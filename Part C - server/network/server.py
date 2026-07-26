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
from network.protocol import MatchNotFoundMessage, OpponentDisconnectedMessage, OpponentReconnectedMessage, LoginOkMessage, LoginErrorMessage
from data.player_store import PlayerStore, InvalidCredentialsError, UsernameTakenError
from constants import MessageType, Color, SERVER_HOST, SERVER_PORT

TIMEOUT_CHECK_INTERVAL_SEC = 1

tournament_manager = TournamentManager()
connection_manager = ConnectionManager()
player_store = PlayerStore()
matchmaker = Matchmaker()
disconnect_timer = DisconnectTimer()
_disconnected_seats = {}


async def _handle_login(websocket):
    try:
        raw = await websocket.recv()
        data = json.loads(raw)
    except (websockets.exceptions.ConnectionClosed, json.JSONDecodeError):
        return None

    if data.get("type") != MessageType.LOGIN:
        await websocket.send(LoginErrorMessage(reason="expected LOGIN as first message").to_json())
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
        await websocket.send(LoginErrorMessage(reason=str(exc)).to_json())
        await websocket.close()
        return None

    rating = player_store.get_rating(username)
    await websocket.send(LoginOkMessage(username=username, rating=rating).to_json())
    return username


def _find_pending_reconnect(username, disconnected_seats):
    for (room_id, color), pending_username in disconnected_seats.items():
        if pending_username == username:
            return room_id, color
    return None

async def _notify_opponent(room_id, color, message, tournament_manager, connection_manager):
    player_ids = tournament_manager.get_player_ids(room_id)
    opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
    opponent_id = player_ids.get(opponent_color)
    if opponent_id is None:
        return
    ws = connection_manager.get_websocket(opponent_id)
    if ws is not None:
        await ws.send(message)


async def handler(websocket):
    try:
        username = await _handle_login(websocket)
        if username is None:
            return

        player_id = str(uuid.uuid4())
        connection_manager.register(player_id, websocket)
        connection_manager.set_username(player_id, username)

        reconnect_seat = _find_pending_reconnect(username, _disconnected_seats)
        if reconnect_seat is not None:
            room_id, color = reconnect_seat
            disconnect_timer.cancel(room_id, color)
            del _disconnected_seats[(room_id, color)]
            tournament_manager.reseat(room_id, color, player_id)
            connection_manager.join_room(room_id, player_id)
            await _notify_opponent(room_id, color, OpponentReconnectedMessage().to_json(), tournament_manager, connection_manager)

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
                    await _notify_opponent(room_id, color, OpponentDisconnectedMessage(seconds_remaining=20).to_json(), tournament_manager, connection_manager)

            matchmaker.cancel(player_id)
            connection_manager.unregister(player_id)
    except Exception:
        import traceback
        traceback.print_exc()
        raise


async def _matchmaking_timeout_loop():
    while True:
        await asyncio.sleep(TIMEOUT_CHECK_INTERVAL_SEC)
        timed_out = matchmaker.check_timeouts()
        for player_id in timed_out:
            ws = connection_manager.get_websocket(player_id)
            if ws is not None:
                await ws.send(MatchNotFoundMessage().to_json())


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
    async with websockets.serve(handler, SERVER_HOST, SERVER_PORT):
        print(f"Server listening on ws://{SERVER_HOST}:{SERVER_PORT}")
        asyncio.create_task(_matchmaking_timeout_loop())
        asyncio.create_task(_disconnect_timeout_loop())
        asyncio.create_task(_game_tick_loop())
        await asyncio.Future()

async def _game_tick_loop():
    interval_sec = 0.05
    while True:
        await asyncio.sleep(interval_sec)
        tournament_manager.tick_all(interval_sec * 1000)
        for room_id in tournament_manager.all_room_ids():
            snapshot = tournament_manager.get_snapshot(room_id)
            await broadcast_snapshot(room_id, snapshot, connection_manager)


if __name__ == "__main__":
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())