import argparse
import multiprocessing
import os
import random
import time

import numpy as np

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.go import Player
from dlgo.utils import keras, simulate_game, print_board


def play_games(args):
    agent1_fname, agent2_fname, num_games, board_size, gpu_frac = args

    keras.set_gpu_memory_target(gpu_frac)

    random.seed(int(time.time()) + os.getpid())
    np.random.seed(int(time.time()) + os.getpid())

    agent1 = ConstrainedPolicyAgent.load(agent1_fname)
    agent2 = ConstrainedPolicyAgent.load(agent2_fname)

    wins, losses = 0, 0
    color1 = Player.black
    for i in range(num_games):
        print(f'Simulating game {i + 1}/{num_games}...')

        if color1 is Player.black:
            black_player, white_player = agent1, agent2
        else:
            white_player, black_player = agent1, agent2

        game, score = simulate_game(board_size, 7.5, black_player, white_player)
        print_board(game.board)

        if score.winner is color1:
            print('Agent 1 wins')
            wins += 1
        else:
            print('Agent 2 wins')
            losses += 1
        print(f'Agent 1 record: {wins}/{wins + losses}')

        color1 = color1.other

    return wins, losses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent1', required=True)
    parser.add_argument('--agent2', required=True)
    parser.add_argument('--num-games', '-n', type=int, default=10)
    parser.add_argument('--num-workers', '-w', type=int, default=1)
    parser.add_argument('--board-size', '-b', type=int, default=19)

    args = parser.parse_args()

    games_per_worker = args.num_games // args.num_workers
    gpu_frac = 0.95 / float(args.num_workers)
    pool = multiprocessing.Pool(args.num_workers)
    worker_args = [
        (args.agent1, args.agent2, games_per_worker, args.board_size, gpu_frac)
        for _ in range(args.num_workers)
    ]
    game_results = pool.map(play_games, worker_args)

    total_wins, total_losses = 0, 0
    for wins, losses in game_results:
        total_wins += wins
        total_losses += losses

    print('FINAL RESULTS:')
    print(f'Agent 1: {total_wins}')
    print(f'Agent 2: {total_losses}')


if __name__ == '__main__':
    main()
