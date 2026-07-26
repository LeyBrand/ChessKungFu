from input.board_mapper import pixel_to_cell
from model.position import Position


class Controller:

    def __init__(self, engine):
        self.engine = engine
        self.selected_pos = None
        self.selected_by = None
        self.actions = {
            "click": self._handle_click,
            "wait": self._handle_wait,
            "jump": self._handle_jump,
        }


    def handle(self, command, board):
        name = command["name"]
        args = command.get("args", [])
        color = command.get("color")

        if name in self.actions:
            self.actions[name](args, board, color)

    def _handle_click(self, args, board, color):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.click(Position(col, row), board, color)

    def click(self, position, board, color):
        in_bounds = board.in_bounds(position)

        if self.selected_pos is None:
            if not in_bounds:
                return
            piece = board.get_piece_at(position)
            if piece is None:
                return
            if color is not None and piece.color != color:
                return
            self.selected_pos = position
            self.selected_by = color
            return
        
        if color is not None and color != self.selected_by:
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

        self.selected_pos = None
        self.selected_by = None
        
    def _handle_jump(self, args, board, color):
        self.jump(board, color)

    def jump(self, board, color):
        if self.selected_pos is None:
            return
        if color is not None and color != self.selected_by:
            return
        result = self.engine.jump(self.selected_pos)

        self.selected_pos = None
        self.selected_by = None

    def _handle_wait(self, args, board, color):
        ms = int(args[0])
        self.engine.wait(ms)