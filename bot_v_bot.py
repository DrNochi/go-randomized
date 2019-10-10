import time

from dlgo.agents.random import FastConstrainedRandomAgent
from dlgo.boards.fast import FastGameState
from dlgo.gotypes import Player
from dlgo.scoring import Score
from dlgo.utils import print_board, print_move


def main():
    game = FastGameState.new_game(9, 7.5)
    bots = {
        Player.black: FastConstrainedRandomAgent(),
        Player.white: FastConstrainedRandomAgent(),
    }

    while not game.is_over():
        time.sleep(0.3)

        print(chr(27) + "[2J")
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)

    print(Score.compute(game))


if __name__ == '__main__':
    main()
