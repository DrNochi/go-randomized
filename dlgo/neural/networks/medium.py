from tensorflow import keras


def medium(input_shape, output_shape):
    return keras.models.Sequential([
        keras.layers.ZeroPadding2D((2, 2), input_shape=input_shape, data_format='channels_first'),
        keras.layers.Conv2D(64, (5, 5), padding='valid', data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(64, (5, 5), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D((1, 1), data_format='channels_first'),
        keras.layers.Conv2D(64, (3, 3), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D((1, 1), data_format='channels_first'),
        keras.layers.Conv2D(64, (3, 3), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D((1, 1), data_format='channels_first'),
        keras.layers.Conv2D(64, (3, 3), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.Flatten(),
        keras.layers.Dense(512),
        keras.layers.Activation('relu'),

        keras.layers.Dense(output_shape),
        keras.layers.Activation('softmax')
    ])
