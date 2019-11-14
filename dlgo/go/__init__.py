import copy

from . import zobrist
from .scoring import Territory, Score
from .types import Point, Player, Group, Move

_neighbor_tables = {}
_corner_tables = {}


def _get_neighbor_table(dim):
    if dim not in _neighbor_tables:
        _neighbor_tables[dim] = {
            p: [n for n in p.neighbors if 1 <= n.row <= dim and 1 <= n.col <= dim]
            for p in (
                Point(r, c)
                for r in range(1, dim + 1)
                for c in range(1, dim + 1)
            )
        }
    return _neighbor_tables[dim]


def _get_corner_table(dim):
    if dim not in _corner_tables:
        _corner_tables[dim] = {
            p: [n for n in p.corners if 1 <= n.row <= dim and 1 <= n.col <= dim]
            for p in (
                Point(r, c)
                for r in range(1, dim + 1)
                for c in range(1, dim + 1)
            )
        }
    return _corner_tables[dim]


class Board:
    def __init__(self, size):
        self.size = size
        self._grid = {}
        self._hash = zobrist.empty_board

        self._neighbor_table = _get_neighbor_table(size)
        self._corner_table = _get_corner_table(size)

    def neighbors(self, point):
        return self._neighbor_table[point]

    def corners(self, point):
        return self._corner_table[point]

    def place_stone(self, player, point):
        assert self.is_on_grid(point) and self._grid.get(point) is None

        adjacent_own_groups = []
        adjacent_opponent_groups = []
        liberties = []

        for neighbor in self._neighbor_table[point]:
            neighbor_group = self._grid.get(neighbor)
            if neighbor_group is None:
                liberties.append(neighbor)
            elif neighbor_group.color is player:
                if neighbor_group not in adjacent_own_groups:
                    adjacent_own_groups.append(neighbor_group)
            else:
                if neighbor_group not in adjacent_opponent_groups:
                    adjacent_opponent_groups.append(neighbor_group)

        new_group = Group(player, frozenset((point,)), frozenset(liberties))
        for own_group in adjacent_own_groups:
            new_group = new_group.merged_with(own_group)
        self._replace_group(new_group)

        self._hash ^= zobrist.hashes[point, player]

        for opponent_group in adjacent_opponent_groups:
            new_group = opponent_group.without_liberty(point)
            if new_group.liberty_count:
                self._replace_group(new_group)
            else:
                self._remove_group(opponent_group)

    def _replace_group(self, new_group):
        for point in new_group.stones:
            self._grid[point] = new_group

    def _remove_group(self, group):
        for point in group.stones:
            for neighbor in self._neighbor_table[point]:
                neighbor_group = self._grid.get(neighbor)
                if neighbor_group is not None and neighbor_group is not group:
                    self._replace_group(neighbor_group.with_liberty(point))

            self._grid[point] = None
            self._hash ^= zobrist.hashes[point, group.color]

    def is_self_capture(self, player, point):
        adjacent_own_groups = []

        for neighbor in self._neighbor_table[point]:
            neighbor_group = self._grid.get(neighbor)
            if neighbor_group is None:
                return False
            elif neighbor_group.color is player:
                adjacent_own_groups.append(neighbor_group)
            elif neighbor_group.liberty_count == 1:
                return False

        return all(group.liberty_count == 1 for group in adjacent_own_groups)

    def will_capture(self, player, point):
        for neighbor in self._neighbor_table[point]:
            neighbor_group = self._grid.get(neighbor)
            if neighbor_group is not None and neighbor_group.color is not player and neighbor_group.liberty_count == 1:
                return True
        return False

    def is_on_grid(self, point):
        return 1 <= point.row <= self.size and 1 <= point.col <= self.size

    def get_color(self, point):
        group = self._grid.get(point)
        return group.color if group is not None else None

    def __getitem__(self, point):
        return self._grid.get(point)

    def __eq__(self, other):
        return isinstance(other, Board) and self.size == other.size and self._hash == other._hash

    def __hash__(self):
        return self._hash

    def __deepcopy__(self, memo):
        copied = Board(self.size)
        copied._grid = copy.copy(self._grid)
        copied._hash = self._hash
        return copied


class GameState:
    def __init__(self, board, next_player, previous, move, komi):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move
        self.komi = komi

        self.previous_states = (previous.previous_states | {hash(previous.board)}
                                if previous is not None else frozenset())

    @staticmethod
    def new_game(board_size, komi):
        return GameState(Board(board_size), Player.black, None, None, komi)

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move, self.komi)

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        return self.board.is_self_capture(player, move.point)

    # @property
    # def situation(self):
    #     return self.next_player, self.board

    def does_move_violate_ko(self, player, move):
        if not move.is_play or not self.board.will_capture(player, move.point):
            return False

        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        return hash(next_board) in self.previous_states

    def is_valid_move(self, move):
        return not self.is_over and (
            (move.is_pass or move.is_resign) or
            (self.board[move.point] is None and
             not self.is_move_self_capture(self.next_player, move) and
             not self.does_move_violate_ko(self.next_player, move))
        )

    @property
    def is_over(self):
        return self.last_move is not None and (
            self.last_move.is_resign or
            (self.last_move.is_pass and
             self.previous_state.last_move is not None and
             self.previous_state.last_move.is_pass)
        )

    @property
    def possible_moves(self):
        if self.is_over:
            return []

        moves = [move for move in (Move.play(Point(row, col))
                                   for row in range(1, self.board.size + 1)
                                   for col in range(1, self.board.size + 1))
                 if self.is_valid_move(move)]

        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    @property
    def winner(self):
        assert self.is_over

        return self.next_player if self.last_move.is_resign else Score.compute(self).winner
