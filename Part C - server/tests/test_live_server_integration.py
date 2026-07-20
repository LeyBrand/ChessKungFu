"""
Real end-to-end sanity check: opens an actual TCP/WebSocket server
(no fakes anywhere), connects a real client to it, plays a king
capture, and confirms the client sees GAME_OVER over the wire.

This is slower and heavier than test_game_server.py on purpose - it's
meant to be run by hand when you want to be sure the whole stack
(Part A + Part B's BusinessBridge + Part C's GameServer + a real
socket) actually works together, not just the unit-tested pieces.
"""
import asyncio
import json
import os
import sys

import pytest
import websockets

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_C_DIR = os.path.join(_CURRENT_DIR, "..")
_PART_B_DIR = os.path.join(_CURRENT_DIR, "..", "..", "Part B - GUI")
for path in (_PART_C_DIR, _PART_B_DIR):
    if path not in sys.path:
        sys.path.insert(0, os.path.abspath(path))

from bridge.business_bridge import BusinessBridge  # noqa: E402
from game_server import GameServer  # noqa: E402
from data.player_store import PlayerStore  # noqa: E402

TEST_HOST = "localhost"
TEST_PORT = 8767  # different from the real app's 8765, to avoid clashing with a running server

# black king at (0,5), white rook at (0,6) - one move forward captures the king.
GAME_OVER_BOARD_TEXT = """
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
bK .  .  .  .  .  .  .
wR .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
"""


@pytest.mark.asyncio
async def test_real_client_sees_game_over_after_king_capture_over_the_wire():
    bridge = BusinessBridge(GAME_OVER_BOARD_TEXT)
    server = GameServer(
        bridge=bridge,
        player_store=PlayerStore(db_path=":memory:"),
        prompt_username=lambda ws: "test-player",
        prompt_password=lambda ws, text: "test-password",
    )

    tick_task = None
    async with websockets.serve(server.handle_client, TEST_HOST, TEST_PORT):
        tick_task = asyncio.create_task(server.tick_loop(interval_sec=0.05))
        try:
            async with websockets.connect(f"ws://{TEST_HOST}:{TEST_PORT}") as ws:
                initial = json.loads(await ws.recv())
                assert initial["type"] == "state"
                assert initial["snapshot"]["is_game_over"] is False

                await ws.send(json.dumps({"type": "click", "x": 0, "y": 600}))  # select rook
                await ws.send(json.dumps({"type": "click", "x": 0, "y": 500}))  # move onto king

                game_over_seen = False
                for _ in range(50):  # up to ~5s of polling, well past MOVE_MS(1000ms)
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=1.0))
                    if msg["snapshot"]["is_game_over"]:
                        game_over_seen = True
                        break

                assert game_over_seen, "client never received a state with is_game_over=True"
        finally:
            tick_task.cancel()