from collections import namedtuple
from enum import Enum


class Player(Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]

    def corners(self):
        return [
            Point(self.row - 1, self.col - 1),
            Point(self.row - 1, self.col + 1),
            Point(self.row + 1, self.col - 1),
            Point(self.row + 1, self.col + 1),
        ]


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
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

    # @property
    # def tuple(self):
    #     return self.is_play, self.is_pass, self.is_resign, self.point
    #
    # def __hash__(self):
    #     return hash(self.tuple)
    #
    # def __eq__(self, other):
    #     return isinstance(other, Move) and self.tuple == other.tuple
