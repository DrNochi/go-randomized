from copy import deepcopy

from dlgo.boards.base import GoString, Board, GameState
from dlgo.gotypes import Player


class MutableGoString(GoString):
    def __init__(self, owner, stones, liberties):
        super().__init__(owner, set(stones), set(liberties))

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, string):
        assert string.owner == self.owner
        common_stones = self.stones | string.stones
        return MutableGoString(self.owner, common_stones, self.liberties | string.liberties - common_stones)


class NaiveBoard(Board):
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

        string = MutableGoString(player, [point], liberties)

        for own_string in adj_own_strings:
            string = string.merged_with(own_string)

        for own_point in string.stones:
            self[own_point] = string

        for opponent_string in adj_opponent_strings:
            opponent_string.remove_liberty(point)
            if opponent_string.num_liberties == 0:
                self._capture_string(opponent_string)

    def _capture_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                adj_string = self[neighbor]
                if adj_string is not None and adj_string is not string:
                    adj_string.add_liberty(point)

            self[point] = None


class SlowGameState(GameState):
    @staticmethod
    def new_game(board_size, komi):
        assert isinstance(board_size, int)
        return SlowGameState(NaiveBoard(board_size, board_size), Player.black, None, None, komi)

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

        prev_state = self.prev_state
        while prev_state is not None:
            if prev_state.board == board:
                return True

            prev_state = prev_state.prev_state

        return False
