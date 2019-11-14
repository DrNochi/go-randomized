from dlgo.agents.neural import ConstrainedPolicyAgent, ConstrainedValueAgent
from dlgo.agents.neural.alphago import AlphaGoMCTS

fast_policy = ConstrainedPolicyAgent.load('alphago_sl_policy.h5')
strong_policy = ConstrainedPolicyAgent.load('alphago_rl_policy.h5')
value = ConstrainedValueAgent.load('alphago_value.h5')

alphago = AlphaGoMCTS(strong_policy, fast_policy, value)
