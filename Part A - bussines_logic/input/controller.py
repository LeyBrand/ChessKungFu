from constants import EMPTY_CELL
from input.board_mapper import pixel_to_cell
from model.position import *
from model.piece import PieceState
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion

class Controller:
    def __init__(self):
        self.selected_pos = None
        self.pending_motions = []

    def handle(self, command, board):
        self._resolve_motions(board)

        name = command["name"]
        actions = {
            "click": self._handle_click,
            "print": self._handle_print,
            "wait": self._handle_wait
        }

        if name in actions:
            actions[name](command["args"], board)

    def _resolve_motions(self, board):
        arbiter = RealTimeArbiter.instance()
        now = arbiter.now()
        still_pending = []

        for motion in self.pending_motions:
            if motion.is_complete(now):
                board.remove_piece(motion.start_pos)
                motion.piece.move_to(motion.end_pos)
                board.place_piece(motion.piece, motion.end_pos)
                motion.piece.set_state(PieceState.IDLE)
            else:
                still_pending.append(motion)

        self.pending_motions = still_pending

    def _handle_wait(self, args, board):
        ms = int(args[0])
        RealTimeArbiter.instance().advance(ms)
        self._resolve_motions(board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.click(Position(col, row), board)

    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)

    def click(self, position, board):
        if not board.in_bounds(position):
            self.selected_pos = None
            return

        clicked_piece = board.get_piece_at(position)
        is_empty = clicked_piece is None or clicked_piece == EMPTY_CELL

        if self.selected_pos is None:
            if not is_empty:
                self.selected_pos = position
        else:
            selected_piece = board.get_piece_at(self.selected_pos)

            if not is_empty and clicked_piece.color == selected_piece.color:
                if position == self.selected_pos:
                    self.selected_pos = None  # ביטול בחירה בלחיצה על אותו כלי
                else:
                    self.selected_pos = position  # החלפת בחירה לכלי החדש

            # אם לחצנו על משבצת ריקה או כלי אויב -> מבצעים תנועה
            else:
                from rules.rule_engine import validate_move
                result = validate_move(board, selected_piece, position)

                if result == "ok":
                    # לא מזיזים מיידית - יוצרים תנועה שתושלם רק כשעובר מספיק זמן
                    now = RealTimeArbiter.instance().now()
                    motion = Motion(selected_piece, self.selected_pos, position, now)
                    selected_piece.set_state(PieceState.MOVING)
                    self.pending_motions.append(motion)

                # בסיום ניסיון תנועה, תמיד מנקים את הבחירה
                self.selected_pos = None