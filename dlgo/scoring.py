from collections import namedtuple
from dlgo.gotypes import Player, Point


class Territory:
    def __init__(self, owners):
        self.black = 0
        self.white = 0

        for owner in owners.values():
            if owner == Player.black:
                self.black += 1
            elif owner == Player.white:
                self.white += 1

    @classmethod
    def evaluate(cls, board):
        owners = {}
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 1):
                pos = Point(r, c)

                if pos in owners:
                    continue

                owner = board.get_owner(pos)
                if owner is not None:
                    owners[pos] = owner
                else:
                    points, region_owners = cls._collect_region(pos, board)

                    if len(region_owners) == 1:
                        region_owner = region_owners.pop()
                    else:
                        region_owner = None

                    for point in points:
                        owners[point] = region_owner

        return Territory(owners)

    @classmethod
    def _collect_region(cls, pos, board, visited=None):
        if visited is None:
            visited = set()

        if pos in visited:
            return [], set()
        visited.add(pos)

        points = [pos]
        owners = set()

        for neighbor in pos.neighbors():
            if not board.is_on_board(neighbor):
                continue

            adj_owner = board.get_owner(neighbor)
            if adj_owner is None:
                adj_points, adj_owners = cls._collect_region(neighbor, board, visited)
                points += adj_points
                owners |= adj_owners
            else:
                owners.add(adj_owner)

        return points, owners


class GameResult(namedtuple('GameResult', 'black white komi')):
    def winner(self):
        return Player.black if self.black > self.white + self.komi else Player.black

    def winning_margin(self):
        return abs(self.black - self.white - self.komi)

    @staticmethod
    def compute(game, komi):
        territory = Territory.evaluate(game.board)
        return GameResult(territory.black, territory.white, komi)
