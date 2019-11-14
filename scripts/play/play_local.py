import re
import subprocess

from dlgo.agents.neural import ConstrainedPolicyAgent
from dlgo.agents.termination import PassWhenOpponentPasses, TerminationAgent
from dlgo.go import GameState, Player, Score, Move
from dlgo.utils import print_board, coords_from_point, point_from_coords


class LocalGtpBot:
    def __init__(self, go_bot, termination=None, handicap=0, opponent='gnugo', our_color='b'):
        self.bot = TerminationAgent(go_bot, termination)
        self.handicap = handicap
        self._stopped = False
        self.game_state = GameState.new_game(19, 7.5)
        self.our_color = Player.black if our_color == 'b' else Player.white
        self.their_color = self.our_color.other

        cmd = self.opponent_cmd(opponent)
        pipe = subprocess.PIPE
        self.gtp_stream = subprocess.Popen(cmd, stdin=pipe, stdout=pipe)

    @staticmethod
    def opponent_cmd(opponent):
        if opponent == 'gnugo':
            return ['gnugo', '--mode', 'gtp']
        elif opponent == 'pachi':
            return ['pachi']
        else:
            raise ValueError(f'Unknown bot name {opponent}')

    def send_command(self, cmd):
        self.gtp_stream.stdin.write(cmd.encode('utf-8'))

    def get_response(self):
        succeeded = False
        result = ''
        while not succeeded:
            line = self.gtp_stream.stdout.readline()
            if line[0] == '=':
                succeeded = True
                line = line.strip()
                result = re.sub('^= ?', '', line)
        return result

    def command_and_response(self, cmd):
        self.send_command(cmd)
        return self.get_response()

    def run(self):
        self.command_and_response('boardsize 19\n')
        self.set_handicap()
        self.play()

    def set_handicap(self):
        if self.handicap == 0:
            self.command_and_response('komi 7.5\n')
        else:
            stones = self.command_and_response(f'fixed_handicap {self.handicap}\n')
            for pos in stones.split(" "):
                move = Move.play(point_from_coords(pos))
                self.game_state = self.game_state.apply_move(move)

    def play(self):
        while not self._stopped:
            if self.game_state.next_player is self.our_color:
                self.play_our_move()
            else:
                self.play_their_move()

            print(chr(27) + '[2J')
            print_board(self.game_state.board)
            print('Estimated result: ')
            print(Score.compute(self.game_state))

    def play_our_move(self):
        move = self.bot.select_move(self.game_state)
        self.game_state = self.game_state.apply_move(move)

        our_name = self.our_color.name
        if move.is_pass:
            self.command_and_response(f'play {our_name} pass\n')
        elif move.is_resign:
            self.command_and_response(f'play {our_name} resign\n')
        else:
            pos = coords_from_point(move.point)
            self.command_and_response(f'play {our_name} {pos}\n')

    def play_their_move(self):
        their_name = self.their_color.name

        pos = self.command_and_response(f'genmove {their_name}\n')
        if pos.lower() == 'resign':
            self.game_state = self.game_state.apply_move(Move.resign())
            self._stopped = True
        elif pos.lower() == 'pass':
            self.game_state = self.game_state.apply_move(Move.pass_turn())
            if self.game_state.last_move.is_pass:
                self._stopped = True
        else:
            move = Move.play(point_from_coords(pos))
            self.game_state = self.game_state.apply_move(move)


if __name__ == '__main__':
    bot = ConstrainedPolicyAgent.load('../../data/agents/betago.hdf5')
    gnu_go = LocalGtpBot(go_bot=bot, termination=PassWhenOpponentPasses(), handicap=0, opponent='pachi')
    gnu_go.run()
