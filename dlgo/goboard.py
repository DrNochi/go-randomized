from copy import deepcopy, copy
from dlgo.gotypes import Player, Point
from dlgo.zobrist import HASH_CODE, HASH_CODE_EMPTY


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @staticmethod
    def play(point):
        return Move(point=point)

    @staticmethod
    def pass_turn():
        return Move(is_pass=True)

    @staticmethod
    def resign():
        return Move(is_resign=True)


class GoString:
    def __init__(self, owner, stones, liberties):
        self.owner = owner
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        return GoString(self.owner, self.stones, self.liberties - frozenset([point]))

    def with_liberty(self, point):
        return GoString(self.owner, self.stones, self.liberties | frozenset([point]))

    def merged_with(self, string):
        assert string.owner == self.owner
        common_stones = self.stones | string.stones
        return GoString(self.owner, common_stones, self.liberties | string.liberties - common_stones)

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

        string = GoString(player, [point], liberties)

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

    def is_on_board(self, point):
        return (1 <= point.row <= self.rows and
                1 <= point.col <= self.cols)

    def get_owner(self, point):
        return self[point].owner if self[point] is not None else None

    @property
    def hash(self):
        return self._hash

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
                self._hash == other._hash)

    def __deepcopy__(self, memodict={}):
        copied = Board(self.rows, self.cols)
        copied._grid = copy(self._grid)
        copied._hash = self._hash
        return copied


class GameState:
    def __init__(self, board, next_player, prev_state, move):
        self.board = board
        self.next_player = next_player
        self.prev_state = prev_state
        self.prev_states = prev_state.prev_states | frozenset(
            (prev_state.board.hash,)) if self.prev_state is not None else frozenset()
        self.last_move = move

    def apply_move(self, move):
        if move.is_play:
            board = deepcopy(self.board)
            board.place_stone(self.next_player, move.point)
        else:
            board = self.board

        return GameState(board, self.next_player.other, self, move)

    @staticmethod
    def new_game(board_size):
        assert isinstance(board_size, int)
        return GameState(Board(board_size, board_size), Player.black, None, None)

    def is_suicide(self, player, move):
        if not move.is_play:
            return False

        board = deepcopy(self.board)
        board.place_stone(player, move.point)

        return board[move.point].num_liberties == 0

    # @property
    # def situation(self):
    #     return (self.next_player, self.board)

    def is_ko(self, player, move):
        if not move.is_play:
            return False

        board = deepcopy(self.board)
        board.place_stone(player, move.point)

        return board.hash in self.prev_states

    def is_over(self):
        if self.last_move is None:
            return False
        elif self.last_move.is_resign:
            return True

        return self.prev_state.last_move.is_pass if self.last_move.is_pass and self.prev_state.last_move is not None else False

    def is_valid(self, move):
        return not self.is_over() and (
            move.is_pass or move.is_resign or (
                self.board[move.point] is None and
                not self.is_suicide(self.next_player, move) and
                not self.is_ko(self.next_player, move)))
