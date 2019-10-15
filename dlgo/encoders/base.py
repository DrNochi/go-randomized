class Encoder:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def encode_board(self, game):
        raise NotImplementedError()

    def encode_move(self, move):
        raise NotImplementedError()

    def decode_move(self, encoded):
        raise NotImplementedError()

    @property
    def board_shape(self):
        return self.rows, self.cols

    @property
    def move_shape(self):
        return self.rows * self.cols,
