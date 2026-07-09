def validate_move(board, piece, destination):
    """
    Validates if a move is legal based on the current board state and piece type.
    
    Args:
        board (board): The current state of the chess board.
        piece (piece): The piece to be moved.
        destination (position): The target position for the move.
    """

    if not (0 <= destination.col < 8 and 0 <= destination.row < 8):
        return "outside_board"

    legal_moves = board.legal_destinations(piece)
    if destination not in legal_moves:
        return "illegal_piece_move"

    if board.is_friendly_destination(piece, destination):
        return "friendly_destination"
    
    if piece.state != "idle":
        return "empty_source"

    return "ok"