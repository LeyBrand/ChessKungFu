from model.position import position

def legal_destinations(piece, board):
        destinations = []
        col, row = piece.cell.col, piece.cell.row
        for direaction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            c, r = col + direaction[0], row + direaction[1]
            while 0 <= c < board.cols and 0 <= r < board.rows:
                  target = board.get_piece_at(position(c, r))
                  destinations.append(position(c, r))
                  if target is not None:
                      break
                  c += direaction[0]
                  r += direaction[1]
        return destinations