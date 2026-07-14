from app import build_app


def run(board, commands):
    state, engine, controller = build_app(board)

    for command in commands:
        controller.handle(command, board)