import random

from dlgo.agents.base import Agent
from dlgo.gotypes import Move


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


class RandomAgent(Agent):
    def select_move(self, game):
        candidates = [candidate for candidate in game.possible_moves()
                      if candidate.is_play and not is_point_an_eye(game.board, candidate.point, game.next_player)]
        return random.choice(candidates) if candidates else Move.pass_turn()
