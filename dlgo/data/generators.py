import math

import numpy as np


def repeat(generator, *args, **kwargs):
    while True:
        for item in generator(*args, **kwargs):
            yield item


class DataGenerator:
    def generate(self, batch_size):
        raise NotImplementedError()

    def length(self, batch_size):
        raise NotImplementedError()

    def __len__(self):
        return self.length(1)


class NPZGameDataGenerator(DataGenerator):
    def __init__(self, data_files):
        self._length = None
        self._data_files = data_files

    def generate_game(self):
        for filename, positions in self._data_files:
            data = np.load(filename)
            yield data['features'], data['labels']

    def generate(self, batch_size):
        gen = self.generate_game()

        features = None
        labels = None
        for feature_chunk, label_chunk in gen:
            if features is None:
                features = feature_chunk
                labels = label_chunk
            else:
                features = np.concatenate((features, feature_chunk), axis=0)
                labels = np.concatenate((labels, label_chunk), axis=0)

            while features.shape[0] >= batch_size:
                feature_batch, features = features[:batch_size], features[batch_size:]
                label_batch, labels = labels[:batch_size], labels[batch_size:]
                yield feature_batch, label_batch

        if isinstance(features, np.ndarray) and features.shape[0] > 0:
            yield features, labels

    def length(self, batch_size):
        return math.ceil(len(self) / batch_size)

    def __len__(self):
        if self._length is None:
            self._length = 0
            for filename, positions in self._data_files:
                self._length += positions

        return self._length


class SymmetriesGenerator(DataGenerator):
    def __init__(self, base, board_size):
        self._base = base
        self._board_size = board_size

    def generate(self, batch_size):
        for features, labels in self._base.generate(batch_size):
            samples = labels.shape[0]
            labels_2d = labels[:, :self._board_size ** 2].reshape(samples, 1, self._board_size, self._board_size)
            labels_rest = labels[:, self._board_size ** 2:]

            for i in range(4):
                yield np.rot90(features, i, axes=(2, 3)), np.concatenate(
                    (np.rot90(labels_2d, i, axes=(2, 3)).reshape(samples, self._board_size ** 2), labels_rest),
                    axis=1)

            features = np.flip(features, axis=2)
            labels_2d = np.flip(labels_2d, axis=2)

            for i in range(4):
                yield np.rot90(features, i, axes=(2, 3)), np.concatenate(
                    (np.rot90(labels_2d, i, axes=(2, 3)).reshape(samples, self._board_size ** 2), labels_rest),
                    axis=1)

    def length(self, batch_size):
        return 8 * self._base.length(batch_size)

    def __len__(self):
        return 8 * len(self._base)
