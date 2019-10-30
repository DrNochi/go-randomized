from dlgo.gotypes import Point


def fixed_handicap(board_size, handicap):
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
