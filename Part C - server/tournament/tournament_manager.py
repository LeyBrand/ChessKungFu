import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_A_DIR = os.path.join(_CURRENT_DIR, "..", "..", "Part A - business_logic")

if _PART_A_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_A_DIR))

_ROOT_DIR = os.path.join(_CURRENT_DIR, "..", "..")
if os.path.abspath(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, os.path.abspath(_ROOT_DIR))

from api.game_api import GameSession
from events.event_bus import EventBus

import uuid
from tournament.room import Room

class UnknownRoomError(ValueError):
    pass


class TournamentManager:
    def __init__(self):
        self._rooms = {}

    def create_room(self, board_text, player_ids):
        room_id = str(uuid.uuid4())
        event_bus = EventBus()
        session = GameSession.new_game(board_text, event_bus=event_bus)
        self._rooms[room_id] = Room(room_id, session, event_bus, player_ids)
        return room_id

    def handle_move(self, room_id, player_id, x, y):
        room = self._get_room(room_id)
        room.handle_click(player_id, x, y)

    def get_snapshot(self, room_id):
        return self._get_room(room_id).get_snapshot()
    
    def get_event_bus(self, room_id):
        return self._get_room(room_id).event_bus

    def get_player_ids(self, room_id):
        return dict(self._get_room(room_id).player_ids)

    def create_waiting_room(self, board_text):
        return self.create_room(board_text, player_ids={})
    
    def seat_player(self, room_id, color, player_id):
        self._get_room(room_id).seat(color, player_id)

    def is_room_full(self, room_id):
        return self._get_room(room_id).is_full()

    def _get_room(self, room_id):
        room = self._rooms.get(room_id)
        if room is None:
            raise UnknownRoomError(f"Unknowen room: {room_id}")
        return room
    
    def room_exists(self, room_id):
        return room_id in self._rooms
    