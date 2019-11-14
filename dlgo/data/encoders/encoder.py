import numpy as np

from dlgo.go import Point, Move


class Encoder:
    def __init__(self, board_size):
        self.board_size = board_size

    def encode_board(self, game_state):
        raise NotImplementedError()

    def encode_point(self, point):
        return self.board_size * (point.row - 1) + (point.col - 1)

    def encode_move(self, move):
        assert move.is_play

        move_vector = np.zeros(self.move_shape)
        move_vector[self.encode_point(move.point)] = 1
        return move_vector

    def decode_point(self, index):
        return Point(index // self.board_size + 1, index % self.board_size + 1)

    def decode_move(self, encoded):
        return Move.play(self.decode_point(encoded.argmax()))

    @property
    def board_shape(self):
        raise NotImplementedError()

    @property
    def move_shape(self):
        return self.board_size ** 2
