from model.position import Position

def get_rook_moves(board, piece):
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for dc, dr in directions:
        curr_col, curr_row = piece.position.col, piece.position.row
        while True:
            curr_col += dc
            curr_row += dr
            new_pos = Position(curr_col, curr_row)
            
            if not board.in_bounds(new_pos):
                break
            
            target = board.get_piece_at(new_pos)
            if target is None:
                moves.append(new_pos)
            else:
                if target.color != piece.color:
                    moves.append(new_pos)
                break
    return moves