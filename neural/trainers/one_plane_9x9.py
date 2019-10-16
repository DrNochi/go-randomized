import numpy as np
from tensorflow import keras

x = np.load('../../game_data/features-40k.npy').squeeze()
y = np.load('../../game_data/labels-40k.npy')

samples = x.shape[0]
train_samples = int(0.9 * samples)
x_train, x_test = x[:train_samples], x[train_samples:]
y_train, y_test = y[:train_samples], y[train_samples:]

rows = x.shape[1]
cols = x.shape[2]

model = keras.models.Sequential([
    keras.layers.Input(x.shape[1:]),
    keras.layers.Reshape((rows, cols, 1)),
    keras.layers.Conv2D(48, (3, 3), activation='relu', padding='same'),
    keras.layers.Dropout(0.5),
    keras.layers.Conv2D(48, (3, 3), activation='relu', padding='same'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Dropout(0.5),
    keras.layers.Flatten(),
    keras.layers.Dense(512, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(rows * cols, activation='softmax')])
model.summary()

# callbacks = [keras.callbacks.LambdaCallback(on_epoch_end=lambda epoch, logs: model.save())]

model.compile('adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=64, epochs=100, validation_data=(x_test, y_test))

loss, accuracy = model.evaluate(x_test, y_test)
print('Loss:', loss, '- Accuracy:', accuracy)

model.save('../../nn_models/one_plane_9x9.h5')
