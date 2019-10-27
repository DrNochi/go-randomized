import numpy as np

from dlgo.datasets.base import DataGenerator


class KGSDataGenerator(DataGenerator):
    def __init__(self, data_files):
        super().__init__()
        self.data_files = data_files

    def generate_game(self):
        for base_filename in self.data_files:
            features_file = base_filename + '_features.npy'
            labels_file = base_filename + '_labels.npy'
            yield np.load(features_file), np.load(labels_file)

    def generate(self, batch_size):
        gen = self.generate_game()

        features, labels = next(gen)
        for feature_chunk, label_chunk in gen:
            features = np.concatenate((features, feature_chunk), axis=0)
            labels = np.concatenate((labels, label_chunk), axis=0)

            while features.shape[0] >= batch_size:
                feature_batch, features = features[:batch_size], features[batch_size:]
                label_batch, labels = labels[:batch_size], labels[batch_size:]
                yield feature_batch, label_batch

    def num_games(self):
        return len(self.data_files)
