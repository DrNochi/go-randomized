import unittest

from dlgo.go import Board, Player, Point, GameState
from dlgo.utils import is_ladder_capture, is_ladder_escape


class LadderTest(unittest.TestCase):
    def test_ladder_capture(self):
        board = Board(19)
        board.place_stone(Player.black, Point(13, 13))
        board.place_stone(Player.black, Point(14, 13))
        board.place_stone(Player.black, Point(14, 14))
        board.place_stone(Player.black, Point(15, 14))
        board.place_stone(Player.black, Point(15, 15))
        board.place_stone(Player.white, Point(12, 13))
        board.place_stone(Player.white, Point(13, 12))
        board.place_stone(Player.white, Point(14, 12))
        board.place_stone(Player.white, Point(13, 14))
        board.place_stone(Player.white, Point(15, 13))
        board.place_stone(Player.white, Point(14, 15))
        board.place_stone(Player.white, Point(16, 14))

        game = GameState(board, Player.white, None, None, 7.5)
        self.assertTrue(is_ladder_capture(game, Point(15, 16)))
        self.assertFalse(is_ladder_capture(game, Point(16, 15)))

        board.place_stone(Player.white, Point(15, 16))

        game = GameState(board, Player.white, None, None, 7.5)
        self.assertTrue(is_ladder_capture(game, Point(16, 15)))

    def test_ladder_escape(self):
        board = Board(19)
        board.place_stone(Player.black, Point(13, 13))
        board.place_stone(Player.black, Point(14, 13))
        board.place_stone(Player.black, Point(14, 14))
        board.place_stone(Player.black, Point(15, 14))
        board.place_stone(Player.black, Point(15, 15))
        board.place_stone(Player.white, Point(12, 13))
        board.place_stone(Player.white, Point(13, 12))
        board.place_stone(Player.white, Point(14, 12))
        board.place_stone(Player.white, Point(13, 14))
        board.place_stone(Player.white, Point(15, 13))
        board.place_stone(Player.white, Point(14, 15))
        board.place_stone(Player.white, Point(16, 14))

        game = GameState(board, Player.black, None, None, 7.5)
        self.assertTrue(is_ladder_escape(game, Point(15, 16)))
        self.assertTrue(is_ladder_escape(game, Point(16, 15)))

        board.place_stone(Player.white, Point(15, 16))

        game = GameState(board, Player.black, None, None, 7.5)
        self.assertFalse(is_ladder_escape(game, Point(16, 15)))

        board.place_stone(Player.black, Point(18, 16))

        game = GameState(board, Player.black, None, None, 7.5)
        self.assertTrue(is_ladder_escape(game, Point(16, 15)))


if __name__ == '__main__':
    unittest.main()
