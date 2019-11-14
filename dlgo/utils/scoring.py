from dlgo.go import Point, Player, Score


def stone_difference(game):
    black = 0
    white = 0

    for r in range(1, game.board.size + 1):
        for c in range(1, game.board.size + 1):
            p = Point(r, c)
            color = game.board.get_color(p)
            if color is Player.black:
                black += 1
            elif color is Player.white:
                white += 1

    diff = black - white
    return diff if game.next_player is Player.black else -diff


def area_difference(game):
    score = Score.compute(game)
    return score.winning_margin if score.winner is game.next_player else -score.winning_margin
