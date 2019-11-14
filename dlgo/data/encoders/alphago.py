import numpy as np

from dlgo.go import Point, Move, Player
from dlgo.utils import is_sensible_move, is_ladder_capture, is_ladder_escape
from .encoder import Encoder

"""
Feature name            num of planes   Description
Stone colour            3               Player stone / opponent stone / empty
Ones                    1               A constant plane filled with 1
Zeros                   1               A constant plane filled with 0
Sensibleness            1               Whether a move is legal and does not fill its own eyes
Turns since             8               How many turns since a move was played
Liberties               8               Number of liberties (empty adjacent points)
Liberties after move    8               Number of liberties after this move is played
Capture size            8               How many opponent stones would be captured
Self-atari size         8               How many of own stones would be captured
Ladder capture          1               Whether a move at this point is a successful ladder capture
Ladder escape           1               Whether a move at this point is a successful ladder escape
"""

feature_offsets = {
    "stone_color": 0,
    "ones": 3,
    "zeros": 4,
    "sensibleness": 5,
    "turns_since": 6,
    "liberties": 14,
    "liberties_after": 22,
    "capture_size": 30,
    "self_atari_size": 38,
    "ladder_capture": 46,
    "ladder_escape": 47,
    "current_player_color": 48
}


def offset(feature):
    return feature_offsets[feature]


class AlphaGoEncoder(Encoder):
    def __init__(self, board_size, use_player_plane=True):
        super().__init__(board_size)
        self.use_player_plane = use_player_plane
        self.num_planes = 48 + use_player_plane

    def encode_board(self, game_state):
        encoded = np.zeros(self.board_shape)

        encoded[offset("ones")] = 1

        if self.use_player_plane and game_state.next_player is Player.black:
            encoded[offset("current_player_color")] = 1

        for r in range(self.board_size):
            for c in range(self.board_size):
                point = Point(r + 1, c + 1)
                group = game_state.board[point]

                if group is None:
                    encoded[offset("stone_color") + 2][r][c] = 1

                    move = Move(point)
                    if game_state.is_valid_move(move):
                        new_state = game_state.apply_move(move)
                        liberties = min(new_state.board[point].liberty_count, 8) - 1
                        encoded[offset("liberties_after") + liberties][r][c] = 1

                        adjacent_groups = {
                            game_state.board[nb]
                            for nb in game_state.board.neighbors(point)
                        }

                        capture_count = 0
                        self_atari_count = 0
                        for group in adjacent_groups:
                            if group is not None and group.liberty_count == 1:
                                if group.color is game_state.next_player:
                                    self_atari_count += len(group.stones)
                                else:
                                    capture_count += len(group.stones)
                        capture_count = min(capture_count, 8 - 1)
                        self_atari_count = min(self_atari_count, 8 - 1)
                        encoded[offset("capture_size") + capture_count][r][c] = 1
                        encoded[offset("self_atari_size") + self_atari_count][r][c] = 1

                        if is_ladder_capture(game_state, point):
                            encoded[offset("ladder_capture")][r][c] = 1
                        if is_ladder_escape(game_state, point):
                            encoded[offset("ladder_escape")][r][c] = 1

                        if is_sensible_move(game_state, move):
                            encoded[offset("sensibleness")][r][c] = 1
                else:
                    if group.color is game_state.next_player:
                        encoded[offset("stone_color")][r][c] = 1
                    else:
                        encoded[offset("stone_color") + 1][r][c] = 1

                    liberties = min(group.liberty_count, 8) - 1
                    encoded[offset("liberties") + liberties][r][c] = 1

                    encoded[offset("turns_since") + 8 - 1][r][c] = 1

        for i in range(7):
            if game_state is None or game_state.last_move is None:
                break
            if game_state.last_move.is_play:
                point = game_state.last_move.point
                encoded[offset("turns_since") + 8 - 1][point.row - 1][point.col - 1] = 0
                encoded[offset("turns_since") + i][point.row - 1][point.col - 1] = 1
            game_state = game_state.previous_state

        return encoded

    @property
    def board_shape(self):
        return self.num_planes, self.board_size, self.board_size
