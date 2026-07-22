from network.protocol import (
    parse_incoming, make_error_message,
    make_match_found_message, make_match_not_found_message,
)
from network.broadcaster import broadcast_snapshot
from tournament.tournament_manager import UnknownRoomError
from tournament.room import UnknownPlayerError
from constants import Color  # safe here: importing tournament_manager above already added repo root to sys.path

STARTING_BOARD_TEXT = """
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
"""


async def handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket,
                          matchmaker=None, player_store=None):
    try:
        data = parse_incoming(raw_message)
    except ValueError as e:
        await websocket.send(make_error_message(str(e)))
        return

    try:
        if data["type"] == "JOIN_ROOM":
            connection_manager.join_room(data["room_id"], player_id)

        elif data["type"] == "MOVE":
            tournament_manager.handle_move(data["room_id"], player_id, data["x"], data["y"])
            snapshot = tournament_manager.get_snapshot(data["room_id"])
            await broadcast_snapshot(data["room_id"], snapshot, connection_manager)

        elif data["type"] == "JUMP":
            tournament_manager.handle_jump(data["room_id"], player_id, data["x"], data["y"])
            snapshot = tournament_manager.get_snapshot(data["room_id"])
            await broadcast_snapshot(data["room_id"], snapshot, connection_manager)

        elif data["type"] == "PLAY":
            await _handle_play(player_id, tournament_manager, connection_manager, matchmaker, player_store)

        elif data["type"] == "CANCEL_SEEK":
            if matchmaker is not None:
                matchmaker.cancel(player_id)

    except (UnknownRoomError, UnknownPlayerError, KeyError) as e:
        await websocket.send(make_error_message(str(e)))


async def _handle_play(player_id, tournament_manager, connection_manager, matchmaker, player_store):
    if matchmaker is None or player_store is None:
        return  # not wired up (e.g. an old test calling handle_message directly) - no-op

    username = connection_manager.get_username(player_id)
    rating = player_store.get_rating(username)

    opponent_id = matchmaker.seek(player_id, username, rating)
    if opponent_id is None:
        return  # now waiting in the pool - MATCH_NOT_FOUND arrives later on timeout

    room_id = tournament_manager.create_room(STARTING_BOARD_TEXT, player_ids={})
    tournament_manager.seat_player(room_id, Color.WHITE, opponent_id)
    tournament_manager.seat_player(room_id, Color.BLACK, player_id)
    connection_manager.join_room(room_id, opponent_id)
    connection_manager.join_room(room_id, player_id)

    opponent_ws = connection_manager.get_websocket(opponent_id)
    this_ws = connection_manager.get_websocket(player_id)

    if opponent_ws is not None:
        await opponent_ws.send(make_match_found_message(room_id, Color.WHITE))
    if this_ws is not None:
        await this_ws.send(make_match_found_message(room_id, Color.BLACK))