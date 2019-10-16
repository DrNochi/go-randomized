import numpy as np

from dlgo.gotypes import Move, Point


class Encoder:
    def encode_board(self, game):
        raise NotImplementedError()

    def encode_move(self, move):
        raise NotImplementedError()

    def decode_move(self, encoded):
        raise NotImplementedError()

    @property
    def board_shape(self):
        raise NotImplementedError()

    @property
    def move_shape(self):
        raise NotImplementedError()


class OneHotMoveEncoder(Encoder):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def encode_move(self, move):
        assert move.is_play
        move_vector = np.zeros(self.move_shape)
        move_vector[(move.point.row - 1) * self.cols + move.point.col - 1] = 1
        return move_vector

    def decode_move(self, encoded):
        index = np.argmax(encoded)
        return Move.play(Point((index // self.cols) + 1, (index % self.cols) + 1))

    @property
    def move_shape(self):
        return self.rows * self.cols,

    def encode_board(self, game):
        raise NotImplementedError()

    @property
    def board_shape(self):
        raise NotImplementedError()
