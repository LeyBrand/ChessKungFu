from model.position import Position

def get_king_moves(board, piece):
    moves = []

    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  
        (1, 1), (1, -1), (-1, 1), (-1, -1) 
    ]
    
    curr_col, curr_row = piece.position.col, piece.position.row
    
    for dc, dr in directions:
        new_col = curr_col + dc
        new_row = curr_row + dr
        new_pos = Position(new_col, new_row)
        
        if board.in_bounds(new_pos):
            target = board.get_piece_at(new_pos)
            
            if target is None:
                moves.append(new_pos)
            elif target.color != piece.color:
                moves.append(new_pos)
    return moves