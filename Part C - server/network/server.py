import asyncio
import uuid

import websockets

from tournament.tournament_manager import TournamentManager
from network.connection_manager import ConnectionManager
from network.message_router import handle_message

tournament_manager = TournamentManager()
connection_manager = ConnectionManager()


async def handler(websocket):
    player_id = str(uuid.uuid4())
    connection_manager.register(player_id, websocket)
    try:
        async for raw_message in websocket:
            await handle_message(raw_message, player_id, tournament_manager, connection_manager, websocket)
    finally:
        connection_manager.unregister(player_id)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
