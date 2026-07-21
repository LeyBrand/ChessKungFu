import sys
import os

_CURRENT_DIR - os.path.dirname(os.path.abspath(__file__))
_PART_A_DIR = os.path.join(_CURRENT_DIR, "..", "..", "Part A - business logic")

if _PART_A_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_A_DIR))

from api.game_api import GameSession
from events.event_bus import EventBus

import uuid
from tournamet.room import Room

class TournametManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, board_text, player_ids):
        room_id = str(uuid.uuid4())
        event_bus = EventBus()
        session = GameSession(board_text, event_bus=event_bus)
        self._rooms[room_id] = Room(room_id, session, event_bus, player_ids)
        return room_id

    def handle_move(self, room_id, player_id, x, y):
        room = self._rooms.get(room_id)
        if room is None:
            raise ValueError(f"Unknowen room: {room_id}")
        room.handle_click(player_id, x, y)

    def get_snapshot(self, room_id):
        return self._rooms[room_id].get_snapshot()
    
    def create_waiting_room(self, board_text):
        return self.create_room(board_text, player_ids={})
    
    def seat_player(self, room_id, color, player_id):
        self._get_room(room_id).seat(color, player_id)

    def is_room_full(self, room_id):
        return self._get_room(room_id).is_full()
    