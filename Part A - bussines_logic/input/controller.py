from constants import EMPTY_CELL

selected_pos = None

def click(position, board):
    global selected_pos
    if selected_pos is None:
        if board.in_bounds(position):
            piece = board.get_piece_at(position)
            if piece is not None and piece != EMPTY_CELL:
                selected_pos = position
    else:
        # כאן קורה המהלך
        if board.in_bounds(position):
            piece = board.get_piece_at(selected_pos)
            
            # קריאה ל-RuleEngine כדי לבדוק חוקיות
            from rules.rule_engine import validate_move
            result = validate_move(board, piece, position)
            
            if result == "ok":
                # ביצוע המהלך
                board.remove_piece(selected_pos)
                board.place_piece(piece, position)
                selected_pos = None  # איפוס לאחר מהלך מוצלח
            else:
                # אופציונלי: כאן תוכלי להדפיס את השגיאה (למשל: "illegal_piece_move")
                # איפוס בחירה אם המהלך לא חוקי (או להשאיר את הבחירה)
                selected_pos = None 
        else:
            selected_pos = None