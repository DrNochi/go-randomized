from tensorflow import keras


def alphago_policy(input_shape):
    return _alphago_model(input_shape, is_policy_net=True)


def alphago_value(input_shape):
    return _alphago_model(input_shape, is_policy_net=False)


def _alphago_model(input_shape, is_policy_net=False, num_filters=192, first_kernel_size=5,
                   other_kernel_size=3):
    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(num_filters, first_kernel_size, input_shape=input_shape, padding='same',
                                  data_format='channels_first', activation='relu'))

    for i in range(2, 12):
        model.add(keras.layers.Conv2D(num_filters, other_kernel_size, padding='same',
                                      data_format='channels_first', activation='relu'))

    if is_policy_net:
        model.add(keras.layers.Conv2D(filters=1, kernel_size=1, padding='same',
                                      data_format='channels_first', activation='softmax'))
        model.add(keras.layers.Flatten())
    else:
        model.add(keras.layers.Conv2D(num_filters, other_kernel_size, padding='same',
                                      data_format='channels_first', activation='relu'))
        model.add(keras.layers.Conv2D(filters=1, kernel_size=1, padding='same',
                                      data_format='channels_first', activation='relu'))
        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dense(256, activation='relu'))
        model.add(keras.layers.Dense(1, activation='tanh'))

    return model
