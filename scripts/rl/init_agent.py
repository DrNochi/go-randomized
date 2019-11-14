import argparse

import h5py
from tensorflow import keras

import dlgo.neural.networks.leaky
from dlgo.agents.neural.pg import policy_gradient_loss, PolicyAgent
from dlgo.data.encoders.encoder import get_encoder_by_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', type=int, default=19)
    parser.add_argument('output_file')
    args = parser.parse_args()

    encoder = get_encoder_by_name('simple', args.board_size)
    model = keras.layers.Sequential()
    for layer in dlgo.neural.networks.leaky.layers(encoder.shape()):
        model.add(layer)
    model.add(keras.layers.Dense(encoder.num_points()))
    model.add(keras.layers.Activation('softmax'))
    opt = keras.optimizers.SGD(lr=0.02)
    model.compile(loss=policy_gradient_loss, optimizer=opt)

    new_agent = PolicyAgent(model, encoder)
    with h5py.File(args.output_file, 'w') as outf:
        new_agent.serialize(outf)


if __name__ == '__main__':
    main()
