EMPTY_CELL = '.'
MOVE_MS = 1000

VALID_PIECES = {
    '.', 
    'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
    'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
}

CELL_SIZE = 100

WHITE = 'w'
BLACK = 'b'

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765

PIECE_VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}

def value_of(kind):
    return PIECE_VALUES.get(kind, 0)

from enum import Enum

class Color(str, Enum):
    WHITE = "white"
    BLACK = "black"

class MessageType(str, Enum):
    JOIN_ROOM = "JOIN_ROOM"
    MOVE = "MOVE"
    JUMP = "JUMP"
    PLAY = "PLAY"
    CANCEL_SEEK = "CANCEL_SEEK"
    LOGIN = "LOGIN"

    SNAPSHOT = "SNAPSHOT"
    ERROR = "ERROR"
    MATCH_FOUND = "MATCH_FOUND"
    MATCH_NOT_FOUND = "MATCH_NOT_FOUND"
    OPPONENT_DISCONNECTED = "OPPONENT_DISCONNECTED"
    OPPONENT_RECONNECTED = "OPPONENT_RECONNECTED"
    LOGIN_OK = "LOGIN_OK"
    LOGIN_ERROR = "LOGIN_ERROR"
    CREATE_ROOM = "CREATE_ROOM"
    ROOM_CREATED = "ROOM_CREATED"
    ROOM_JOINED = "ROOM_JOINED"