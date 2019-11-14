import numpy as np

from dlgo.go import Point
from .encoder import Encoder


class OnePlaneEncoder(Encoder):
    def encode_board(self, game_state):
        encoded = np.zeros(self.board_shape)

        next_player = game_state.next_player

        for r in range(self.board_size):
            for c in range(self.board_size):
                p = Point(r + 1, c + 1)
                group = game_state.board[p]

                if group is None:
                    continue
                elif group.color is next_player:
                    encoded[0, r, c] = 1
                else:
                    encoded[0, r, c] = -1

        return encoded

    @property
    def board_shape(self):
        return 1, self.board_size, self.board_size
