import argparse

from dlgo.agents import StandardMCTSAgent
from dlgo.agents.neural import ConstrainedPolicyAgent, ConstrainedQAgent, ConstrainedActorCriticAgent
from dlgo.frontend.web import get_web_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind-address', default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=5000)
    parser.add_argument('--pg-agent', help='9x9 policy agent')
    parser.add_argument('--predict-agent', help='19x19 policy agent')
    parser.add_argument('--q-agent', help='9x9 Q agent')
    parser.add_argument('--ac-agent', help='actor critic agent')

    args = parser.parse_args()

    bots = {'mcts': StandardMCTSAgent(800, temperature=0.7)}
    if args.pg_agent:
        bots['pg'] = ConstrainedPolicyAgent.load(args.pg_agent)
    if args.predict_agent:
        bots['predict'] = ConstrainedPolicyAgent.load(args.predict_agent)
    if args.q_agent:
        q_bot = ConstrainedQAgent.load(args.q_agent)
        q_bot.temperature = 0.01
        bots['q'] = q_bot
    if args.ac_agent:
        ac_bot = ConstrainedActorCriticAgent.load(args.ac_agent)
        ac_bot.temperature = 0.05
        bots['ac'] = ac_bot

    web_app = get_web_app(bots)
    web_app.run(host=args.bind_address, port=args.port, threaded=False)


if __name__ == '__main__':
    main()
