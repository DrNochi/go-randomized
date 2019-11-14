from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.agents.termination import PassWhenOpponentPasses, TerminationAgent
from dlgo.frontend.gtp import GTPFrontend

agent = ConstrainedPolicyAgent.load('data/agents/betago.hdf5')
termination_agent = TerminationAgent(agent, PassWhenOpponentPasses())

GTPFrontend(termination_agent).run()
