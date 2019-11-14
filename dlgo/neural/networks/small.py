from tensorflow import keras


def small(input_shape, output_shape):
    return keras.models.Sequential([
        keras.layers.ZeroPadding2D(padding=3, input_shape=input_shape, data_format='channels_first'),
        keras.layers.Conv2D(48, (7, 7), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D(padding=2, data_format='channels_first'),
        keras.layers.Conv2D(32, (5, 5), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D(padding=2, data_format='channels_first'),
        keras.layers.Conv2D(32, (5, 5), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.ZeroPadding2D(padding=2, data_format='channels_first'),
        keras.layers.Conv2D(32, (5, 5), data_format='channels_first'),
        keras.layers.Activation('relu'),

        keras.layers.Flatten(),
        keras.layers.Dense(512),
        keras.layers.Activation('relu'),

        keras.layers.Dense(output_shape),
        keras.layers.Activation('softmax')
    ])
