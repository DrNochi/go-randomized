import unittest

import numpy as np

from dlgo.neural.rl import experience, ExperienceBuffer


class ExperienceTest(unittest.TestCase):
    def test_combine_experience(self):
        collector1 = experience.ExperienceCollector()
        collector2 = experience.ExperienceCollector()

        collector1.begin_episode()
        collector1.record_decision(np.array([[1, 1], [1, 1]]), np.array([1, 0, 0, 0]), 0)
        collector1.record_decision(np.array([[2, 2], [2, 2]]), np.array([0, 2, 0, 0]), 0)
        collector1.complete_episode(reward=1)

        collector1.begin_episode()
        collector1.record_decision(np.array([[3, 3], [3, 3]]), np.array([0, 0, 3, 0]), 0)
        collector1.complete_episode(reward=2)

        collector2.begin_episode()
        collector2.record_decision(np.array([[4, 4], [4, 4]]), np.array([0, 0, 0, 4]), 0)
        collector2.complete_episode(reward=3)

        combined = ExperienceBuffer.combine_experience([collector1, collector2])

        self.assertEqual((4, 2, 2), combined.states.shape)
        self.assertEqual((4, 4), combined.actions.shape)
        self.assertEqual((4,), combined.rewards.shape)
        self.assertEqual([1, 1, 2, 3], list(combined.rewards))


if __name__ == '__main__':
    unittest.main()
