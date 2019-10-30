from dlgo.gotypes import Point, Player

player_chars = {
    None: ' . ',
    Player.black: ' x ',
    Player.white: ' o ',
}

column_chars = 'ABCDEFGHJKLMNOPQRSTUVWXZY'


def int_to_char(n):
    return column_chars[n - 1]


def char_to_int(c):
    return column_chars.index(c.upper()) + 1


def point_from_coords(coords):
    col = char_to_int(coords[0])
    row = int(coords[1:])
    return Point(row, col)


def coords_from_point(point):
    return '{}{}'.format(int_to_char(point.col), point.row)


def format_board(board):
    result = ''
    for row in range(board.rows, 0, -1):
        offset = ' ' if row <= 9 else ''

        line = []
        for col in range(1, board.cols + 1):
            player = board.get_owner(Point(row, col))
            line.append(player_chars[player])

        result += '{}{} {}\n'.format(offset, row, ''.join(line))

    result += '    '
    for col in range(1, board.cols + 1):
        result += int_to_char(col) + '  '

    return result
