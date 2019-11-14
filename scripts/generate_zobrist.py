import random
import sys
from argparse import ArgumentParser

from dlgo.go import Point, Player


def generate_zobrist_hashes(board_size):
    return {
        (point, color): random.randint(1, sys.maxsize)
        for point in (Point(r, c) for r in range(1, board_size + 1) for c in range(1, board_size + 1))
        for color in Player
    }


def print_python_code(hashes):
    print('from .types import Point, Player')
    print('')
    print('hashes = {')
    for (point, color), hash_code in hashes.items():
        print(f'    ({point}, {color}): {hash_code},')
    print('}')
    print('')
    print('empty_board = 0')
    print('')


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-s', '--size', default=25, type=int, help='the maximum supported board size')
    args = arg_parser.parse_args()

    hash_table = generate_zobrist_hashes(args.size)
    print_python_code(hash_table)
