import glob
import os

import numpy as np

from dlgo.datasets.base import DataGenerator


class KGSDataGenerator(DataGenerator):
    def __init__(self, data_directory, data_type, sample_data):
        self._length = {}
        self.data_directory = data_directory
        self.data_type = data_type
        self.sample_data = sample_data

    def generate(self, batch_size):
        archives = set(file_name for file_name, index in self.sample_data)

        for archive in archives:
            data_file = archive.replace('.tar.gz', '') + self.data_type
            file_pattern = os.path.join(self.data_directory, data_file + '_features_*.npy')

            for feature_file in glob.glob(file_pattern):
                label_file = feature_file.replace('features', 'labels')

                features = np.load(feature_file)
                labels = np.load(label_file)

                while features.shape[0] >= batch_size:
                    feature_batch, features = features[:batch_size], features[batch_size:]
                    label_batch, labels = labels[:batch_size], labels[batch_size:]
                    yield feature_batch, label_batch

    def length(self, batch_size):
        if batch_size not in self._length:
            self._length[batch_size] = 0
            for _ in self.generate(batch_size):
                self._length[batch_size] += 1

        return self._length[batch_size]
