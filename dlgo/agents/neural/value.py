import numpy as np

from .agent import NeuralAgent, ConstrainedNeuralAgent


class ValueAgent(NeuralAgent):
    def _predict_moves(self, game_state, encoded_board):
        moves = []
        encoded_boards = []

        for move in game_state.possible_moves:
            if not move.is_play:
                continue
            next_state = game_state.apply_move(move)
            encoded_board = self.encoder.encode_board(next_state)
            encoded_boards.append(encoded_board)
            moves.append(move)

        if moves:
            values = self.model.predict_on_batch(np.array(encoded_boards)).reshape(len(moves))

            prediction = np.zeros(self.encoder.move_shape)
            for move, value in zip(moves, values):
                prediction[self.encoder.encode_point(move.point)] = value
        else:
            prediction = np.ones(self.encoder.move_shape)

        return prediction / np.sum(prediction), 0

    def train(self, experience, optimizer, batch_size):
        self.model.compile(loss='mse', optimizer=optimizer)

        y = np.maximum(experience.rewards, 0)

        self.model.fit(experience.states, y, batch_size=batch_size, epochs=1)

    # def diagnostics(self):
    #     return {'value': self.last_move_value}


class ConstrainedValueAgent(ValueAgent, ConstrainedNeuralAgent):
    pass