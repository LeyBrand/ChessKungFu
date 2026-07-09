# https://github.com/LeyBrand/ChessKungFu

from final.board import board_piece_parsing, print_board
from final.game import ChessGame

def processer(game_factory = None):
    import sys
    input_data = sys.stdin.read()

    b_idx = input_data.find("Board:")
    c_idx = input_data.find("Commands:")

    board = board_piece_parsing(
        input_data[b_idx + len("Board:"):c_idx].strip())
    
    game = game_factory(board) if game_factory else ChessGame(board)

    for line in input_data[c_idx + len("Commands:"):].strip().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "click":
            game.click(int(parts[1]), int(parts[2]))
        elif parts[0] == "wait":
            game.game_time += int(parts[1])
        elif parts[0] == "print" and parts[1] == "board":
            game.print_board()

if __name__ == "__main__":
    processer()