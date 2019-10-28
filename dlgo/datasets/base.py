class DataSet:
    def load_data(self, data_type, samples, use_generator=False):
        raise NotImplementedError()


class DataGenerator:
    def generate(self, batch_size):
        raise NotImplementedError()

    def generate_repeating(self, batch_size):
        while True:
            for item in self.generate(batch_size):
                yield item

    def length(self, batch_size):
        raise NotImplementedError()

    def __len__(self):
        return self.length(1)
