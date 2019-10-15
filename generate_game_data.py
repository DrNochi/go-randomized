import argparse

import numpy as np

from dlgo.agents.mcts import StandardMCTSAgent
from dlgo.boards.fast import FastGameState
from dlgo.encoders.oneplane import OnePlaneEncoder
from dlgo.utils import print_move, print_board


def generate_game_data(board_size, komi, rollouts, temperature, max_moves):
    encoder = OnePlaneEncoder(board_size, board_size)
    boards, moves = [], []

    game = FastGameState.new_game(board_size, komi)
    bot = StandardMCTSAgent(rollouts, temperature)

    while not game.is_over():
        move = bot.select_move(game)

        if move.is_play:
            boards.append(encoder.encode_board(game))
            moves.append(encoder.encode_move(move))

        print_move(game.next_player, move)
        game = game.apply_move(move)
        print_board(game.board)

        max_moves -= 1
        if max_moves == 0:
            break

    return np.array(boards), np.array(moves)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--num-games', '-n', type=int, default=20)
    argument_parser.add_argument('--board-size', '-b', type=int, default=9)
    argument_parser.add_argument('--komi', '-k', type=float, default=7.5)
    argument_parser.add_argument('--rollouts', '-r', type=int, default=1000)
    argument_parser.add_argument('--temperature', '-t', type=float, default=0.8)
    argument_parser.add_argument('--max-moves', '-m', type=int, default=60)
    argument_parser.add_argument('--boards-out')
    argument_parser.add_argument('--moves-out')
    arguments = argument_parser.parse_args()

    boards_per_game = []
    moves_per_game = []

    for i in range(arguments.num_games):
        print('Generating game %d/%d...' % (i + 1, arguments.num_games))

        game_boards, game_moves = generate_game_data(arguments.board_size, arguments.komi, arguments.rollouts,
                                                     arguments.temperature, arguments.max_moves)

        boards_per_game.append(game_boards)
        moves_per_game.append(game_moves)

    boards = np.concatenate(boards_per_game)
    moves = np.concatenate(moves_per_game)

    np.save(arguments.board_out, boards)
    np.save(arguments.move_out, moves)


if __name__ == '__main__':
    main()
