import unittest

from dlgo.go import Board, Player, Point, GameState, Move


class BoardTest(unittest.TestCase):
    def test_capture(self):
        board = Board(19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(1, 2))

        self.assertIs(Player.black, board.get_color(Point(2, 2)))

        board.place_stone(Player.white, Point(2, 1))

        self.assertIs(Player.black, board.get_color(Point(2, 2)))

        board.place_stone(Player.white, Point(2, 3))

        self.assertIs(Player.black, board.get_color(Point(2, 2)))

        board.place_stone(Player.white, Point(3, 2))

        self.assertIsNone(board.get_color(Point(2, 2)))

    def test_capture_two_stones(self):
        board = Board(19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(1, 3))

        self.assertIs(Player.black, board.get_color(Point(2, 2)))
        self.assertIs(Player.black, board.get_color(Point(2, 3)))

        board.place_stone(Player.white, Point(3, 2))
        board.place_stone(Player.white, Point(3, 3))

        self.assertIs(Player.black, board.get_color(Point(2, 2)))
        self.assertIs(Player.black, board.get_color(Point(2, 3)))

        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 4))

        self.assertIsNone(board.get_color(Point(2, 2)))
        self.assertIsNone(board.get_color(Point(2, 3)))

    def test_capture_is_not_suicide(self):
        board = Board(19)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(1, 3))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(1, 2))

        self.assertIsNone(board.get_color(Point(1, 1)))
        self.assertIs(Player.white, board.get_color(Point(2, 1)))
        self.assertIs(Player.white, board.get_color(Point(1, 2)))

    def test_remove_liberties(self):
        board = Board(5)
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(2, 2))

        white_group = board[Point(2, 2)]
        self.assertCountEqual(white_group.liberties, [Point(2, 3), Point(2, 1), Point(1, 2), Point(3, 2)])

        board.place_stone(Player.black, Point(3, 2))

        white_group = board[Point(2, 2)]
        self.assertCountEqual(white_group.liberties, [Point(2, 3), Point(2, 1), Point(1, 2)])

    def test_empty_triangle(self):
        board = Board(5)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(2, 1))

        black_string = board[Point(1, 1)]
        self.assertCountEqual(black_string.liberties, [Point(3, 2), Point(2, 3), Point(1, 3)])

    def test_self_capture(self):
        board = Board(5)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(1, 3))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 2))
        board.place_stone(Player.white, Point(2, 3))
        board.place_stone(Player.white, Point(1, 4))

        self.assertTrue(board.is_self_capture(Player.black, Point(1, 2)))

    def test_not_self_capture(self):
        board = Board(5)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(1, 3))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 3))
        board.place_stone(Player.white, Point(1, 4))

        self.assertFalse(board.is_self_capture(Player.black, Point(1, 2)))

    def test_not_self_capture_is_other_capture(self):
        board = Board(5)
        board.place_stone(Player.black, Point(3, 1))
        board.place_stone(Player.black, Point(3, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 2))
        board.place_stone(Player.white, Point(1, 3))

        self.assertFalse(board.is_self_capture(Player.black, Point(1, 2)))


class GameTest(unittest.TestCase):
    def test_new_game(self):
        before_move = GameState.new_game(19, 7.5)
        after_move = before_move.apply_move(Move.play(Point(16, 16)))

        self.assertEqual(before_move, after_move.previous_state)
        self.assertIs(Player.white, after_move.next_player)
        self.assertIs(Player.black, after_move.board.get_color(Point(16, 16)))


if __name__ == '__main__':
    unittest.main()
