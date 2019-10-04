from dlgo.agent.naive import RandomBot
from dlgo.goboard_fast import GameState, Move
from dlgo.gotypes import Player
from dlgo.utils import print_board, print_move, point_from_coords
from dlgo.scoring import GameResult
import time


def main():
    game = GameState.new_game(9)
    bot = RandomBot()

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

    print(GameResult.compute(game, 7.5))


if __name__ == '__main__':
    main()
