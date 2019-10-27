class DataSet:
    def load_data(self, data_type, samples, use_generator=False):
        raise NotImplementedError()


class DataGenerator:
    def __init__(self):
        self._length = None

    def generate(self, batch_size):
        raise NotImplementedError()

    def generate_repeating(self, batch_size):
        while True:
            for item in self.generate(batch_size):
                yield item

    def length(self, batch_size):
        if self._length is not None:
            return self._length
        else:
            self._length = 0
            for _ in self.generate(batch_size):
                self._length += 1
            return self._length
