from model.position import Position

def get_pawn_moves(board, piece):
    moves = []

    curr_col, curr_row = piece.position.col, piece.position.row

    # לבן זז כלפי מעלה (row פוחת), שחור זז כלפי מטה (row גדל)
    direction = -1 if piece.color == "white" else 1

    # 1. צעד קדימה - רק אם המשבצת ריקה (אין אכילה בצעד ישר)
    forward_pos = Position(curr_col, curr_row + direction)
    if board.in_bounds(forward_pos):
        target = board.get_piece_at(forward_pos)
        if target is None:
            moves.append(forward_pos)

    # 2. אכילה באלכסון - רק אם יש שם כלי של היריב
    diagonal_offsets = [(-1, direction), (1, direction)]
    for dc, dr in diagonal_offsets:
        diag_pos = Position(curr_col + dc, curr_row + dr)
        if board.in_bounds(diag_pos):
            target = board.get_piece_at(diag_pos)
            if target is not None and target.color != piece.color:
                moves.append(diag_pos)

    return moves