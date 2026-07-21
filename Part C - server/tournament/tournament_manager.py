"""
Floor 2 of the architecture: the "tournament manager".

Deliberately does NOT import asyncio / websockets / anything network
related - it only knows about GameSession (Floor 1) and Room. This is
what makes the offline test possible: you can create a room and play
moves through this file with zero network stack running.

sys.path wiring to Part A mirrors business_bridge.py in Part B (same
technique, flagged in conversation as a spot to revisit/DRY-up later).
"""

import sys
import os
import uuid

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_A_DIR = os.path.join(_CURRENT_DIR, "..", "..", "Part A - business_logic")
if _PART_A_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_A_DIR))

from api.game_api import GameSession   # noqa: E402
from events.event_bus import EventBus  # noqa: E402

from tournament.room import Room  # noqa: E402


class UnknownRoomError(ValueError):
    pass


class TournamentManager:
    def __init__(self):
        self._rooms = {}  # room_id -> Room

    def create_room(self, board_text, player_ids):
        room_id = str(uuid.uuid4())
        event_bus = EventBus()
        session = GameSession.new_game(board_text, event_bus=event_bus)
        self._rooms[room_id] = Room(room_id, session, event_bus, player_ids)
        return room_id

    def room_exists(self, room_id):
        return room_id in self._rooms

    def _get_room(self, room_id):
        room = self._rooms.get(room_id)
        if room is None:
            raise UnknownRoomError(f"Unknown room: {room_id}")
        return room

    def handle_move(self, room_id, player_id, x, y):
        self._get_room(room_id).handle_click(player_id, x, y)

    def handle_jump(self, room_id, player_id, x, y):
        self._get_room(room_id).handle_jump(player_id, x, y)

    def tick(self, room_id, elapsed_ms):
        self._get_room(room_id).tick(elapsed_ms)

    def get_snapshot(self, room_id):
        return self._get_room(room_id).get_snapshot()

    def is_game_over(self, room_id):
        return self._get_room(room_id).is_game_over()
