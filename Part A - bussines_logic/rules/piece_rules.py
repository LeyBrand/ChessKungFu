from abc import ABC, abstractmethod
from model.position import Position


class PieceRules(ABC):
    @abstractmethod
    def legal_destinations(self, board, piece):
        raise NotImplementedError

    def _sliding_moves(self, board, piece, directions):
        moves = []
        curr_col, curr_row = piece.position.col, piece.position.row

        for dc, dr in directions:
            new_col, new_row = curr_col + dc, curr_row + dr
            new_pos = Position(new_col, new_row)

            while board.in_bounds(new_pos):
                target = board.get_piece_at(new_pos)

                if target is None:
                    moves.append(new_pos)
                else:
                    if target.color != piece.color:
                        moves.append(new_pos)
                    break  # כלי (של יריב או שלנו) חוסם את ההמשך

                new_col += dc
                new_row += dr
                new_pos = Position(new_col, new_row)

        return moves

    def _single_step_moves(self, board, piece, offsets):
        moves = []
        curr_col, curr_row = piece.position.col, piece.position.row

        for dc, dr in offsets:
            new_pos = Position(curr_col + dc, curr_row + dr)

            if board.in_bounds(new_pos):
                target = board.get_piece_at(new_pos)
                if target is None or target.color != piece.color:
                    moves.append(new_pos)

        return moves