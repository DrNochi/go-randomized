#!/usr/bin/env python3

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.encoders.basic import SevenPlaneEncoder
from dlgo.frontend.gtp import GTPFrontend

agent = ConstrainedPolicyAgent('nn_models/seven_plane_19x19.best.h5', SevenPlaneEncoder(19, 19))
gtp = GTPFrontend(agent)
gtp.run()
