from dlgo.go import Point, Player

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
    return f'{int_to_char(point.col)}{point.row}'


def print_move(player, move):
    if move.is_pass:
        desc = 'passes'
    elif move.is_resign:
        desc = 'resigns'
    else:
        desc = coords_from_point(move.point)
    print(f'{player} {desc}')


def print_board(board):
    print(format_board(board))


def format_board(board):
    result = ''
    for row in range(board.size, 0, -1):
        offset = ' ' if row <= 9 else ''

        line = []
        for col in range(1, board.size + 1):
            player = board.get_color(Point(row, col))
            line.append(player_chars[player])

        result += f'{offset}{row} {"".join(line)}\n'

    result += '    '
    for col in range(1, board.size + 1):
        result += int_to_char(col) + '  '

    return result
