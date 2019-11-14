import numpy as np

from .agent import NeuralAgent, ConstrainedNeuralAgent


class ActorCriticAgent(NeuralAgent):
    def _predict_moves(self, game_state, encoded_board):
        prediction, board_value = self.model.predict_on_batch(np.expand_dims(encoded_board, axis=0))
        return prediction[0], board_value[0][0]

    def train(self, experience, optimizer, batch_size):
        self.model.compile(loss=['categorical_crossentropy', 'mse'], optimizer=optimizer)

        y_policy = experience.actions * experience.advantages[:, None]
        y_value = np.maximum(experience.rewards, 0)

        self.model.fit(experience.states, [y_policy, y_value], batch_size=batch_size, epochs=1)

    # def diagnostics(self):
    #     return {'value': self.last_state_value}


class ConstrainedActorCriticAgent(ActorCriticAgent, ConstrainedNeuralAgent):
    pass
