from tensorflow import keras

from dlgo.agents.neural.value import ValueAgent
from dlgo.data.encoders.alphago import AlphaGoEncoder
from dlgo.neural.networks import alphago_value
from dlgo.neural.rl import ExperienceBuffer

board_size = 19
encoder = AlphaGoEncoder(board_size)
input_shape = encoder.board_shape
alphago_value_network = alphago_value(input_shape)

alphago_value = ValueAgent(alphago_value_network, encoder)

experience = ExperienceBuffer.load('alphago_rl_experience.h5')

alphago_value.train(experience, keras.optimizers.SGD(lr=0.1, clipnorm=1.0), batch_size=128)

alphago_value.serialize('alphago_value.h5')
