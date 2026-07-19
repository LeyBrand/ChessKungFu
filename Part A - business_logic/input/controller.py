from input.board_mapper import pixel_to_cell
from model.position import Position


class Controller:

    def __init__(self, engine):
        self.engine = engine
        self.selected_pos = None
        self.actions = {
            "click": self._handle_click,
            "wait": self._handle_wait,
            "jump": self._handle_jump,
        }


    def handle(self, command, board):
        name = command["name"]
        args = command.get("args", [])

        if name in self.actions:
            self.actions[name](args, board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.click(Position(col, row), board)

    def click(self, position, board):
        in_bounds = board.in_bounds(position)

        if self.selected_pos is None:
            if not in_bounds:
                return

            piece = board.get_piece_at(position)
            if piece is None:
                return

            self.selected_pos = position
            return

        if not in_bounds:
            self.selected_pos = None
            return

        selected_piece = board.get_piece_at(self.selected_pos)
        clicked_piece = board.get_piece_at(position)
        if clicked_piece is not None and selected_piece is not None and clicked_piece.color == selected_piece.color:
            self.selected_pos = position
            return

        source = self.selected_pos
        destination = position
        result = self.engine.request_move(source, destination)
        print(f"MOVE {source} -> {destination}: accepted={result.is_accepted}, reason={result.reason}")  # זמני לדיבוג

        self.selected_pos = None
        
    def _handle_jump(self, args, board):
        # x, y (args) לא בשימוש יותר - הכלי שקופץ הוא זה שכבר נבחר
        # (בדיוק כמו שהקליק השני לא "מזהה מחדש" את הכלי הנבחר).
        self.jump(board)

    def jump(self, board):
        """
        Launches whichever piece is currently selected - the jump
        counterpart of click()'s second-click branch. Requires a prior
        click() to have selected a piece; otherwise it's a no-op.
        """
        if self.selected_pos is None:
            return

        result = self.engine.jump(self.selected_pos)
        print(f"JUMP {self.selected_pos}: accepted={result.is_accepted}, reason={result.reason}")  # זמני לדיבוג

        self.selected_pos = None

    def _handle_wait(self, args, board):
        ms = int(args[0])
        self.engine.wait(ms)