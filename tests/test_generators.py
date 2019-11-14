import unittest

import numpy as np

from dlgo.data.generators import DataGenerator, SymmetriesGenerator


class TestDataGenerator(DataGenerator):
    def __init__(self, features, labels):
        self._features = features
        self._labels = labels

    def generate(self, batch_size):
        assert batch_size == 1
        for i in range(len(self)):
            yield self._features[i:i + 1], self._labels[i: i + 1]

    def length(self, batch_size):
        assert batch_size == 1
        return len(self._features)


class SymmetriesGeneratorTest(unittest.TestCase):
    def test_generator(self):
        base_generator = TestDataGenerator(np.array([
            [[[1, 1, 0],
              [1, 1, 1],
              [0, 0, 0]]],
        ]), np.array([
            [0, 0, 1,
             0, 0, 0,
             0, 0, 0, 1, 1]
        ]))

        generator = SymmetriesGenerator(base_generator, 3).generate(1)

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[1, 1, 0], [1, 1, 1], [0, 0, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 1, 0], [1, 1, 0], [1, 1, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 0, 0], [1, 1, 1], [0, 1, 1]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 1, 1], [0, 1, 1], [0, 1, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 0, 0], [1, 1, 1], [1, 1, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 1, 0], [0, 1, 1], [0, 1, 1]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[0, 1, 1], [1, 1, 1], [0, 0, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]])))

        features, labels = next(generator)
        self.assertTrue(np.array_equal(features, np.array([[[[1, 1, 0], [1, 1, 0], [0, 1, 0]]]])))
        self.assertTrue(np.array_equal(labels, np.array([[0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]])))


if __name__ == '__main__':
    unittest.main()
