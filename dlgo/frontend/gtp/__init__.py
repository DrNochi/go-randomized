import sys

from dlgo.boards.fast import FastGameState, FastBoard
from dlgo.frontend.gtp.protocol import Command, Response
from dlgo.frontend.gtp.utils import fixed_handicap
from dlgo.frontend.utils import coords_from_point, point_from_coords, format_board
from dlgo.gotypes import Player, Move


class GTPFrontend:
    def __init__(self, agent, input_stream=sys.stdin, output_stream=sys.stdout):
        self.agent = agent

        self.board_size = 19
        self.komi = 7.5
        self.game = FastGameState.new_game(self.board_size, self.komi)

        self._input = input_stream
        self._output = output_stream
        self._running = False

        self._command_handlers = {
            'protocol_version': self._handle_protocol_version,
            'name': self._handle_name,
            'version': self._handle_version,
            'known_command': self._handle_known_command,
            'list_commands': self._handle_list_commands,
            'quit': self._handle_quit,
            'boardsize': self._handle_boardsize,
            'clear_board': self._handle_clear_board,
            'komi': self._handle_komi,
            'fixed_handicap': self._handle_fixed_handicap,
            'place_free_handicap': self._handle_place_free_handicap,
            'set_free_handicap': self._handle_set_free_handicap,
            'play': self._handle_play,
            'genmove': self._handle_genmove,
            'undo': self._handle_undo,
            'time_settings': self._handle_time_settings,
            'time_left': self._handle_time_left,
            # 'final_score': self._handle_final_score,
            # 'final_status_list': self._handle_final_status_list,
            # 'loadsgf': self._handle_loadsgf,
            # 'reg_genmove': self._handle_reg_genmove,
            'showboard': self._handle_showboard
        }

    def run(self):
        self._running = True
        while self._running:
            input_str = self._input.readline().strip()
            if input_str.startswith('#'):
                continue

            command = Command.parse(input_str)
            response = self.process_command(command)

            self._output.write(str(response) + '\n\n')
            self._output.flush()

    def process_command(self, command):
        if command.command in self._command_handlers:
            return self._command_handlers[command.command](command)
        return Response(False, command.id, 'unknown command')

    @staticmethod
    def _handle_protocol_version(command):
        return Response(True, command.id, 2)

    def _handle_name(self, command):
        return Response(True, command.id, 'DLGO ({})'.format(type(self.agent).__name__))

    @staticmethod
    def _handle_version(command):
        return Response(True, command.id, '')

    def _handle_known_command(self, command):
        return Response(True, command.id, 'true' if command.arguments[0] in self._command_handlers else 'false')

    def _handle_list_commands(self, command):
        return Response(True, command.id, '\n'.join(self._command_handlers.keys()))

    def _handle_quit(self, command):
        self._running = False
        return Response(True, command.id, '')

    def _handle_boardsize(self, command):
        self.board_size = int(command.arguments[0])
        self.game = FastGameState.new_game(self.board_size, self.komi)
        return Response(True, command.id, '')

    def _handle_clear_board(self, command):
        self.game = FastGameState.new_game(self.board_size, self.komi)
        return Response(True, command.id, '')

    def _handle_komi(self, command):
        self.komi = float(command.arguments[0])
        self.game.komi = self.komi
        return Response(True, command.id, '')

    def _handle_fixed_handicap(self, command):
        assert self.game.prev_state is None

        handicap = fixed_handicap(self.board_size, int(command.arguments[0]))

        board = FastBoard(self.board_size, self.board_size)
        for point in handicap:
            board.place_stone(Player.black, point)
        self.game = FastGameState(board, Player.white, None, None, self.komi)

        return Response(True, command.id, ' '.join([coords_from_point(point) for point in handicap]))

    def _handle_place_free_handicap(self, command):
        assert self.game.prev_state is None

        handicap = fixed_handicap(self.board_size, int(command.arguments[0]))

        board = FastBoard(self.board_size, self.board_size)
        for position in handicap:
            board.place_stone(Player.black, position)
        self.game = FastGameState(board, Player.white, None, None, self.komi)

        return Response(True, command.id, ' '.join([coords_from_point(point) for point in handicap]))

    def _handle_set_free_handicap(self, command):
        assert self.game.prev_state is None

        handicap = [point_from_coords(coords) for coords in command.arguments]

        board = FastBoard(self.board_size, self.board_size)
        for position in handicap:
            board.place_stone(Player.black, position)
        self.game = FastGameState(board, Player.white, None, None, self.komi)

        return Response(True, command.id, '')

    def _handle_play(self, command):
        player = Player.black if command.arguments[0].lower() == 'b' else Player.white
        assert self.game.next_player == player

        move_str = command.arguments[1].lower()
        if move_str == 'pass':
            move = Move.pass_turn()
        elif move_str == 'resign':
            move = Move.resign()
        else:
            move = Move.play(point_from_coords(move_str))
        assert self.game.is_valid(move)
        self.game = self.game.apply_move(move)

        return Response(True, command.id, '')

    def _handle_genmove(self, command):
        player = Player.black if command.arguments[0].lower() == 'b' else Player.white
        assert self.game.next_player == player

        move = self.agent.select_move(self.game)
        if move.is_pass:
            move_str = 'pass'
        elif move.is_resign:
            move_str = 'resign'
        else:
            move_str = coords_from_point(move.point)
        self.game = self.game.apply_move(move)

        return Response(True, command.id, move_str)

    def _handle_undo(self, command):
        assert self.game.prev_state is not None
        self.game = self.game.prev_state
        return Response(True, command.id, '')

    @staticmethod
    def _handle_time_settings(command):
        return Response(True, command.id, '')

    @staticmethod
    def _handle_time_left(command):
        return Response(True, command.id, '')

    def _handle_showboard(self, command):
        return Response(True, command.id, '\n' + format_board(self.game.board))
