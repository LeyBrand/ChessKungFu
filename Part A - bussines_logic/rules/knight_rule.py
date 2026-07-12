from model.position import Position

def get_knight_moves(board, piece):
    moves = []

    offsets = [
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    ]

    curr_col, curr_row = piece.position.col, piece.position.row

    for dc, dr in offsets:
        new_col = curr_col + dc
        new_row = curr_row + dr
        new_pos = Position(new_col, new_row)

        # 1. בדיקה שהמיקום בתוך הלוח
        if board.in_bounds(new_pos):
            target = board.get_piece_at(new_pos)

            # 2. אם המשבצת ריקה - אפשר לזוז
            if target is None:
                moves.append(new_pos)
            # 3. אם יש כלי של היריב - אפשר לאכול
            elif target.color != piece.color:
                moves.append(new_pos)
    return moves