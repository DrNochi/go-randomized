from dlgo.gotypes import Player, Point

player_chars = {
    None: ' . ',
    Player.black: ' x ',
    Player.white: ' o ',
}


def int_to_char(n):
    return chr(ord('a') + n - 1)


def char_to_int(c):
    return ord(c) - ord('a') + 1


def print_move(player, move):
    if move.is_pass:
        desc = 'passes'
    elif move.is_resign:
        desc = 'resigns'
    else:
        desc = coords_from_point(move.point)
    print('{} {}'.format(player, desc))


def print_board(board):
    for row in range(board.rows, 0, -1):
        offset = ' ' if row <= 9 else ''

        line = []
        for col in range(1, board.cols + 1):
            player = board.get_owner(Point(row, col))
            line.append(player_chars[player])

        print('{}{} {}'.format(offset, row, ''.join(line)))

    print('    ', end='')
    for col in range(1, board.cols + 1):
        print(int_to_char(col) + '  ', end='')
    print('')


def point_from_coords(coords):
    col = char_to_int(coords[0])
    row = int(coords[1:])
    return Point(row, col)


def coords_from_point(point):
    return '{}{}'.format(int_to_char(point.col), point.row)
