import os

from flask import Flask, request, jsonify

from dlgo.boards.fast import FastGameState
from dlgo.frontend.utils import point_from_coords, coords_from_point
from dlgo.gotypes import Move


def get_web_app(bots):
    package_path = os.path.dirname(__file__)
    static_path = os.path.join(package_path, 'static')
    app = Flask(__name__, static_folder=static_path, static_url_path='/static')

    @app.route('/select-move/<bot_name>', methods=['POST'])
    def select_move(bot_name):
        content = request.json
        board_size = content['board_size']

        game = FastGameState.new_game(board_size, komi=7.5)

        for move_str in content['moves']:
            if move_str == 'pass':
                move = Move.pass_turn()
            elif move_str == 'resign':
                move = Move.resign()
            else:
                move = Move.play(point_from_coords(move_str))
            game = game.apply_move(move)

        bot = bots[bot_name]
        move = bot.select_move(game)

        if move.is_pass:
            move_str = 'pass'
        elif move.is_resign:
            move_str = 'resign'
        else:
            move_str = coords_from_point(move.point)

        return jsonify({
            'move': move_str,
            # 'diagnostics': bot.diagnostics()
        })

    return app
