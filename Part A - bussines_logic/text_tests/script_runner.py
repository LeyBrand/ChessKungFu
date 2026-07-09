from input.controller import Controller
controller = Controller()
def run(board, commands):
    for command in commands:
        controller.handle(command, board)
        
