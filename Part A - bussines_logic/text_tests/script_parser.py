from data_io.board_parser import parse_board
from data_io.command_parser import parse_commands 

def parse(raw_script):
    parts = raw_script.split("Commands:")
    board_text = parts[0].replace("Board:", "").strip()
    commands_text = parts[1].strip()
    
    board = parse_board(board_text)
    commands = parse_commands(commands_text)
    
    if board and commands:
        return board, commands
    return None, None