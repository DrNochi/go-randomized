from dlgo.agent.naive import RandomBot
from dlgo.goboard import GameState
from dlgo.gotypes import Player
from dlgo.utils import print_board, print_move
from dlgo.scoring import compute_game_result
import time


def main():
    game = GameState.new_game(9)
    bots = {
        Player.black: RandomBot(),
        Player.white: RandomBot(),
    }

    while not game.is_over():
        # time.sleep(0.3)

        # print(chr(27) + "[2J")
        print("Current State:")
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
    print(compute_game_result(game).__str__())
    # time.sleep(3)

if __name__ == '__main__':
    main()
