import time

from dlgo.agents.random import FastConstrainedRandomAgent
from dlgo.boards.fast import FastGameState
from dlgo.frontend.cmd import print_move, print_board
from dlgo.frontend.utils import point_from_coords
from dlgo.gotypes import Player, Move
from dlgo.scoring import Score


def main():
    game = FastGameState.new_game(9, 7.5)
    bot = FastConstrainedRandomAgent()

    while not game.is_over():
        time.sleep(0.3)

        print(chr(27) + "[2J")
        print_board(game.board)

        if game.next_player == Player.black:
            human_move = input('-- ')
            if human_move == 'pass':
                move = Move.pass_turn()
            elif human_move == 'resign':
                move = Move.resign()
            else:
                point = point_from_coords(human_move.strip())
                move = Move.play(point)
        else:
            move = bot.select_move(game)

        print_move(game.next_player, move)
        game = game.apply_move(move)

    print(Score.compute(game))


if __name__ == '__main__':
    main()
