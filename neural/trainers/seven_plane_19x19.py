from tensorflow import keras

from dlgo.datasets.kgs.parallel import ParallelKGSDataSet
from dlgo.encoders.basic import SevenPlaneEncoder

# def generate_symmetries(data_generator):
#     while True:
#         board, move = next(data_generator)
#         move = move.reshape(batch_size, rows, cols)
#         for board, move in ((board, move),
#                             (board[:, ::-1, ...], move[:, ::-1, :]),
#                             (board[:, :, ::-1, ...], move[:, :, ::-1])):
#             yield board, move.reshape(batch_size, rows * cols)
#             yield np.rot90(board, 1, (1, 2)), np.rot90(move, 1, (1, 2)).reshape(batch_size, rows * cols)
#             yield np.rot90(board, 2, (1, 2)), np.rot90(move, 2, (1, 2)).reshape(batch_size, rows * cols)
#             yield np.rot90(board, 3, (1, 2)), np.rot90(move, 3, (1, 2)).reshape(batch_size, rows * cols)

rows = 19
cols = 19

batch_size = 128

data = ParallelKGSDataSet(encoder=SevenPlaneEncoder(rows, cols))
# data_train = data.load_data('train', 5000, use_generator=True)
data_test = data.load_data('test', None, use_generator=True)

input_shape = data.encoder.board_shape
output_shape = data.encoder.move_shape

# model = keras.models.Sequential([
#     keras.layers.Input(input_shape),
#     keras.layers.Conv2D(64, (7, 7), activation='relu', padding='same'),
#     keras.layers.Conv2D(64, (5, 5), activation='relu', padding='same'),
#     keras.layers.Conv2D(64, (5, 5), activation='relu', padding='same'),
#     keras.layers.Conv2D(48, (5, 5), activation='relu', padding='same'),
#     keras.layers.Conv2D(48, (5, 5), activation='relu', padding='same'),
#     keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
#     keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
#     keras.layers.Flatten(),
#     keras.layers.Dense(1024, activation='relu'),
#     keras.layers.Dense(output_shape[0], activation='softmax')])
# model.summary()
#
# model.compile('adam', loss='categorical_crossentropy', metrics=['accuracy'])
#
# model.fit_generator(data_train.generate_repeating(batch_size),
#                     steps_per_epoch=data_train.length(batch_size), epochs=1000,
#                     validation_data=data_test.generate_repeating(batch_size), validation_steps=1,
#                     callbacks=[keras.callbacks.ModelCheckpoint('../../nn_models/seven_plane_19x19.best.h5',
#                                                                save_best_only=True),
#                                keras.callbacks.ModelCheckpoint('../../nn_models/seven_plane_19x19.latest.h5')])

model = keras.models.load_model('../../nn_models/seven_plane_19x19.latest.h5')

loss, accuracy = model.evaluate_generator(data_test.generate(batch_size), steps=data_test.length(batch_size), verbose=1)
print('Loss:', loss, '- Accuracy:', accuracy)

# model.save('../../nn_models/seven_plane_19x19.h5')
