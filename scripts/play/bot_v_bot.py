import time

from dlgo.agents import ConstrainedRandomAgent
from dlgo.go import GameState, Player
from dlgo.utils import print_board, print_move


def main():
    game = GameState.new_game(9, 7.5)

    bots = {
        Player.black: ConstrainedRandomAgent(),
        Player.white: ConstrainedRandomAgent(),
    }

    while not game.is_over:
        time.sleep(0.3)

        print(chr(27) + '[2J')
        if game.last_move is None:
            print(f'{game.next_player} to move')
        else:
            print_move(game.next_player.other, game.last_move)
        print('')
        print_board(game.board)

        bot_move = bots[game.next_player].select_move(game)
        game = game.apply_move(bot_move)


if __name__ == '__main__':
    main()
