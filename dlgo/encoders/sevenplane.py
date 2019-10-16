import numpy as np

from dlgo.encoders.base import OneHotMoveEncoder
from dlgo.gotypes import Point, Move


class SevenPlaneEncoder(OneHotMoveEncoder):
    def encode_board(self, game):
        assert game.board.rows == self.rows and game.board.cols == self.cols

        board_matrix = np.zeros(self.board_shape)

        for r in range(self.rows):
            for c in range(self.cols):
                point = Point(r + 1, c + 1)
                string = game.board[point]

                if string is not None:
                    plane = min(string.num_liberties, 3) - 1
                    if string.owner != game.next_player:
                        plane += 3
                    board_matrix[r, c, plane] = 1
                elif game.is_ko(game.next_player, Move.play(point)):
                    board_matrix[r, c, 6] = 1

        return board_matrix

    @property
    def board_shape(self):
        return self.rows, self.cols, 7
