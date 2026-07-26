from network.protocol import parse_incoming, ErrorMessage, MatchFoundMessage, MatchNotFoundMessage
from network.broadcaster import broadcast_snapshot
from tournament.tournament_manager import UnknownRoomError
from tournament.room import UnknownPlayerError
from constants import Color, MessageType
from network.rating_updater import subscribe_rating_update

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


async def _handle_join_room(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store):
    connection_manager.join_room(data["room_id"], player_id)


async def _handle_move(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store):
    tournament_manager.handle_move(data["room_id"], player_id, data["x"], data["y"])
    snapshot = tournament_manager.get_snapshot(data["room_id"])
    await broadcast_snapshot(data["room_id"], snapshot, connection_manager)


async def _handle_jump(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store):
    tournament_manager.handle_jump(data["room_id"], player_id, data["x"], data["y"])
    snapshot = tournament_manager.get_snapshot(data["room_id"])
    await broadcast_snapshot(data["room_id"], snapshot, connection_manager)


async def _handle_cancel_seek(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store):
    if matchmaker is not None:
        matchmaker.cancel(player_id)


async def _handle_play(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store):
    if matchmaker is None or player_store is None:
        return  # not wired up (e.g. an old test calling handle_message directly) - no-op

    username = connection_manager.get_username(player_id)
    rating = player_store.get_rating(username)

    opponent_id = matchmaker.seek(player_id, username, rating)
    if opponent_id is None:
        return  # now waiting in the pool - MATCH_NOT_FOUND arrives later on timeout

    room_id = tournament_manager.create_room(STARTING_BOARD_TEXT, player_ids={})
    subscribe_rating_update(
        tournament_manager.get_event_bus(room_id),
        lambda: tournament_manager.get_player_ids(room_id),
        connection_manager,
        player_store,
    )
    tournament_manager.seat_player(room_id, Color.WHITE, opponent_id)
    tournament_manager.seat_player(room_id, Color.BLACK, player_id)
    connection_manager.join_room(room_id, opponent_id)
    connection_manager.join_room(room_id, player_id)
    snapshot = tournament_manager.get_snapshot(room_id)
    await broadcast_snapshot(room_id, snapshot, connection_manager)

    opponent_ws = connection_manager.get_websocket(opponent_id)
    this_ws = connection_manager.get_websocket(player_id)

    if opponent_ws is not None:
        await opponent_ws.send(MatchFoundMessage(room_id, Color.WHITE).to_json())
    if this_ws is not None:
        await this_ws.send(MatchFoundMessage(room_id, Color.BLACK).to_json())


_HANDLERS = {
    MessageType.JOIN_ROOM: _handle_join_room,
    MessageType.MOVE: _handle_move,
    MessageType.JUMP: _handle_jump,
    MessageType.PLAY: _handle_play,
    MessageType.CANCEL_SEEK: _handle_cancel_seek,
}


async def handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket,
                          matchmaker=None, player_store=None):
    try:
        data = parse_incoming(raw_message)
    except ValueError as e:
        await websocket.send(ErrorMessage(reason=str(e)).to_json())
        return

    handler = _HANDLERS.get(data["type"])
    if handler is None:
        return  # already validated by parse_incoming, shouldn't happen

    try:
        await handler(data, player_id, tournament_manager, connection_manager, websocket, matchmaker, player_store)
    except (UnknownRoomError, UnknownPlayerError, KeyError) as e:
        await websocket.send(ErrorMessage(reason=str(e)).to_json())