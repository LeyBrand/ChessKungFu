import sys; sys.path.insert(0,'.')
from final.board import board_piece_parsing, CELL_SIZE
from final.rules import is_valid_move, is_in_movement, is_dst_taken, add_pending_move, apply_arrived_moves

board = board_piece_parsing('. . .\n. wP .\n. . .')
pending_moves = []
game_over = [False, None]
selected_pos = None
game_time = 0

def click(x, y):
    global selected_pos
    col, row = x // CELL_SIZE, y // CELL_SIZE
    apply_arrived_moves(board, pending_moves, game_time, game_over)
    print(f'  after apply: board[0]={board[0]}, pending={pending_moves}, selected={selected_pos}')
    if selected_pos is None:
        if board[row][col] != '.' and not is_in_movement((col,row), pending_moves):
            selected_pos = (col, row)
            print(f'  selected: {selected_pos}')
        else:
            print(f'  nothing selected, board[{row}][{col}]={board[row][col]}, in_movement={is_in_movement((col,row),pending_moves)}')
    else:
        src, dst = selected_pos, (col, row)
        piece = board[src[1]][src[0]]
        valid = is_valid_move(piece, src, dst, board)
        taken = is_dst_taken(dst, pending_moves)
        print(f'  try move piece={piece} from {src} to {dst}, valid={valid}, taken={taken}')
        if valid and not taken:
            add_pending_move(piece, src, dst, game_time, pending_moves)
            selected_pos = None
        else:
            selected_pos = (col,row) if board[row][col] != '.' and not is_in_movement((col,row),pending_moves) else None
            print(f'  move failed, new selected={selected_pos}')

for cmd in ['click 150 150','click 150 50','wait 1000','click 150 50','click 250 150','wait 1000']:
    print(f'\nCMD: {cmd}')
    p = cmd.split()
    if p[0]=='click': click(int(p[1]),int(p[2]))
    elif p[0]=='wait': game_time+=int(p[1])

apply_arrived_moves(board, pending_moves, game_time, game_over)
print('\nfinal board:')
for r in board: print(' '.join(r))
