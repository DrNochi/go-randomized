from dlgo.agents import StandardMCTSAgent
from dlgo.frontend.web import get_web_app


def main():
    bot = StandardMCTSAgent(700, temperature=1.4)
    web_app = get_web_app({'mcts': bot})
    web_app.run()


if __name__ == '__main__':
    main()
