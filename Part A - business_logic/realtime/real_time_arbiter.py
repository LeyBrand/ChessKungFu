import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.piece import PieceState
from constants import Color


class RealTimeArbiter:
    def __init__(self, board, event_bus=None):
        self.board = board
        self.event_bus = event_bus
        self.game_clock_ms = 0
        self.active_motions = []

    def now(self):
        return self.game_clock_ms

    def advance(self, ms):
        self.game_clock_ms += ms

    def add_motion(self, motion):
        self.active_motions.append(motion)

    def get_active_motions(self):
        return self.active_motions

    def remove_motion(self, motion):
        if motion in self.active_motions:
            self.active_motions.remove(motion)

    def advance_time(self, ms):
        self.game_clock_ms += ms
        king_captured = False

        completed_motions = []
        for motion in self.active_motions:
            if motion.is_complete(self.game_clock_ms):
                completed_motions.append(motion)

        for i, motion1 in enumerate(completed_motions):
            for motion2 in completed_motions[i+1:]:
                same_destination = motion1.end_pos == motion2.end_pos
                swapped_path = (
                    motion1.start_pos == motion2.end_pos and
                    motion1.end_pos == motion2.start_pos
                )

                if same_destination or swapped_path:
                    if motion1.start_time <= motion2.start_time:
                        captured, capturer = motion2.piece, motion1.piece
                    else:
                        captured, capturer = motion1.piece, motion2.piece

                    captured.set_state(PieceState.CAPTURED)

                    if self.event_bus is not None:
                        self.event_bus.publish(
                            "PIECE_CAPTURED",
                            piece_id=captured.id,
                            kind=captured.kind,
                            color=captured.color,
                            captured_by=capturer.color,
                            time_ms=self.game_clock_ms,
                        )

        # Snapshot who was already sitting at each destination BEFORE any
        # motion in this batch lands - otherwise a sibling motion landing on
        # the same square (already handled above, as a mid-air collision)
        # would be misread here as a second, separate capture.
        occupant_before_landing = {
            motion: self.board.get_piece_at(motion.end_pos) for motion in completed_motions
        }

        for motion in completed_motions:
            captured_piece = occupant_before_landing[motion]

            if captured_piece is not None and self.event_bus is not None:
                self.event_bus.publish(
                    "PIECE_CAPTURED",
                    piece_id=captured_piece.id,
                    kind=captured_piece.kind,
                    color=captured_piece.color,
                    captured_by=motion.piece.color,
                    time_ms=self.game_clock_ms,
                )

            if motion.piece.state != PieceState.CAPTURED:
                self.board.move_piece(motion.start_pos, motion.end_pos)
                motion.piece.set_state(PieceState.IDLE)

            self.active_motions.remove(motion)

            if motion.piece.kind == "P":
                promotion_row = 0 if motion.piece.color == Color.WHITE else self.board.rows_length - 1
                if motion.end_pos.row == promotion_row:
                    motion.piece.kind = "Q"

            if captured_piece and captured_piece.kind == "K":
                king_captured = True

        return king_captured

    def reset(self):
        self.game_clock_ms = 0
        self.active_motions = []

    def tick(self, ms):
        return self.advance_time(ms)