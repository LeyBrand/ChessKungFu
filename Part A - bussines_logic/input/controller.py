from input.board_mapper import pixel_to_cell
from model.position import Position


class Controller:
    """
    הבקר מתרגם פעולות משתמש (קליקים) לפקודות משחק.
    הוא אינו מחליט על חוקיות שחמט - זו אחריות של RuleEngine, דרך GameEngine.

    הבקר אסור לו:
    - לקרוא ישירות ל-Board.move_piece
    - לקרוא ישירות ל-RuleEngine
    """

    def __init__(self, engine):
        self.engine = engine
        self.selected_pos = None

    def handle(self, command, board):
        name = command["name"]
        args = command.get("args", [])

        actions = {
            "click": self._handle_click,
            "print": self._handle_print,
            "wait": self._handle_wait,
            "jump": self._handle_jump,
        }

        if name in actions:
            actions[name](args, board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.click(Position(col, row), board)

    def click(self, position, board):
        in_bounds = board.in_bounds(position)

        if self.selected_pos is None:
            # אין בחירה - קליקים מחוץ ללוח מתעלמים
            if not in_bounds:
                return

            # קליק ראשון על תא ריק - מתעלמים
            piece = board.get_piece_at(position)
            if piece is None:
                return

            self.selected_pos = position
            return

        # יש בחירה קיימת:
        if not in_bounds:
            # קליק מחוץ ללוח מבטל את הבחירה, בלי לשלוח פקודה ל-GameEngine
            self.selected_pos = None
            return

        # קליק שני על כלי ידידותי (אותו צבע) - מחליף את הבחירה, לא שולח request_move
        # (זו בדיקת בעלות פשוטה על מידע גולמי מה-Board, לא החלטת חוקיות-שחמט)
        selected_piece = board.get_piece_at(self.selected_pos)
        clicked_piece = board.get_piece_at(position)
        if clicked_piece is not None and selected_piece is not None and clicked_piece.color == selected_piece.color:
            self.selected_pos = position
            return

        # קליק שני בתוך הלוח - שולחים בקשת מהלך ל-GameEngine
        source = self.selected_pos
        destination = position
        self.engine.request_move(source, destination)

        # מנקים את הבחירה תמיד, בין אם המהלך חוקי ובין אם לא
        self.selected_pos = None

    def _handle_jump(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.engine.jump(Position(col, row))

    def _handle_wait(self, args, board):
        ms = int(args[0])
        self.engine.wait(ms)

    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)