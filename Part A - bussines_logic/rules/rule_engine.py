from rules.rook_rule import RookRules
from rules.king_rule import KingRules
from rules.knight_rule import KnightRules
from rules.bishop_rule import BishopRules
from rules.queen_rule import QueenRules
from rules.pawn_rule import PawnRules


# מפה משותפת - RuleEngine, לא Board, הוא הבעלים של הידע הזה
_RULES = {
    "R": RookRules(),
    "K": KingRules(),
    "N": KnightRules(),
    "B": BishopRules(),
    "Q": QueenRules(),
    "P": PawnRules(),
}


def get_legal_destinations(board, piece):
    rules = _RULES.get(piece.kind)
    if rules is None:
        return []
    return rules.legal_destinations(board, piece)


def validate_move(board, piece, destination):
    if not board.in_bounds(destination):
        return "outside_board"

    if not piece.is_available():
        return "empty_source"

    legal_moves = get_legal_destinations(board, piece)
    is_legal = False
    for move in legal_moves:
        if move.col == destination.col and move.row == destination.row:
            is_legal = True
            break

    if not is_legal:
        return "illegal_piece_move"

    target = board.get_piece_at(destination)
    if target is not None and target.color == piece.color:
        return "friendly_destination"

    return "ok"