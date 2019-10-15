from sgfmill.sgf import Sgf_game

from dlgo.boards.fast import FastGameState
from dlgo.gotypes import Player, Move, Point
from dlgo.utils import print_move, print_board

sgf_content = "(;GM[1]FF[4]SZ[9];B[ee];W[ef];B[ff];W[df];B[fe];W[fc];B[ec];W[gd];B[fb])"
sgf_game = Sgf_game.from_string(sgf_content)

game = FastGameState.new_game(sgf_game.size, sgf_game.get_komi())

for sgf_node in sgf_game.main_sequence_iter():
    assert not game.is_over()

    sgf_color, sgf_point = sgf_node.get_move()

    if sgf_color is not None:
        player = Player.black if sgf_color == 'b' else Player.white
        assert player == game.next_player

        if sgf_point is not None:
            sgf_row, sgf_col = sgf_point
            move = Move.play(Point(sgf_row + 1, sgf_col + 1))
        else:
            move = Move.pass_turn()

        assert game.is_valid(move)
        game = game.apply_move(move)

        print_move(player, move)
        print_board(game.board)
