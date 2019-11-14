import unittest

from dlgo.go import Board, Player, Point, Territory


class ScoringTest(unittest.TestCase):
    def test_scoring(self):
        board = Board(5)
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(1, 4))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.black, Point(2, 4))
        board.place_stone(Player.black, Point(2, 5))
        board.place_stone(Player.black, Point(3, 1))
        board.place_stone(Player.black, Point(3, 2))
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(3, 4))
        board.place_stone(Player.white, Point(3, 5))
        board.place_stone(Player.white, Point(4, 1))
        board.place_stone(Player.white, Point(4, 2))
        board.place_stone(Player.white, Point(4, 3))
        board.place_stone(Player.white, Point(4, 4))
        board.place_stone(Player.white, Point(5, 2))
        board.place_stone(Player.white, Point(5, 4))
        board.place_stone(Player.white, Point(5, 5))

        territory = Territory.evaluate(board)
        self.assertEqual(9, territory.black_stones)
        self.assertEqual(4, territory.black_territory)
        self.assertEqual(9, territory.white_stones)
        self.assertEqual(3, territory.white_territory)
        self.assertEqual(0, territory.dame)


if __name__ == '__main__':
    unittest.main()
