import numpy as np

from dlgo.agents.base import Agent


class Experience:
    def __init__(self, encoder):
        self.encoder = encoder

        self.states = []
        self.actions = []
        self.reward = 0

    def record_decision(self, state, action):
        if self.encoder.can_encode_move(action):
            self.states.append(state)
            self.actions.append(action)

    def add_final_reward(self, reward):
        self.reward = reward

    def for_training(self):
        positions = len(self.states)
        features = np.zeros((positions,) + self.encoder.board_shape)
        labels = np.zeros((positions,) + self.encoder.move_shape)

        for i in range(positions):
            features[i] = self.encoder.encode_board(self.states[i])
            labels[i] = self.encoder.encode_move(self.actions[i]) * self.reward

        return features, labels


class ExperienceAgent(Agent):
    def __init__(self, agent, encoder):
        self.base_agent = agent
        self.experience = Experience(encoder)

    def select_move(self, game):
        move = self.base_agent.select_move(game)
        self.experience.record_decision(game, move)
        return move
