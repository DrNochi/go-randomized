import multiprocessing
import os
import random
import uuid

import numpy as np
from tensorflow import keras

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.agents.random import FastConstrainedRandomAgent
from dlgo.boards.fast import FastGameState
from dlgo.encoders.basic import SevenPlaneEncoder
from dlgo.gotypes import Player
from dlgo.train.experience import ExperienceAgent
from neural.utils import limit_gpu_memory

board_size = 19
encoder = SevenPlaneEncoder(board_size, board_size)

cache = '.cache/experience'
model_file = '../../nn_models/seven_plane_19x19.rl.h5'
persist_experience_to_disk = True

current_agent = None
original_agent = None
random_agent = FastConstrainedRandomAgent()


def init_worker():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

    limit_gpu_memory()

    global current_agent, original_agent
    current_agent = ConstrainedPolicyAgent(model_file, encoder, sample=True)
    original_agent = ConstrainedPolicyAgent('../../nn_models/seven_plane_19x19.best.h5', encoder, sample=True)

    seed = random.SystemRandom().randint(0, (1 << 32) - 1)
    random.seed(seed)
    np.random.seed(seed)

    print('>>> [WORKER] Initialized')


def generate_experience(args):
    print('>>> [WORKER] Generating experience ({})'.format(args))

    black = ExperienceAgent(get_agent(), encoder)
    white = ExperienceAgent(get_agent(), encoder)

    winner = run_simulation({Player.black: black, Player.white: white})

    black.experience.add_final_reward(1 if winner == Player.black else -1)
    white.experience.add_final_reward(1 if winner == Player.white else -1)

    return save_experience(black.experience), save_experience(white.experience)


def get_agent():
    return random.choices((current_agent, original_agent, random_agent), weights=(1, 1, 0.1))[0]


def run_simulation(players):
    game = FastGameState.new_game(board_size, 7.5)
    while not game.is_over():
        move = players[game.next_player].select_move(game)
        game = game.apply_move(move)

    # print('')
    # print_board(game.board)
    # print('')

    return game.winner


def save_experience(experience):
    features, labels = experience.for_training()

    if persist_experience_to_disk:
        file = os.path.join(cache, str(uuid.uuid4()) + '.npz')
        np.savez(file, features=features, labels=labels)
        return file
    else:
        return features, labels


def train_on_experience(pipe):
    print('>>> [TRAINER] Started')

    limit_gpu_memory()
    model = keras.models.load_model(model_file)
    model.compile('sgd', loss='categorical_crossentropy')

    while True:
        msg = pipe.recv()
        # print('>>> [TRAINER] Message: {}'.format(msg))

        if msg is None:
            print('>>> [TRAINER] Shutting down')
            break
        if msg == '#save':
            print('>>> [TRAINER] Model saved')
            model.save(model_file)
            pipe.send('saved')
        else:
            if persist_experience_to_disk:
                with np.load(msg) as experience:
                    features, labels = experience['features'], experience['labels']
                os.remove(msg)
            else:
                features, labels = msg
            model.train_on_batch(features, labels)


def train_one_epoch(games_per_epoch, trainer):
    worker_count = 2  # multiprocessing.cpu_count() - 1
    with multiprocessing.Pool(worker_count, initializer=init_worker, initargs=()) as workers:
        experience = workers.imap_unordered(generate_experience, range(games_per_epoch))
        for black, white in experience:
            trainer.send(black)
            trainer.send(white)
    trainer.send('#save')
    assert trainer.recv() == 'saved'


def train(epochs, games_per_epoch):
    if not os.path.isdir(cache):
        os.makedirs(cache)

    trainer_pipe_, trainer_pipe = multiprocessing.Pipe()
    trainer = multiprocessing.Process(target=train_on_experience, args=(trainer_pipe_,))
    trainer.start()

    for epoch in range(epochs):
        print('>>> Epoch {}/{}:'.format(epoch, epochs))
        train_one_epoch(games_per_epoch, trainer_pipe)
        print('>>> Epoch {} finished - played {} games total'.format(epoch, (epoch + 1) * games_per_epoch))

    trainer_pipe.send(None)
    trainer.join()


if __name__ == '__main__':
    print('>>> Start training')
    train(1000, 1000)
