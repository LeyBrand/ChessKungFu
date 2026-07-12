def validate_move(board, piece, destination):
    if not board.in_bounds(destination):
        return "outside_board"

    if not piece.is_available():
        return "empty_source"
    
    legal_moves = board.legal_destinations(piece)
    is_legal = False
    for move in legal_moves:
        if move.col == destination.col and move.row == destination.row:
            is_legal = True
            break
            
    if not is_legal:
        return "illegal_piece_move"

    if board.is_friendly_destination(piece, destination):
        return "friendly_destination"

    return "ok"