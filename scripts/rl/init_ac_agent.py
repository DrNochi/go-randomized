import argparse

import h5py
from tensorflow import keras

import dlgo.networks
from dlgo.data.encoders.encoder import get_encoder_by_name
from dlgo.agents.neural.actor_critic import ACAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', type=int, default=19)
    parser.add_argument('--network', default='large')
    parser.add_argument('--hidden-size', type=int, default=512)
    parser.add_argument('output_file')
    args = parser.parse_args()

    encoder = get_encoder_by_name('simple', args.board_size)
    board_input = keras.layers.Input(shape=encoder.shape(), name='board_input')

    processed_board = board_input
    network = getattr(dlgo.networks, args.network)
    for layer in network.layers(encoder.shape()):
        processed_board = layer(processed_board)

    policy_hidden_layer = keras.layers.Dense(args.hidden_size, activation='relu')(processed_board)
    policy_output = keras.layers.Dense(encoder.num_points(), activation='softmax')(policy_hidden_layer)

    value_hidden_layer = keras.layers.Dense(args.hidden_size, activation='relu')(processed_board)
    value_output = keras.layers.Dense(1, activation='tanh')(value_hidden_layer)

    model = keras.models.Model(inputs=[board_input], outputs=[policy_output, value_output])

    new_agent = ACAgent(model, encoder)
    with h5py.File(args.output_file, 'w') as outf:
        new_agent.serialize(outf)


if __name__ == '__main__':
    main()
