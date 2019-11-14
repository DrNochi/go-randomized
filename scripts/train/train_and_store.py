from dlgo.data.datasets import KGSDataSet
from dlgo.data.encoders import SevenPlaneEncoder
from dlgo.neural.networks import large

board_size = 19
nb_classes = board_size ** 2

encoder = SevenPlaneEncoder(board_size)
processor = KGSDataSet(encoder)

input_shape = encoder.board_shape

X, y = processor.load_data('train', 1000)

model = large(input_shape, nb_classes)
model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])

model.fit(X, y, batch_size=128, epochs=100, verbose=1)

weight_file = '../../data/agents/weights.hd5'
model.save_weights(weight_file, overwrite=True)
model_file = '../../data/agents/model.yml'
with open(model_file, 'w') as yml:
    model_yaml = model.to_yaml()
    yml.write(model_yaml)
