import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion
from model.piece import PieceState


class MoveResult:
    def __init__(self, success, message):
        self.success = success
        self.message = message


class GameEngine:
    def __init__(self, state):
        self.state = state
        self.arbiter = RealTimeArbiter(self.state.board)
        self.current_selection = None
        self.move_history = []
        self.airborne = []

    def has_motion_on_path(self, from_pos, to_pos):
        for motion in self.arbiter.get_active_motions():
            if motion.start_pos == from_pos or motion.end_pos == to_pos:
                return True
        return False

    def _is_reserved_by_friend(self, position, color):
        for entry in self.airborne:
            if entry["origin"] == position and entry["piece"].color == color:
                return True
        return False

    def request_move(self, from_pos, to_pos):
        if self.state.game_over:
            return MoveResult(False, "game_over")

        if not self.state.board.in_bounds(from_pos):
            return MoveResult(False, "out_of_bounds")

        piece = self.state.board.get_piece_at(from_pos)
        if piece is None:
            return MoveResult(False, "empty_source")

        if self.has_motion_on_path(from_pos, to_pos):
            return MoveResult(False, "motion_in_progress")

        if self._is_reserved_by_friend(to_pos, piece.color):
            return MoveResult(False, "reserved_square")

        from rules.rule_engine import validate_move
        if validate_move(self.state.board, piece, to_pos) != "ok":
            return MoveResult(False, "invalid_move")

        now = self.arbiter.now()
        motion = Motion(piece, from_pos, to_pos, now)
        self.arbiter.add_motion(motion)

        return MoveResult(True, "ok")

    def wait(self, ms):
        if self.arbiter.tick(ms):
            self.state.game_over = True
        self._resolve_airborne()

    def _resolve_airborne(self):
        now = self.arbiter.now()
        still_airborne = []

        for entry in self.airborne:
            if now >= entry["land_time"]:
                piece = entry["piece"]
                origin = entry["origin"]

                occupant = self.state.board.get_piece_at(origin)
                self.state.board.place_piece(piece, origin)
                piece.set_state(PieceState.IDLE)

                if occupant is not None and occupant.kind == "K":
                    self.state.game_over = True
            else:
                still_airborne.append(entry)

        self.airborne = still_airborne

    def snapshot(self):
        pieces_state = {}
        for (col, row), piece in self.state.board.pieces.items():
            pieces_state[(col, row)] = {
                'id': piece.id,
                'kind': piece.kind,
                'color': piece.color,
                'state': piece.state
            }

        active_motions_snapshot = []
        for motion in self.arbiter.get_active_motions():
            active_motions_snapshot.append({
                'from': (motion.start_pos.col, motion.start_pos.row),
                'to': (motion.end_pos.col, motion.end_pos.row),
                'started_at': motion.start_time,
                'duration': motion.duration_ms,
                'piece_id': motion.piece.id
            })

        return {
            'timestamp': self.arbiter.now(),
            'board_pieces': pieces_state,
            'game_over': self.state.game_over,
            'active_motions': active_motions_snapshot,
            'move_history': self.move_history
        }

    def jump(self, pos):
        if self.state.game_over:
            return MoveResult(False, "game_over")

        piece = self.state.board.get_piece_at(pos)
        if piece is None:
            return MoveResult(False, "empty_source")

        if self.has_motion_on_path(pos, pos):
            return MoveResult(False, "motion_in_progress")

        now = self.arbiter.now()
        self.state.board.remove_piece(pos)
        self.airborne.append({
            "piece": piece,
            "origin": pos,
            "land_time": now + MOVE_MS
        })

        return MoveResult(True, "ok")