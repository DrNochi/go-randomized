import math

import numpy as np

from dlgo.datasets.base import DataGenerator


class KGSDataGenerator(DataGenerator):
    def __init__(self, data_files):
        self._length = None
        self.data_files = data_files

    def generate_game(self):
        for base_filename, positions in self.data_files:
            features_file = base_filename + '_features.npy'
            labels_file = base_filename + '_labels.npy'
            yield np.load(features_file), np.load(labels_file)

    def generate(self, batch_size):
        gen = self.generate_game()

        features, labels = None, None
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

        if features is not None and features.shape[0] > 0:
            yield features, labels

    def length(self, batch_size):
        return math.ceil(len(self) / batch_size)

    def __len__(self):
        if self._length is None:
            self._length = 0
            for base_filename, positions in self.data_files:
                self._length += positions

        return self._length
