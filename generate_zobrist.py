import argparse
import random

from dlgo.gotypes import Player, Point

EMPTY_BOARD = 0
MAX63 = '0x7fffffffffffffff'


def generate_hashes(board_size, max_value):
    table = {}

    for row in range(1, board_size + 1):
        for col in range(1, board_size + 1):
            for player in (Player.black, Player.white):
                code = random.randint(0, max_value)
                table[Point(row, col), player] = code

    return table


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-s", "--size", type=int, required=True)
    argument_parser.add_argument("-m", "--max", type=str, default=MAX63)
    arguments = argument_parser.parse_args()

    hashes = generate_hashes(arguments.size, int(arguments.max, base=0))

    print('from dlgo.gotypes import Player, Point')
    print('')
    print('HASH_CODE = {')
    for (pt, p), h in hashes.items():
        print('    ({}, {}): {},'.format(pt, p, h))
    print('}')
    print('')
    print('HASH_CODE_EMPTY = {}'.format(EMPTY_BOARD))


if __name__ == '__main__':
    main()
