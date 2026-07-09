from input.controller import handle
def run(commands, board):
    for command in commands:
        handle(command, board)