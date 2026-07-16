import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion
from model.piece import PieceState


class MoveResult:
    def __init__(self, is_accepted, reason):
        self.is_accepted = is_accepted
        self.reason = reason


class GameEngine:
    def __init__(self, state):
        self.state = state
        self.arbiter = RealTimeArbiter(self.state.board)
        self.move_history = []
        self.airborne = []


    def _is_game_over(self):
        return self.state.game_over

    def _is_route_busy(self, piece):
        return any(motion.piece is piece for motion in self.arbiter.get_active_motions())

    def _is_reserved_by_friend(self, position, color):
        return any(
            entry["origin"] == position and entry["piece"].color == color
            for entry in self.airborne
        )

    def request_move(self, from_pos, to_pos):
        if self._is_game_over():
            return MoveResult(False, "game_over")

        piece = self.state.board.get_piece_at(from_pos)
        if piece is not None:
            if self._is_route_busy(piece):
                return MoveResult(False, "motion_in_progress")

            if self._is_reserved_by_friend(to_pos, piece.color):
                return MoveResult(False, "reserved_square")

        from rules.rule_engine import validate_move
        validation = validate_move(self.state.board, from_pos, to_pos)
        if not validation.is_valid:
            return MoveResult(False, validation.reason)
        now = self.arbiter.now()
        motion = Motion(piece, from_pos, to_pos, now)
        self.arbiter.add_motion(motion)
        self.move_history.append({
            "from": (from_pos.col, from_pos.row),
            "to": (to_pos.col, to_pos.row),
            "piece_id": piece.id
        })

        return MoveResult(True, "ok")

    def jump(self, pos):
        if self._is_game_over():
            return MoveResult(False, "game_over")

        piece = self.state.board.get_piece_at(pos)
        if piece is None:
            return MoveResult(False, "empty_source")

        if self._is_route_busy(piece):
            return MoveResult(False, "motion_in_progress")

        now = self.arbiter.now()
        piece.set_state(PieceState.JUMPING)
        self.state.board.remove_piece(pos)
        land_time = now + MOVE_MS
        self.airborne.append({
            "piece": piece,
            "origin": pos,
            "land_time": land_time
        })
        print(f"JUMP TAKEOFF piece={piece.id} at {pos}, now={now}ms, will land at {land_time}ms")  # זמני לדיבוג

        return MoveResult(True, "ok")

    def wait(self, ms):
        if self.arbiter.advance_time(ms):
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
                print(f"JUMP LANDING piece={piece.id} back at {origin}, now={now}ms"
                      + (f", captured occupant={occupant.id}" if occupant is not None else ""))  # זמני לדיבוג

                if occupant is not None and occupant.kind == "K":
                    self.state.game_over = True
            else:
                still_airborne.append(entry)

        self.airborne = still_airborne

    def snapshot(self, selected_pos=None):
        from view.game_snapshot import GameSnapshot

        now = self.arbiter.now()
        active_by_piece_id = {
            motion.piece.id: motion for motion in self.arbiter.get_active_motions()
        }

        pieces_snapshot = []
        for (col, row), piece in self.state.board.pieces.items():
            motion = active_by_piece_id.get(piece.id)

            motion_info = None
            if motion is not None and motion.duration_ms > 0:
                progress = (now - motion.start_time) / motion.duration_ms
                progress = min(1.0, max(0.0, progress))
                motion_info = {
                    "from": (motion.start_pos.col, motion.start_pos.row),
                    "to": (motion.end_pos.col, motion.end_pos.row),
                    "progress": progress,
                }

            pieces_snapshot.append({
                'id': piece.id,
                'kind': piece.kind,
                'color': piece.color,
                'state': piece.state,
                'cell': (col, row),
                'motion': motion_info,
            })

        for entry in self.airborne:
            piece = entry["piece"]
            col, row = entry["origin"].col, entry["origin"].row
            pieces_snapshot.append({
                'id': piece.id,
                'kind': piece.kind,
                'color': piece.color,
                'state': piece.state,
                'cell': (col, row),
                'motion': None,
            })

        selected_cell = None
        if selected_pos is not None:
            selected_cell = (selected_pos.col, selected_pos.row)

        return GameSnapshot(
            board_width=self.state.board.cols_length,
            board_height=self.state.board.rows_length,
            pieces=pieces_snapshot,
            selected_cell=selected_cell,
            game_over=self.state.game_over,
            timestamp=now,
        )