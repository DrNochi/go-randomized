from tensorflow import keras

from dlgo.datasets.kgs.parallel import ParallelKGSDataSet

data = ParallelKGSDataSet()
data_train = data.load_data('train', 100, use_generator=True)
data_test = data.load_data('test', 100, use_generator=True)

shape = data.encoder.board_shape
rows = shape[0]
cols = shape[1]

model = keras.models.Sequential([
    keras.layers.Input(shape),
    keras.layers.Reshape((rows, cols, 1)),
    keras.layers.Conv2D(48, (7, 7), activation='relu', padding='same'),
    keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
    keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
    keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
    keras.layers.Flatten(),
    keras.layers.Dense(512, activation='relu'),
    keras.layers.Dense(rows * cols, activation='softmax')])
model.summary()

batch_size = 128

model.compile('adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit_generator(data_train.generate_repeating(batch_size), steps_per_epoch=data_train.length(batch_size), epochs=5,
                    validation_data=data_test.generate_repeating(batch_size),
                    validation_steps=data_test.length(batch_size))

loss, accuracy = model.evaluate_generator(data_test.generate_repeating(batch_size), steps=data_test.length(batch_size))
print('Loss:', loss, '- Accuracy:', accuracy)
