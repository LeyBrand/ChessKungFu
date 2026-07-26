import sys
import os

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_C_DIR = os.path.join(_TESTS_DIR, "..")
if os.path.abspath(_PART_C_DIR) not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_C_DIR))

_ROOT_DIR = os.path.join(_TESTS_DIR, "..", "..")
if os.path.abspath(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, os.path.abspath(_ROOT_DIR))

STARTING_BOARD_TEXT = """
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
"""
