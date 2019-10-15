import numpy as np

from dlgo.encoders.base import Encoder
from dlgo.gotypes import Point, Move


class OnePlaneEncoder(Encoder):
    def encode_board(self, game):
        assert game.board.rows == self.rows and game.board.cols == self.cols

        board_matrix = np.zeros(self.board_shape)

        for r in range(self.rows):
            for c in range(self.cols):
                string = game.board[Point(r + 1, c + 1)]

                if string is not None:
                    board_matrix[r, c] = 1 if string.owner == game.next_player else -1

        return board_matrix

    def encode_move(self, move):
        assert move.is_play
        move_vector = np.zeros(self.move_shape)
        move_vector[(move.point.row - 1) * self.cols + move.point.col - 1] = 1
        return move_vector

    def decode_move(self, encoded):
        index = np.argmax(encoded)
        return Move.play(Point((index // self.cols) + 1, (index % self.cols) + 1))
