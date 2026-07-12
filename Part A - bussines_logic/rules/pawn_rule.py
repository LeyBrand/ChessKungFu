from model.position import Position

def get_pawn_moves(board, piece):
    moves = []

    curr_col, curr_row = piece.position.col, piece.position.row

    direction = -1 if piece.color == "white" else 1

    start_row = board.rows - 2 if piece.color == "white" else 1

    single_step_pos = Position(curr_col, curr_row + direction)
    single_step_clear = False

    if board.in_bounds(single_step_pos):
        target = board.get_piece_at(single_step_pos)
        if target is None:
            moves.append(single_step_pos)
            single_step_clear = True

    if curr_row == start_row and single_step_clear:
        double_step_pos = Position(curr_col, curr_row + 2 * direction)
        if board.in_bounds(double_step_pos):
            target = board.get_piece_at(double_step_pos)
            if target is None:
                moves.append(double_step_pos)

    diagonal_offsets = [(-1, direction), (1, direction)]
    for dc, dr in diagonal_offsets:
        diag_pos = Position(curr_col + dc, curr_row + dr)
        if board.in_bounds(diag_pos):
            target = board.get_piece_at(diag_pos)
            if target is not None and target.color != piece.color:
                moves.append(diag_pos)

    return moves