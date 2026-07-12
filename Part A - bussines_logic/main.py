import sys
from text_tests.script_parser import parse
from text_tests.script_runner import run
from realtime.real_time_arbiter import RealTimeArbiter

def main():
    RealTimeArbiter.instance().reset()
    raw_input = sys.stdin.read()
    board, commands = parse(raw_input)
    if board and commands:
        run(board, commands)

if __name__ == "__main__":
    main()