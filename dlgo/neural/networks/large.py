from tensorflow import keras


def large(input_shape,output_shape):
    return _large(input_shape, output_shape, keras.layers.ReLU)


def large_leaky(input_shape, output_shape):
    return _large(input_shape, output_shape, keras.layers.LeakyReLU)


def _large(input_shape, output_shape, activation):
    return keras.models.Sequential([
        keras.layers.ZeroPadding2D((3, 3), input_shape=input_shape, data_format='channels_first'),
        keras.layers.Conv2D(64, (7, 7), padding='valid', data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(64, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(64, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(48, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(48, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(32, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        keras.layers.Conv2D(32, (5, 5), data_format='channels_first'),
        activation(),

        keras.layers.Flatten(),
        keras.layers.Dense(1024),
        activation(),

        keras.layers.Dense(output_shape),
        keras.layers.Activation('softmax')
    ])
