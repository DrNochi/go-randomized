class DataSet:
    def load_data(self, data_type, samples, use_generator=False):
        raise NotImplementedError()


class DataGenerator:
    def __init__(self):
        self._last_batch_size = 1

    def generate(self, batch_size=None):
        raise NotImplementedError()

    def with_batch_size(self, batch_size):
        return DataGeneratorIterator(self, batch_size)

    def __iter__(self):
        return DataGeneratorIterator(self, self._last_batch_size)


class DataGeneratorIterator:
    def __init__(self, data_generator, batch_size):
        self._generator = data_generator
        self._batch_size = batch_size

    def __next__(self):
        return self._generator.generate(self._batch_size)
