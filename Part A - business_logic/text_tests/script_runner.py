from app import build_app
from data_io.board_printer import print_board


def run(board, commands):
    state, engine, controller = build_app(board)

    for command in commands:
        if command["name"] == "print":
            print_board(board)
            continue

        controller.handle(command, board)