import random

import numpy as np

from dlgo.agents.base import Agent
from dlgo.agents.utils import is_sensible_move
from dlgo.gotypes import Point, Move


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

    def _shuffle_moves(self, game):
        if self._move_cache is None:
            self._init_move_cache(game.board.rows, game.board.cols)

        indices = np.arange(len(self._move_cache))
        np.random.shuffle(indices)
        return indices

    def select_move(self, game):
        indices = self._shuffle_moves(game)

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
        indices = self._shuffle_moves(game)

        for i in indices:
            candidate = self._move_cache[i]
            if game.is_valid(candidate) and self.constraint(game, candidate):
                return candidate

        return Move.pass_turn()
