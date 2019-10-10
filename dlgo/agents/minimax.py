import random

from dlgo.agents.base import Agent
from dlgo.gotypes import Player, Point
from dlgo.scoring import Score

MAX_SCORE = (1 << 15) - 1


def capture_difference(game):
    black = 0
    white = 0

    for r in range(1, game.board.rows + 1):
        for c in range(1, game.board.cols + 1):
            p = Point(r, c)
            color = game.board.get_owner(p)
            if color == Player.black:
                black += 1
            elif color == Player.white:
                white += 1

    diff = black - white
    return diff if game.next_player == Player.black else -diff


def area_difference(game):
    score = Score.compute(game)
    return score.winning_margin if score.winner == game.next_player else -score.winning_margin


class MinimaxAgent(Agent):
    def __init__(self, depth, heuristic=capture_difference):
        self.search_depth = depth
        self.position_evaluation_function = heuristic

    def select_move(self, game):
        best_moves = []
        best_score = -MAX_SCORE

        black = -MAX_SCORE
        white = -MAX_SCORE

        for possible_move in game.possible_moves():
            next_state = game.apply_move(possible_move)
            result = -self.best_result(next_state, 0, black, white)

            if result > best_score:
                best_moves = [possible_move]
                best_score = result

                if game.next_player == Player.black:
                    black = best_score
                elif game.next_player == Player.white:
                    white = best_score
            elif result == best_score:
                best_moves.append(possible_move)

        return random.choice(best_moves)

    def best_result(self, game, depth, black, white):
        if game.is_over():
            return MAX_SCORE if game.winner == game.next_player else -MAX_SCORE

        if depth == self.search_depth:
            return self.position_evaluation_function(game)

        best = -MAX_SCORE
        for possible_move in game.possible_moves():
            next_state = game.apply_move(possible_move)
            result = -self.best_result(next_state, depth + 1, black, white)

            if result > best:
                best = result

            if game.next_player == Player.white:
                if -best < black:
                    return best
                if best > white:
                    white = best
            elif game.next_player == Player.black:
                if -best < white:
                    return best
                if best > black:
                    black = best

        return best
