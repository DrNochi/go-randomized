import time

from dlgo.agents.random import RandomAgent
from dlgo.boards.fast import FastGameState
from dlgo.gotypes import Player, Move
from dlgo.scoring import Score
from dlgo.utils import print_board, print_move, point_from_coords


def main():
    game = FastGameState.new_game(9)
    bot = RandomAgent()

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

    print(Score.compute(game, 7.5))


if __name__ == '__main__':
    main()
