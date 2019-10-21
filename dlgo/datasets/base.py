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

    # def with_batch_size(self, batch_size):
    #     return DataGeneratorIterator(self, batch_size)
    #
    # def __len__(self):
    #     return self.length(self._last_batch_size)
    #
    # def __iter__(self):
    #     return self.with_batch_size(self._last_batch_size)

# class DataGeneratorIterator:
#     def __init__(self, data_generator, batch_size):
#         self._data_generator = data_generator
#         self._batch_size = batch_size
#         self._generator = data_generator.generate(batch_size)
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         return next(self._generator)
#
#     def __len__(self):
#         return self._data_generator.length(self._batch_size)
