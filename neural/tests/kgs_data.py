import numpy as np
from tensorflow import keras

from dlgo.datasets.kgs import KGSDataSet

data = KGSDataSet()
x_train, y_train = data.load_data('train', 100)
x_test, y_test = data.load_data('test', 100)

x_test = np.expand_dims(x_test, axis=3)
x_train = np.expand_dims(x_train, axis=3)

rows = x_test.shape[1]
cols = x_test.shape[2]

model = keras.models.Sequential([
    keras.layers.Input(x_test.shape[1:]),
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

model.compile('adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=100, epochs=10, validation_data=(x_test, y_test))

loss, accuracy = model.evaluate(x_test, y_test)
print('Loss:', loss, '- Accuracy:', accuracy)
