import argparse

from tensorflow import keras

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.neural.rl import ExperienceBuffer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--learning-agent', required=True)
    parser.add_argument('--agent-out', required=True)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--bs', type=int, default=512)
    parser.add_argument('experience', nargs='+')

    args = parser.parse_args()

    learning_agent = ConstrainedPolicyAgent.load(args.learning_agent)
    for exp_filename in args.experience:
        print('Training with %s...' % exp_filename)
        exp_buffer = ExperienceBuffer.load(exp_filename)
        optimizer = keras.optimizers.SDG(lr=args.lr, clipnorm=1.0)
        learning_agent.train(exp_buffer, optimizer, args.bs)

    learning_agent.serialize(args.agent_out)


if __name__ == '__main__':
    main()
