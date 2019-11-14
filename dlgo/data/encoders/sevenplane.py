import numpy as np

from dlgo.go import Point, Move
from .encoder import Encoder


class SevenPlaneEncoder(Encoder):
    def encode_board(self, game_state):
        encoded = np.zeros(self.board_shape)

        base_plane = {game_state.next_player: 0,
                      game_state.next_player.other: 3}

        for r in range(self.board_size):
            for c in range(self.board_size):
                p = Point(r + 1, c + 1)
                group = game_state.board[p]

                if group is None:
                    if game_state.does_move_violate_ko(game_state.next_player, Move.play(p)):
                        encoded[6][r][c] = 1
                else:
                    plane = base_plane[group.color] + min(3, group.liberty_count) - 1
                    encoded[plane][r][c] = 1

        return encoded

    @property
    def board_shape(self):
        return 7, self.board_size, self.board_size
