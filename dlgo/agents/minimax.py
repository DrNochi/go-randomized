import random
import sys

from dlgo.go import Player
from dlgo.utils import stone_difference
from .agent import Agent

max_score = sys.maxsize


class MinimaxAgent(Agent):
    def __init__(self, depth, heuristic=stone_difference):
        self.search_depth = depth
        self.position_evaluation_function = heuristic

    def select_move(self, game):
        best_moves = []
        best_score = -max_score

        black = -max_score
        white = -max_score

        for possible_move in game.possible_moves:
            next_state = game.apply_move(possible_move)
            result = -self._best_result(next_state, 0, black, white)

            if result > best_score:
                best_moves = [possible_move]
                best_score = result

                if game.next_player is Player.black:
                    black = best_score
                elif game.next_player is Player.white:
                    white = best_score
            elif result == best_score:
                best_moves.append(possible_move)

        return random.choice(best_moves)

    def _best_result(self, game, depth, black, white):
        if game.is_over:
            return max_score if game.winner is game.next_player else -max_score

        if depth == self.search_depth:
            return self.position_evaluation_function(game)

        best = -max_score
        for possible_move in game.possible_moves:
            next_state = game.apply_move(possible_move)
            result = -self._best_result(next_state, depth + 1, black, white)

            if result > best:
                best = result

            if game.next_player is Player.white:
                if -best < black:
                    return best
                if best > white:
                    white = best
            elif game.next_player is Player.black:
                if -best < white:
                    return best
                if best > black:
                    black = best

        return best
