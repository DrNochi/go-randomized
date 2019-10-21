import numpy as np
from tensorflow import keras

from dlgo.agents.base import Agent
from dlgo.agents.utils import is_sensible_move
from dlgo.gotypes import Move


class PolicyAgent(Agent):
    def __init__(self, model, encoder, sample=False):
        self.model = keras.models.load_model(model)
        self.encoder = encoder
        self.sample_prediction = sample

    def _predict_moves(self, game):
        prediction = self.model.predict(np.expand_dims(self.encoder.encode_board(game), axis=0))[0]

        if self.sample_prediction:
            epsilon = 1e-6

            prediction = prediction ** 3
            prediction = np.clip(prediction, epsilon, 1 - epsilon)
            prediction /= np.sum(prediction)

            return self.encoder.sample_moves(prediction)
        else:
            return self.encoder.decode_moves(prediction)

    def select_move(self, game):
        moves = self._predict_moves(game)

        for m in moves:
            move = self.encoder.get_move(m)
            if game.is_valid(move):
                return move

        assert False


class ConstrainedPolicyAgent(PolicyAgent):
    def __init__(self, model, encoder, sample=False, constraint=is_sensible_move):
        super().__init__(model, encoder, sample)
        self.constraint = constraint

    def select_move(self, game):
        moves = self._predict_moves(game)

        for m in moves:
            move = self.encoder.get_move(m)
            if game.is_valid(move) and self.constraint(game, move):
                return move

        return Move.pass_turn()
