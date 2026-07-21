from network.protocol import parse_incoming, make_error_message
from network.broadcaster import broadcast_snapshot
from tournament.tournament_manager import UnknownRoomError
from tournament.room import UnknownPlayerError


async def handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket):
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

    except (UnknownRoomError, UnknownPlayerError, KeyError) as e:
        await websocket.send(make_error_message(str(e)))
