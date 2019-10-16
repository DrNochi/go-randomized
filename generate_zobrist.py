import random

from dlgo.gotypes import Player, Point

MAX63 = 0x7fffffffffffffff

table = {}
empty_board = 0
for row in range(1, 20):
    for col in range(1, 20):
        for player in (Player.black, Player.white):
            code = random.randint(0, MAX63)
            table[Point(row, col), player] = code

print('from dlgo.gotypes import Player, Point')
print('')
print('HASH_CODE = {')
for (pt, p), h in table.items():
    print('    ({}, {}): {},'.format(pt, p, h))
print('}')
print('')
print('HASH_CODE_EMPTY = {}'.format(empty_board))
