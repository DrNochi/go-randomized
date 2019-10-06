from copy import deepcopy, copy

from dlgo.boards.base import GoString, Board, GameState
from dlgo.boards.zobrist import HASH_CODE, HASH_CODE_EMPTY
from dlgo.gotypes import Player


class FrozenGoString(GoString):
    def __init__(self, owner, stones, liberties):
        super().__init__(owner, frozenset(stones), frozenset(liberties))

    def without_liberty(self, point):
        return FrozenGoString(self.owner, self.stones, self.liberties - frozenset([point]))

    def with_liberty(self, point):
        return FrozenGoString(self.owner, self.stones, self.liberties | frozenset([point]))

    def merged_with(self, string):
        assert string.owner == self.owner
        common_stones = self.stones | string.stones
        return FrozenGoString(self.owner, common_stones, self.liberties | string.liberties - common_stones)

    def __deepcopy__(self, memodict=None):
        return FrozenGoString(self.owner, self.stones, deepcopy(self.liberties))


class NormalBoard(Board):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)

        self._hash = HASH_CODE_EMPTY

    def place_stone(self, player, point):
        assert self.is_on_board(point)
        assert self[point] is None

        adj_own_strings = []
        adj_opponent_strings = []
        liberties = []

        for neighbor in point.neighbors():
            if not self.is_on_board(neighbor):
                continue

            adj_string = self[neighbor]

            if adj_string is None:
                liberties.append(neighbor)
            elif adj_string.owner == player:
                if adj_string not in adj_own_strings:
                    adj_own_strings.append(adj_string)
            else:
                if adj_string not in adj_opponent_strings:
                    adj_opponent_strings.append(adj_string)

        string = FrozenGoString(player, [point], liberties)

        for own_string in adj_own_strings:
            string = string.merged_with(own_string)

        for own_point in string.stones:
            self[own_point] = string

        self._hash ^= HASH_CODE[point, player]

        for opponent_string in adj_opponent_strings:
            replacement = opponent_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(opponent_string.without_liberty(point))
            else:
                self._capture_string(opponent_string)

    def _replace_string(self, string):
        for point in string.stones:
            self[point] = string

    def _capture_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                adj_string = self[neighbor]
                if adj_string is not None and adj_string is not string:
                    self._replace_string(adj_string.with_liberty(point))

            self[point] = None
            self._hash ^= HASH_CODE[point, string.owner]

    @property
    def hash(self):
        return self._hash

    def __eq__(self, other):
        return (isinstance(other, NormalBoard) and
                self.rows == other.rows and
                self.cols == other.cols and
                self._hash == other._hash)

    def __deepcopy__(self, memodict=None):
        copied = NormalBoard(self.rows, self.cols)
        copied._grid = copy(self._grid)
        copied._hash = self._hash
        return copied


class NormalGameState(GameState):
    def __init__(self, board, next_player, prev_state, move):
        super().__init__(board, next_player, prev_state, move)

        self.prev_states = prev_state.prev_states | frozenset(
            (prev_state.board.hash,)) if prev_state is not None else frozenset()

    @staticmethod
    def new_game(board_size):
        assert isinstance(board_size, int)
        return NormalGameState(NormalBoard(board_size, board_size), Player.black, None, None)

    def is_suicide(self, player, move):
        if not move.is_play:
            return False

        board = deepcopy(self.board)
        board.place_stone(player, move.point)

        return board[move.point].num_liberties == 0

    def is_ko(self, player, move):
        if not move.is_play:
            return False

        board = deepcopy(self.board)
        board.place_stone(player, move.point)

        return board.hash in self.prev_states
