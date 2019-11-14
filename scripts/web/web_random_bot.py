from dlgo.agents import ConstrainedRandomAgent
from dlgo.frontend.web import get_web_app

random_agent = ConstrainedRandomAgent()
web_app = get_web_app({'random': random_agent})
web_app.run()
