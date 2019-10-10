from copy import deepcopy

from dlgo.gotypes import Point, Move
from dlgo.scoring import Score


class GoString:
    def __init__(self, owner, stones, liberties):
        self.owner = owner
        self.stones = stones
        self.liberties = liberties

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return (isinstance(other, GoString) and
                self.owner == other.owner and
                self.stones == other.stones and
                self.liberties == other.liberties)


class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self._grid = {}

    def place_stone(self, player, point):
        raise NotImplementedError()

    def is_on_board(self, point):
        return (1 <= point.row <= self.rows and
                1 <= point.col <= self.cols)

    def get_owner(self, point):
        return self[point].owner if self[point] is not None else None

    def __getitem__(self, point):
        assert isinstance(point, Point)
        return self._grid.get(point)

    def __setitem__(self, point, string):
        assert isinstance(point, Point)
        assert string is None or isinstance(string, GoString)
        self._grid[point] = string

    def __eq__(self, other):
        return (isinstance(other, Board) and
                self.rows == other.rows and
                self.cols == other.cols and
                self._grid == other._grid)


class GameState:
    def __init__(self, board, next_player, prev_state, move, komi):
        self.board = board
        self.next_player = next_player
        self.prev_state = prev_state
        self.last_move = move
        self.komi = komi

    @staticmethod
    def new_game(board_size, komi):
        raise NotImplementedError()

    def apply_move(self, move):
        if move.is_play:
            board = deepcopy(self.board)
            board.place_stone(self.next_player, move.point)
        else:
            board = self.board

        return self.__class__(board, self.next_player.other, self, move, self.komi)

    def is_suicide(self, player, move):
        raise NotImplementedError()

    # @property
    # def situation(self):
    #     return (self.next_player, self.board)

    def is_ko(self, player, move):
        raise NotImplementedError()

    def is_valid(self, move):
        return not self.is_over() and (
            move.is_pass or move.is_resign or (self.board[move.point] is None and
                                               not self.is_suicide(self.next_player, move) and
                                               not self.is_ko(self.next_player, move)))

    def is_over(self):
        if self.last_move is None:
            return False
        elif self.last_move.is_resign:
            return True

        return (self.prev_state.last_move.is_pass
                if self.last_move.is_pass and self.prev_state.last_move is not None
                else False)

    def possible_moves(self):
        if self.is_over():
            return []

        moves = [Move.pass_turn(), Move.resign()]
        for row in range(1, self.board.rows + 1):
            for col in range(1, self.board.cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid(move):
                    moves.append(move)

        return moves

    @property
    def winner(self):
        assert self.is_over()
        return self.winner_with_score(Score.compute(self))

    def winner_with_score(self, score):
        assert self.is_over()
        return self.next_player if self.last_move.is_resign else score.winner
