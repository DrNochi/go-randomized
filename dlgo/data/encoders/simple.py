import numpy as np

from dlgo.go import Player, Move, Point
from .encoder import Encoder

"""
0 - 3. black stones with 1, 2, 3, 4+ liberties
4 - 7. white stones with 1, 2, 3, 4+ liberties
8. black plays next
9. white plays next
10. move would be illegal due to ko
"""


class SimpleEncoder(Encoder):
    def encode_board(self, game_state):
        encoded = np.zeros(self.board_shape)

        if game_state.next_player is Player.black:
            encoded[8] = 1
        else:
            encoded[9] = 1

        for r in range(self.board_size):
            for c in range(self.board_size):
                p = Point(r + 1, c + 1)
                group = game_state.board[p]

                if group is None:
                    if game_state.does_move_violate_ko(game_state.next_player, Move.play(p)):
                        encoded[10][r][c] = 1
                else:
                    plane = min(4, group.liberty_count) - 1
                    if group.color is Player.white:
                        plane += 4
                    encoded[plane][r][c] = 1

        return encoded

    @property
    def board_shape(self):
        return 11, self.board_size, self.board_size
