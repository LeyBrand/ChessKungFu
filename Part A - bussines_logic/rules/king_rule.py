from model.position import Position

def get_king_moves(board, piece):
    moves = []
    # המלך יכול לזוז משבצת אחת לכל הכיוונים (אופקי, אנכי ואלכסוני)
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  # ישרים
        (1, 1), (1, -1), (-1, 1), (-1, -1) # אלכסונים
    ]
    
    curr_col, curr_row = piece.position.col, piece.position.row
    
    for dc, dr in directions:
        new_col = curr_col + dc
        new_row = curr_row + dr
        new_pos = Position(new_col, new_row)
        
        # 1. בדיקה שהמיקום בתוך הלוח
        if board.in_bounds(new_pos):
            target = board.get_piece_at(new_pos)
            
            # 2. אם המשבצת ריקה - אפשר לזוז
            if target is None:
                moves.append(new_pos)
            # 3. אם יש כלי של היריב - אפשר לאכול (אופציונלי, בהתאם לחוקים שלך)
            elif target.color != piece.color:
                moves.append(new_pos)
                
    return moves