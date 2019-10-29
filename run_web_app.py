from dlgo.agents.mcts import StandardMCTSAgent
from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.agents.random import ConstrainedRandomAgent
from dlgo.encoders.basic import SevenPlaneEncoder
from dlgo.frontend.web import get_web_app

app = get_web_app({
    'random': ConstrainedRandomAgent(),
    'mcts': StandardMCTSAgent(700, 1.4),
    'predict': ConstrainedPolicyAgent('nn_models/seven_plane_19x19.best.h5', SevenPlaneEncoder(19, 19))
}).run()
