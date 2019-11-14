from tensorflow import keras

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.data.datasets import KGSDataSet
from dlgo.data.encoders import AlphaGoEncoder
from dlgo.data.generators import repeat
from dlgo.neural.networks import alphago_policy

board_size = 19
num_games = 10000

encoder = AlphaGoEncoder(19)
processor = KGSDataSet(encoder)
generator = processor.load_data('train', num_games, use_generator=True)
test_generator = processor.load_data('test', None, use_generator=True)

# f, l = next(generator.generate(128))
# print(f.shape, l.shape)
# f, l = next(test_generator.generate(128))
# print(f.shape, l.shape)

input_shape = encoder.board_shape
alphago_sl_policy = alphago_policy(input_shape)

alphago_sl_policy.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

epochs = 200
batch_size = 128
alphago_sl_policy.fit_generator(
    generator=repeat(generator.generate(batch_size)),
    epochs=epochs,
    steps_per_epoch=generator.length(batch_size),
    validation_data=repeat(test_generator.generate(batch_size)),
    validation_steps=test_generator.length(batch_size),
    callbacks=[keras.callbacks.ModelCheckpoint('alphago_sl_policy_{epoch}.h5')]
)

alphago_sl_agent = ConstrainedPolicyAgent(alphago_sl_policy, encoder)
alphago_sl_agent.serialize('alphago_sl_policy.h5')

# for f in sys.argv[1:]:
#     print(f'Model {f}:')
#     try:
#         alphago_sl_policy = keras.models.load_model(f)
#     except:
#         with h5py.File(f, 'r') as sl_agent_out:
#             alphago_sl_agent = load_prediction_agent(sl_agent_out)
#             alphago_sl_policy = alphago_sl_agent.model
#
#     print(alphago_sl_policy.evaluate_generator(
#         generator=test_generator.generate(batch_size),
#         steps=test_generator.length(batch_size),
#         verbose=True
#     ))
