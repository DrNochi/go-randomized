import random


class Sampler:
    def __init__(self, index, test_samples=100, max_year=2015, seed=1337, test_seed=None):
        self.index = index
        self.test_samples = test_samples
        self.max_year = max_year

        self._games = [(info.filename, i) for info in self.index.archive_info
                       if info.year <= self.max_year
                       for i in range(info.games)]

        random.seed(test_seed if test_seed is not None else seed)
        self._test_games = self.draw_samples(test_samples)
        if test_seed is not None:
            random.seed(seed)

    def draw_data(self, dtype, samples):
        print('>>> Drawing {} samples from {} games'.format(samples, len(self._games)))

        if dtype == 'test':
            if samples is None:
                return self._test_games
            else:
                assert samples <= self.test_samples
                return random.sample(self._test_games, samples)
        elif dtype == 'train':
            if samples is None:
                return [g for g in self._games if g not in self._test_games]
            else:
                return self.draw_training_samples(samples)
        raise ValueError(dtype + " is not a valid data type, choose from 'train' or 'test'")

    def draw_samples(self, samples):
        sample_set = set()
        while len(sample_set) < samples:
            sample = random.choice(self._games)
            if sample not in sample_set:
                sample_set.add(sample)
        return list(sample_set)

    def draw_training_samples(self, samples):
        sample_set = set()
        while len(sample_set) < samples:
            sample = random.choice(self._games)
            if sample not in sample_set and sample not in self._test_games:
                sample_set.add(sample)
        return list(sample_set)
