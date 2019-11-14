import h5py
from tensorflow import keras

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.data.encoders import AlphaGoEncoder
from dlgo.neural.rl import simulate_games

encoder = AlphaGoEncoder(19)

sl_agent = ConstrainedPolicyAgent.load('alphago_sl_policy.h5')
sl_opponent = ConstrainedPolicyAgent.load('alphago_sl_policy.h5')

alphago_rl_agent = ConstrainedPolicyAgent(sl_agent.model, encoder)
opponent = ConstrainedPolicyAgent(sl_opponent.model, encoder)

num_games = 1000
experience = simulate_games(num_games, 19, 7.5, alphago_rl_agent, opponent)

alphago_rl_agent.train(experience, keras.optimizers.SGD(lr=0.1, clipnorm=1.0), batch_size=128)

alphago_rl_agent.serialize('alphago_rl_policy.h5')
experience.serialize('alphago_rl_experience.h5')
