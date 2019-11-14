import argparse
import multiprocessing
import os
import random
import tempfile
import time

import numpy as np

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.go import Player
from dlgo.neural.rl import ExperienceCollector, ExperienceBuffer
from dlgo.utils import keras, simulate_game


def get_temp_file():
    fd, fname = tempfile.mkstemp(prefix='dlgo-train')
    os.close(fd)
    return fname


def do_self_play(board_size, agent_filename,
                 num_games, temperature,
                 experience_filename,
                 gpu_frac):
    keras.set_gpu_memory_target(gpu_frac)

    random.seed(int(time.time()) + os.getpid())
    np.random.seed(int(time.time()) + os.getpid())

    agent1 = ConstrainedPolicyAgent.load(agent_filename)
    agent1.temperature = temperature
    agent2 = ConstrainedPolicyAgent.load(agent_filename)
    agent2.temperature = temperature

    collector1 = ExperienceCollector()
    collector2 = ExperienceCollector()

    color1 = Player.black
    for i in range(num_games):
        print(f'Simulating game {i + 1}/{num_games}...')
        collector1.begin_episode()
        agent1.collector = collector1
        collector2.begin_episode()
        agent2.collector = collector2

        if color1 is Player.black:
            black_player, white_player = agent1, agent2
        else:
            white_player, black_player = agent1, agent2

        game, score = simulate_game(black_player, 7.5, white_player, board_size)

        if score.winner is color1:
            print('Agent 1 wins.')
            collector1.complete_episode(reward=1)
            collector2.complete_episode(reward=-1)
        else:
            print('Agent 2 wins.')
            collector2.complete_episode(reward=1)
            collector1.complete_episode(reward=-1)

        color1 = color1.other

    experience = ExperienceBuffer.combine_experience([collector1, collector2])
    print(f'Saving experience buffer to {experience_filename}\n')
    experience.serialize(experience_filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--learning-agent', required=True)
    parser.add_argument('--num-games', '-n', type=int, default=10)
    parser.add_argument('--experience-out', '-o', required=True)
    parser.add_argument('--num-workers', '-w', type=int, default=1)
    parser.add_argument('--temperature', '-t', type=float, default=0.0)
    parser.add_argument('--board-size', '-b', type=int, default=19)

    args = parser.parse_args()

    experience_files = []
    workers = []
    gpu_frac = 0.95 / float(args.num_workers)
    games_per_worker = args.num_games // args.num_workers
    print('Starting workers...')
    for i in range(args.num_workers):
        filename = get_temp_file()
        experience_files.append(filename)
        worker = multiprocessing.Process(
            target=do_self_play,
            args=(
                args.board_size,
                args.learning_agent,
                games_per_worker,
                args.temperature,
                filename,
                gpu_frac,
            )
        )
        worker.start()
        workers.append(worker)

    print('Waiting for workers...')
    for worker in workers:
        worker.join()

    print('Merging experience buffers...')
    filename = experience_files[0]
    other_filenames = experience_files[1:]
    combined_buffer = ExperienceBuffer.load(filename)
    for filename in other_filenames:
        next_buffer = ExperienceBuffer.load(filename)
        combined_buffer = ExperienceBuffer.combine_experience([combined_buffer, next_buffer])

    print(f'Saving into {args.experience_out}...')
    combined_buffer.serialize(args.experience_out)

    for fname in experience_files:
        os.unlink(fname)


if __name__ == '__main__':
    main()
