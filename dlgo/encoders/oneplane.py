import numpy as np

from dlgo.encoders.base import OneHotMoveEncoder
from dlgo.gotypes import Point


class OnePlaneEncoder(OneHotMoveEncoder):
    def encode_board(self, game):
        assert game.board.rows == self.rows and game.board.cols == self.cols

        board_matrix = np.zeros(self.board_shape)

        for r in range(self.rows):
            for c in range(self.cols):
                string = game.board[Point(r + 1, c + 1)]

                if string is not None:
                    board_matrix[r, c] = 1 if string.owner == game.next_player else -1

        return board_matrix

    @property
    def board_shape(self):
        return self.rows, self.cols
