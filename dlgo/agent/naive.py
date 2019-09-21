import random
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point


class RandomBot(Agent):
    def select_move(self, game):
        candidates = []

        for row in range(1, game.board.rows + 1):
            for col in range(1, game.board.cols + 1):
                candidate = Point(row, col)

                if (game.is_valid(Move.play(candidate)) and
                        not is_point_an_eye(game.board, candidate, game.next_player)):
                    candidates.append(candidate)

        return Move.play(random.choice(candidates)) if candidates else Move.pass_turn()
