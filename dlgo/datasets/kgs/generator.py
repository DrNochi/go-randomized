import glob
import os

import numpy as np

from dlgo.datasets.base import DataGenerator


class KGSDataGenerator(DataGenerator):
    def __init__(self, data_directory, data_type, sample_data):
        super().__init__()
        self.data_directory = data_directory
        self.data_type = data_type
        self.sample_data = sample_data

    # def get_num_samples(self, batch_size=128, num_classes=19 * 19):
    #     if self.num_samples is not None:
    #         return self.num_samples
    #     else:
    #         self.num_samples = 0
    #         for X, y in self._generate(batch_size=batch_size, num_classes=num_classes):
    #             self.num_samples += X.shape[0]
    #         return self.num_samples

    def _generate(self, batch_size):
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

    def generate(self, batch_size=None):
        if batch_size is None:
            batch_size = self._last_batch_size
        self._last_batch_size = batch_size

        while True:
            for item in self._generate(batch_size):
                yield item
