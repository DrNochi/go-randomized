from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.data.datasets import KGSDataSet
from dlgo.data.encoders import SevenPlaneEncoder
from dlgo.frontend.web import get_web_app
from dlgo.neural.networks import large

model_file = 'data/agents/deep_bot.h5'

board_size = 19
nb_classes = board_size ** 2
encoder = SevenPlaneEncoder(board_size)
dataset = KGSDataSet(encoder)

X, y = dataset.load_data('train', 100)

input_shape = encoder.board_shape
model = large(input_shape, nb_classes)
model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])

model.fit(X, y, batch_size=128, epochs=20, verbose=1)

deep_learning_bot = ConstrainedPolicyAgent(model, encoder)
deep_learning_bot.serialize(model_file)

bot_from_file = ConstrainedPolicyAgent.load(model_file)
web_app = get_web_app({'predict': bot_from_file})
web_app.run()
