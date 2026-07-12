import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.piece import PieceState


class RealTimeArbiter:
    def __init__(self, board):
        self.board = board
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

    def tick(self, ms):
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
                        motion2.piece.set_state(PieceState.CAPTURED)
                    else:
                        motion1.piece.set_state(PieceState.CAPTURED)

        for motion in completed_motions:
            captured_piece = self.board.get_piece_at(motion.end_pos)

            if motion.piece.state != PieceState.CAPTURED:
                self.board.remove_piece(motion.start_pos)
                motion.piece.move_to(motion.end_pos)
                self.board.place_piece(motion.piece, motion.end_pos)
                motion.piece.set_state(PieceState.IDLE)

            self.active_motions.remove(motion)

            if motion.piece.kind == "P":
                promotion_row = 0 if motion.piece.color == "white" else self.board.rows - 1
                if motion.end_pos.row == promotion_row:
                    motion.piece.kind = "Q"

            if captured_piece and captured_piece.kind == "K":
                king_captured = True

        return king_captured

    def reset(self):
        self.game_clock_ms = 0
        self.active_motions = []