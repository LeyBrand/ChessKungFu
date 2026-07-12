from model.position import Position

def get_bishop_moves(board, piece):
    moves = []

    directions = [
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # אלכסונים
    ]

    curr_col, curr_row = piece.position.col, piece.position.row

    for dc, dr in directions:
        new_col = curr_col + dc
        new_row = curr_row + dr
        new_pos = Position(new_col, new_row)

        # ממשיכים בכיוון עד שיוצאים מהלוח או פוגעים בכלי
        while board.in_bounds(new_pos):
            target = board.get_piece_at(new_pos)

            # 1. אם המשבצת ריקה - אפשר לזוז, וממשיכים הלאה באותו כיוון
            if target is None:
                moves.append(new_pos)
            else:
                # 2. אם יש כלי של היריב - אפשר לאכול, אבל עוצרים כאן
                if target.color != piece.color:
                    moves.append(new_pos)
                break  # בכל מקרה, כלי (של יריב או שלנו) חוסם את ההמשך

            new_col += dc
            new_row += dr
            new_pos = Position(new_col, new_row)
    return moves