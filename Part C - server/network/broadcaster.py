from network.protocol import SnapshotMessage


async def broadcast_snapshot(room_id, snapshot, connection_manager):
    message = SnapshotMessage(data=snapshot).to_json()
    sent_to = []
    for player_id in connection_manager.players_in_room(room_id):
        ws = connection_manager.get_websocket(player_id)
        if ws is not None:
            await ws.send(message)
            sent_to.append(player_id)
    return sent_to
