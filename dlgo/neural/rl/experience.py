import h5py
import numpy as np


class ExperienceCollector:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.advantages = []

        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_values = []

    def begin_episode(self):
        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_values = []

    def record_decision(self, state, action, value):
        self._current_episode_states.append(state)
        self._current_episode_actions.append(action)
        self._current_episode_values.append(value)

    def complete_episode(self, reward):
        self.states += self._current_episode_states
        self.actions += self._current_episode_actions
        self.rewards += [reward for _ in self._current_episode_actions]
        self.advantages += [reward - value for value in self._current_episode_values]

        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_values = []


class ExperienceBuffer:
    def __init__(self, states, actions, rewards, advantages):
        self.states = states
        self.actions = actions
        self.rewards = rewards
        self.advantages = advantages

    @staticmethod
    def combine_experience(collectors):
        return ExperienceBuffer(
            np.concatenate([np.array(c.states) for c in collectors]),
            np.concatenate([np.array(c.actions) for c in collectors]),
            np.concatenate([np.array(c.rewards) for c in collectors]),
            np.concatenate([np.array(c.advantages) for c in collectors])
        )

    def serialize(self, file):
        with h5py.File(file, 'w') as serialized:
            serialized.create_group('experience')
            serialized['experience'].create_dataset('states', data=self.states)
            serialized['experience'].create_dataset('actions', data=self.actions)
            serialized['experience'].create_dataset('rewards', data=self.rewards)
            serialized['experience'].create_dataset('advantages', data=self.advantages)

    @staticmethod
    def load(file):
        with h5py.File(file, 'r') as serialized:
            return ExperienceBuffer(
                np.array(serialized['experience']['states']),
                np.array(serialized['experience']['actions']),
                np.array(serialized['experience']['rewards']),
                np.array(serialized['experience']['advantages'])
            )
