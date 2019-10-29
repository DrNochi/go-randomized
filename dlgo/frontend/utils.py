from dlgo.gotypes import Point

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
