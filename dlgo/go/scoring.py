from collections import namedtuple

from .types import Player, Point


def _collect_region(point, board, visited=None):
    visited = visited or set()
    if point in visited:
        return [], set()
    visited.add(point)

    all_points = [point]
    all_borders = set()

    for neighbor in board.neighbors(point):
        neighbor_color = board.get_color(neighbor)
        if neighbor_color is None:
            points, borders = _collect_region(neighbor, board, visited)
            all_points += points
            all_borders |= borders
        else:
            all_borders.add(neighbor_color)

    return all_points, all_borders


class Territory:
    def __init__(self, territory_grid):
        self.black_territory = 0
        self.white_territory = 0
        self.black_stones = 0
        self.white_stones = 0
        self.dame = 0

        for point, status in territory_grid.items():
            if status is Player.black:
                self.black_stones += 1
            elif status is Player.white:
                self.white_stones += 1
            elif status == 'b':
                self.black_territory += 1
            elif status == 'w':
                self.white_territory += 1
            elif status == 'd':
                self.dame += 1

    @staticmethod
    def evaluate(board):
        territory_status = {}
        for r in range(1, board.size + 1):
            for c in range(1, board.size + 1):
                point = Point(r, c)
                if point in territory_status:
                    continue

                owner = board.get_color(point)

                if owner is None:
                    region, borders = _collect_region(point, board)
                    owner = ('b' if borders.pop() is Player.black else 'w') if len(borders) == 1 else 'd'
                    for pos in region:
                        territory_status[pos] = owner
                else:
                    territory_status[point] = owner

        return Territory(territory_status)


class Score(namedtuple('GameResult', 'black white komi')):
    @staticmethod
    def compute(game_state):
        territory = Territory.evaluate(game_state.board)
        return Score(
            territory.black_territory + territory.black_stones,
            territory.white_territory + territory.white_stones,
            game_state.komi)

    @property
    def winner(self):
        if self.black > self.white + self.komi:
            return Player.black
        return Player.white

    @property
    def winning_margin(self):
        return abs(self.black - self.white - self.komi)

    # def __str__(self):
    #     w = self.white + self.komi
    #     if self.black > w:
    #         return 'B+%.1f' % (self.black - w,)
    #     return 'W+%.1f' % (w - self.black,)
