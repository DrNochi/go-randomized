import numpy as np

from dlgo.gotypes import Move, Point


class Encoder:
    def encode_board(self, game):
        raise NotImplementedError()

    def encode_move(self, move):
        raise NotImplementedError()

    def decode_move(self, encoded):
        raise NotImplementedError()

    def decode_moves(self, encoded):
        raise NotImplementedError()

    def sample_moves(self, encoded):
        raise NotImplementedError()

    def get_move(self, internal):
        raise NotImplementedError()

    def can_encode_move(self, move):
        return move.is_play or (move.is_pass and self.can_encode_pass) or (move.is_resign and self.can_encode_resign)

    @property
    def board_shape(self):
        raise NotImplementedError()

    @property
    def move_shape(self):
        raise NotImplementedError()

    @property
    def can_encode_pass(self):
        raise NotImplementedError()

    @property
    def can_encode_resign(self):
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
        return self.get_move(encoded.argmax())

    def decode_moves(self, encoded):
        return np.argsort(encoded)[::-1]

    def sample_moves(self, encoded):
        return np.random.choice(np.arange(len(encoded)), len(encoded), replace=False, p=encoded)

    def get_move(self, index):
        return Move.play(Point((index // self.cols) + 1, (index % self.cols) + 1))

    @property
    def move_shape(self):
        return self.rows * self.cols,

    @property
    def can_encode_pass(self):
        return False

    @property
    def can_encode_resign(self):
        return False

    def encode_board(self, game):
        raise NotImplementedError()

    @property
    def board_shape(self):
        raise NotImplementedError()
