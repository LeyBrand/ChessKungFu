import sys
from text_tests.script_parser import parse
from text_tests.script_runner import run

def main():
    raw_input = sys.stdin.read()
    board, commands = parse(raw_input) 
    run(board, commands)

if __name__ == "__main__":
    main()