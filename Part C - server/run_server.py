"""
Thin runner: wires GameServer to a real BusinessBridge (imported from
Part B - GUI) and a real websockets listener. Kept separate from
game_server.py on purpose, so game_server.py has zero dependency on
the `websockets` package and can be unit tested without a real
network socket.
"""
import asyncio
import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_B_DIR = os.path.join(_CURRENT_DIR, "..", "Part B - GUI")
if _PART_B_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_B_DIR))

import websockets

from bridge.business_bridge import BusinessBridge  # noqa: E402  (import after sys.path setup)
from game_server import GameServer  # noqa: E402

HOST = "localhost"
PORT = 8765
TICK_INTERVAL_SEC = 0.05  # ~20 fps

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


async def main():
    bridge = BusinessBridge(STARTING_BOARD_TEXT)
    server = GameServer(bridge=bridge)

    async with websockets.serve(server.handle_client, HOST, PORT):
        print(f"Server listening on ws://{HOST}:{PORT}")
        await server.tick_loop(TICK_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(main())