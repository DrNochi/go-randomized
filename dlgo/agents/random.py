import random

import numpy as np

from dlgo.agents.base import Agent
from dlgo.gotypes import Point, Move


def is_point_an_eye(board, point, player):
    if board[point] is not None:
        return False

    for neighbor in point.neighbors():
        if board.is_on_board(neighbor):
            adj_player = board.get_owner(neighbor)
            if adj_player != player:
                return False

    friendly_corners = 0
    off_board_corners = 0

    for corner in point.corners():
        if board.is_on_board(corner):
            corner_color = board.get_owner(corner)
            if corner_color == player:
                friendly_corners += 1
        else:
            off_board_corners += 1

    return friendly_corners >= 3 if off_board_corners == 0 else off_board_corners + friendly_corners == 4


def is_sensible_move(game, move):
    return move.is_play and not is_point_an_eye(game.board, move.point, game.next_player)


class RandomAgent(Agent):
    def select_move(self, game):
        return random.choice(game.possible_moves())


class ConstrainedRandomAgent(RandomAgent):
    def __init__(self, constraint=is_sensible_move):
        self.constraint = constraint

    def select_move(self, game):
        candidates = [candidate for candidate in game.possible_moves() if self.constraint(game, candidate)]
        return random.choice(candidates) if candidates else Move.pass_turn()


class FastRandomAgent(RandomAgent):
    def __init__(self):
        self._move_cache = None

    def _init_move_cache(self, rows, cols):
        self._move_cache = [Move.play(Point(r, c)) for r in range(1, rows + 1) for c in range(1, cols + 1)]
        self._move_cache.append(Move.pass_turn())
        self._move_cache.append(Move.resign())

    def select_move(self, game):
        if self._move_cache is None:
            self._init_move_cache(game.board.rows, game.board.cols)

        indices = np.arange(len(self._move_cache))
        np.random.shuffle(indices)

        for i in indices:
            candidate = self._move_cache[i]
            if game.is_valid(candidate):
                return candidate

        assert False


class FastConstrainedRandomAgent(FastRandomAgent, ConstrainedRandomAgent):
    def __init__(self, constraint=is_sensible_move):
        FastRandomAgent.__init__(self)
        ConstrainedRandomAgent.__init__(self, constraint)

    def select_move(self, game):
        if self._move_cache is None:
            self._init_move_cache(game.board.rows, game.board.cols)

        indices = np.arange(len(self._move_cache))
        np.random.shuffle(indices)

        for i in indices:
            candidate = self._move_cache[i]
            if game.is_valid(candidate) and self.constraint(game, candidate):
                return candidate

        return Move.pass_turn()
