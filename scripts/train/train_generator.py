from tensorflow import keras

from dlgo.data.datasets import KGSDataSet
from dlgo.data.encoders import OnePlaneEncoder
from dlgo.data.generators import repeat
from dlgo.neural.networks import small

board_size = 19
num_classes = board_size ** 2
num_games = 100

encoder = OnePlaneEncoder(board_size)
dataset = KGSDataSet(encoder)
generator = dataset.load_data('train', num_games, use_generator=True)
test_generator = dataset.load_data('test', num_games, use_generator=True)

input_shape = encoder.board_shape
model = small(input_shape, num_classes)
model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

epochs = 5
batch_size = 128

model.fit_generator(generator=repeat(generator.generate(batch_size)), epochs=epochs,
                    steps_per_epoch=generator.length(batch_size),
                    validation_data=repeat(test_generator.generate(batch_size)),
                    validation_steps=test_generator.length(batch_size),
                    callbacks=[keras.callbacks.ModelCheckpoint('../../data/checkpoints/small_model_epoch_{epoch}.h5')])

model.evaluate_generator(generator=test_generator.generate(batch_size, num_classes),
                         steps=test_generator.length(batch_size))
