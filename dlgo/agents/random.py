import numpy as np

from dlgo.go import Move, Point
from .agent import Agent
from dlgo.utils import is_sensible_move


class RandomAgent(Agent):
    def __init__(self):
        self._move_cache = None

    def _init_move_cache(self, dim):
        self._move_cache = [Move.play(Point(r, c)) for r in range(1, dim + 1) for c in range(1, dim + 1)]
        self._move_cache.append(Move.pass_turn())
        self._move_cache.append(Move.resign())

    def _shuffle_moves(self, game):
        if self._move_cache is None:
            self._init_move_cache(game.board.size)

        indices = np.arange(len(self._move_cache))
        np.random.shuffle(indices)
        return indices

    def select_move(self, game):
        indices = self._shuffle_moves(game)

        for i in indices:
            candidate = self._move_cache[i]
            if game.is_valid_move(candidate):
                return candidate

        assert False


class ConstrainedRandomAgent(RandomAgent):
    def __init__(self, constraint=is_sensible_move):
        super().__init__()
        self.constraint = constraint

    def select_move(self, game):
        indices = self._shuffle_moves(game)

        for i in indices:
            candidate = self._move_cache[i]
            if game.is_valid_move(candidate) and self.constraint(game, candidate):
                return candidate

        return Move.pass_turn()
