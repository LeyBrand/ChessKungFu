import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion


class MoveResult:
    """תוצאה של ניסיון move - חוצה את הגבול הציבורי של GameEngine."""
    def __init__(self, is_accepted, reason):
        self.is_accepted = is_accepted
        self.reason = reason


class GameEngine:
    """
    מתאם שירות-האפליקציה. זהו גבול הפקודות הציבורי בשימוש
    Controller ו-TextTestRunner.

    GameEngine אינו מכיל:
    - לוגיקת תנועה ספציפית לכלי (זה RuleEngine / piece_rules)
    - מיפוי פיקסלים (זה board_mapper)
    - קוד רינדור (זה board_printer)
    - פירוש טקסט (זה script_parser / command_parser)
    - לוגיקת מריץ בדיקות
    """

    def __init__(self, state):
        self.state = state
        self.arbiter = RealTimeArbiter(self.state.board)
        self.current_selection = None
        self.move_history = []
        # כלים ש"קפצו" וכרגע נעדרים זמנית מהלוח (עד שינחתו בחזרה)
        self.airborne = []

    # ---- שאלות הגנה ברמת האפליקציה (לא ידע-שחמט) ----

    def _is_game_over(self):
        return self.state.game_over

    def _is_route_busy(self, piece):
        """האם לכלי הזה כבר יש תנועה פעילה במסלול המשותף?"""
        return any(motion.piece is piece for motion in self.arbiter.get_active_motions())

    def _is_reserved_by_friend(self, position, color):
        """האם המשבצת שמורה לכלי ידידותי שכרגע 'באוויר' (קפץ)?"""
        return any(
            entry["origin"] == position and entry["piece"].color == color
            for entry in self.airborne
        )

    # ---- הפקודות הציבוריות ----

    def request_move(self, from_pos, to_pos):
        """
        הנקודה היחידה שמבקשים דרכה להזיז כלי.
        סדר הבדיקות: הגנות ברמת האפליקציה (game_over, מסלול תפוס),
        ורק אחרי שהן עוברות - מעבירים ל-RuleEngine לבדיקת חוקיות.
        """
        if self._is_game_over():
            return MoveResult(False, "game_over")

        piece = self.state.board.get_piece_at(from_pos)
        if piece is None:
            return MoveResult(False, "empty_source")

        if self._is_route_busy(piece):
            return MoveResult(False, "motion_in_progress")

        if self._is_reserved_by_friend(to_pos, piece.color):
            return MoveResult(False, "reserved_square")

        from rules.rule_engine import validate_move
        validation = validate_move(self.state.board, piece, to_pos)
        if validation != "ok":
            # סיבות ברמת הכלל מועתקות ישירות מ-MoveValidation
            return MoveResult(False, validation)

        # המהלך אומת - מתחילים Motion דרך RealTimeArbiter
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
        """קפיצה - אותן הגנות ברמת אפליקציה כמו request_move, בלי RuleEngine."""
        if self._is_game_over():
            return MoveResult(False, "game_over")

        piece = self.state.board.get_piece_at(pos)
        if piece is None:
            return MoveResult(False, "empty_source")

        if self._is_route_busy(piece):
            return MoveResult(False, "motion_in_progress")

        now = self.arbiter.now()
        self.state.board.remove_piece(pos)
        self.airborne.append({
            "piece": piece,
            "origin": pos,
            "land_time": now + MOVE_MS
        })

        return MoveResult(True, "ok")

    def wait(self, ms):
        """מאצילה קידום זמן מדומה ל-RealTimeArbiter, ומקבלת התראת אכילת מלך אם קרתה."""
        if self.arbiter.advance_time(ms):
            self.state.game_over = True

        self._resolve_airborne()

    def _resolve_airborne(self):
        """
        פתרון נחיתות - אם אויב תפס משבצת של כלי 'באוויר', הוא נאכל בנחיתה.
        זהו פתרון-הגעה מקביל לזה של RealTimeArbiter, וגם הוא יכול לגרום ל-game_over.
        """
        now = self.arbiter.now()
        still_airborne = []

        for entry in self.airborne:
            if now >= entry["land_time"]:
                piece = entry["piece"]
                origin = entry["origin"]

                occupant = self.state.board.get_piece_at(origin)
                self.state.board.place_piece(piece, origin)

                if occupant is not None and occupant.kind == "K":
                    self.state.game_over = True
            else:
                still_airborne.append(entry)

        self.airborne = still_airborne

    def snapshot(self):
        """GameSnapshot לקריאה-בלבד, לשימוש ה-renderer וה-BoardPrinter."""
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