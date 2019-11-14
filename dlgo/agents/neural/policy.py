import numpy as np

from .agent import NeuralAgent, ConstrainedNeuralAgent


class PolicyAgent(NeuralAgent):
    def _predict_moves(self, game_state, encoded_board):
        prediction = self.model.predict_on_batch(np.expand_dims(encoded_board, axis=0))[0]
        return prediction, 0

    def train(self, experience, optimizer, batch_size):
        self.model.compile(loss='categorical_crossentropy', optimizer=optimizer)

        y = experience.actions * experience.rewards[:, None]

        self.model.fit(experience.states, y, batch_size=batch_size, epochs=1)


class ConstrainedPolicyAgent(PolicyAgent, ConstrainedNeuralAgent):
    pass
