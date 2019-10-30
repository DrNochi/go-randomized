from dlgo.frontend.utils import coords_from_point, format_board


def print_move(player, move):
    if move.is_pass:
        desc = 'passes'
    elif move.is_resign:
        desc = 'resigns'
    else:
        desc = coords_from_point(move.point)
    print('{} {}'.format(player, desc))


def print_board(board):
    print(format_board(board))
