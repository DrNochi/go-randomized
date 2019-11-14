from enum import Enum

import h5py
import numpy as np

from dlgo.data.encoders import get_encoder
from dlgo.go import Move
from dlgo.utils import is_sensible_move
from dlgo.utils.keras import load_model_from_hdf5_group, save_model_to_hdf5_group
from ..agent import Agent


class Policy(Enum):
    eps_greedy = 1
    weighted = 2


class NeuralAgent(Agent):
    def __init__(self, model, encoder, policy=Policy.eps_greedy, temperature=0, collector=None):
        self.model = model
        self.encoder = encoder
        self.policy = policy
        self.temperature = temperature
        self.collector = collector

    def select_move(self, game_state):
        encoded_board = self.encoder.encode_board(game_state)

        move, board_value = self._select_move(game_state, encoded_board)
        encoded_move = self.encoder.encode_move(move)

        if self.collector is not None:
            self.collector.record_decision(encoded_board, encoded_move, board_value)

        return move

    def _select_move(self, game_state, encoded_board):
        moves, board_value = self._predict_moves(game_state, encoded_board)
        ranked_moves = self._rank_moves(moves)

        for m in ranked_moves:
            move = Move.play(self.encoder.decode_point(m))
            if game_state.is_valid_move(move):
                return move, board_value

        assert False

    def _predict_moves(self, game_state, encoded_board):
        raise NotImplementedError()

    def _rank_moves(self, prediction):
        num_moves = self.encoder.move_shape
        assert len(prediction) == num_moves

        if self.policy is Policy.eps_greedy:
            if np.random.random() < self.temperature:
                return np.random.shuffle(np.arange(num_moves))
            else:
                return np.argsort(prediction)[::-1]
        elif self.policy is Policy.weighted:
            epsilon = 1e-6
            prediction = np.power(prediction, 1.0 / self.temperature)
            prediction = np.clip(prediction, epsilon, 1 - epsilon)
            prediction /= np.sum(prediction)
            return np.random.choice(np.arange(num_moves), num_moves, p=prediction, replace=False)

    def train(self, experience, optimizer, batch_size):
        raise NotImplementedError()

    def serialize(self, file):
        with h5py.File(file, 'w') as serialized:
            serialized.create_group('encoder')
            serialized['encoder'].attrs['name'] = type(self.encoder).name
            serialized['encoder'].attrs['board_width'] = self.encoder.board_size
            serialized['encoder'].attrs['board_height'] = self.encoder.board_size

            serialized.create_group('model')
            save_model_to_hdf5_group(self.model, serialized['model'])

    @classmethod
    def load(cls, file):
        with h5py.File(file, 'r') as serialized:
            model = load_model_from_hdf5_group(serialized['model'])

            encoder_name = serialized['encoder'].attrs['name']
            board_size = serialized['encoder'].attrs['board_width']
            encoder = get_encoder(encoder_name, board_size)

        return cls(model, encoder)


class ConstrainedNeuralAgent(NeuralAgent):
    def __init__(self, model, encoder, policy=Policy.eps_greedy, temperature=0, collector=None,
                 constraint=is_sensible_move):
        super().__init__(model, encoder, policy, temperature, collector)
        self.constraint = constraint

    def _select_move(self, game_state, encoded_board):
        moves, board_value = self._predict_moves(game_state, encoded_board)
        ranked_moves = self._rank_moves(moves)

        for m in ranked_moves:
            move = Move.play(self.encoder.decode_point(m))
            if game_state.is_valid_move(move) and self.constraint(game_state, move):
                return move, board_value

        return Move.pass_turn(), board_value

    def _predict_moves(self, game_state, encoded_board):
        raise NotImplementedError()

    def train(self, experience, optimizer, batch_size):
        raise NotImplementedError()
