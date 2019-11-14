import sys
import unittest

import numpy as np

from dlgo.data.encoders import get_encoder, AlphaGoEncoder
from dlgo.go import GameState, Move, Point


class AlphaGoEncoderTest(unittest.TestCase):
    def test_encoder(self):
        alphago = get_encoder('alphago', 19)

        game = GameState.new_game(19, 7.5)
        game = game.apply_move(Move.play(Point(16, 16)))
        encoded = alphago.encode_board(game)

        np.set_printoptions(threshold=sys.maxsize)
        print(encoded)

        self.assertEqual(type(alphago), AlphaGoEncoder)
        self.assertEqual(alphago.board_size, 19)
        self.assertEqual(alphago.num_planes, 49)
        self.assertEqual(alphago.board_shape, (49, 19, 19))
        self.assertEqual(alphago.board_shape, encoded.shape)


if __name__ == '__main__':
    unittest.main()
