import numpy as np
from tensorflow import keras

from dlgo.agents.base import Agent
from dlgo.agents.random import is_sensible_move
from dlgo.gotypes import Move


class NeuralAgent(Agent):
    def __init__(self, model, encoder):
        self.model = keras.models.load_model(model)
        self.encoder = encoder

    def select_move(self, game):
        prediction = self.model.predict(np.expand_dims(self.encoder.encode_board(game), axis=0))[0]

        for _ in range(len(prediction)):
            move = self.encoder.decode_move(prediction)
            if game.is_valid(move) and is_sensible_move(game, move):
                return move
            else:
                print('Invalid move found! Checking next...')
                prediction[prediction.argmax()] = 0

        print('No valid move found! Passing...')

        return Move.pass_turn()
