from dlgo.go import Point


def is_point_an_eye(board, point, color):
    if board.get_color(point) is not None:
        return False

    for neighbor in board.neighbors(point):
        neighbor_color = board.get_color(neighbor)
        if neighbor_color is not color:
            return False

    own_corners = 0
    off_board_corners = 0

    for corner in point.corners:
        if board.is_on_grid(corner):
            corner_color = board.get_color(corner)
            if corner_color is color:
                own_corners += 1
        else:
            off_board_corners += 1
    if off_board_corners > 0:
        return off_board_corners + own_corners == 4
    return own_corners >= 3


def is_sensible_move(game, move):
    return move.is_play and not is_point_an_eye(game.board, move.point, game.next_player)


def fixed_handicap_positions(board_size, handicap):
    assert 7 <= board_size <= 25
    assert handicap <= 9 if board_size % 2 == 1 else handicap <= 4

    edge_distance = 3 if board_size < 13 else 4

    low = edge_distance
    high = board_size - edge_distance + 1
    mid = board_size // 2 + 1

    positions = [
        Point(low, low),
        Point(high, high),
        Point(high, low),
        Point(low, high),
        Point(mid, low),
        Point(mid, high),
        Point(low, mid),
        Point(high, low)
    ]

    if handicap <= 4:
        return positions[:handicap]
    elif handicap % 2 == 0:
        return positions[:handicap]
    else:
        return positions[:handicap] + [Point(mid, mid)]
