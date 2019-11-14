from collections import namedtuple
from enum import Enum


class Player(Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self is Player.white else Player.white


class Point(namedtuple('Point', ('row', 'col'))):
    @property
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]

    @property
    def corners(self):
        return [
            Point(self.row - 1, self.col - 1),
            Point(self.row - 1, self.col + 1),
            Point(self.row + 1, self.col - 1),
            Point(self.row + 1, self.col + 1),
        ]

    def __deepcopy__(self, memo):
        return self


class Group(namedtuple('Group', ('color', 'stones', 'liberties'))):
    def without_liberty(self, point):
        return Group(self.color, self.stones, self.liberties - {point})

    def with_liberty(self, point):
        return Group(self.color, self.stones, self.liberties | {point})

    def merged_with(self, string):
        assert string.color is self.color

        combined_stones = self.stones | string.stones
        return Group(self.color, combined_stones, (self.liberties | string.liberties) - combined_stones)

    @property
    def liberty_count(self):
        return len(self.liberties)

    def __deepcopy__(self, memo):
        return self


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign

        self.point = point
        self.is_play = self.point is not None
        self.is_pass = is_pass
        self.is_resign = is_resign

    @staticmethod
    def play(point):
        return Move(point=point)

    @staticmethod
    def pass_turn():
        return Move(is_pass=True)

    @staticmethod
    def resign():
        return Move(is_resign=True)

    # def __str__(self):
    #     if self.is_pass:
    #         return 'pass'
    #     if self.is_resign:
    #         return 'resign'
    #     return '(r %d, c %d)' % (self.point.row, self.point.col)
    #
    # def __hash__(self):
    #     return hash((
    #         self.is_play,
    #         self.is_pass,
    #         self.is_resign,
    #         self.point))
    #
    # def __eq__(self, other):
    #     return ((self.is_play, self.is_pass, self.is_resign, self.point)
    #             == (other.is_play, other.is_pass, other.is_resign, other.point))
