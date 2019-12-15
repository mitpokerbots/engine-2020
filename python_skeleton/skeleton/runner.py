from .actions import FoldAction, CallAction, CheckAction, RaiseAction
from .states import GameState, TerminalState, RoundState, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from .bot import Bot
import argparse
import socket

'''
This file contains the infrastructure for interacting with the engine.
'''


class Runner():

    def __init__(self, pokerbot, socketfile):
        self.pokerbot = pokerbot
        self.socketfile = socketfile

    def receive(self):
        while True:
            packet = self.socketfile.readline().strip().split(' ')
            if not packet:
                break
            yield packet

    def send(self, action):
        if isinstance(action, FoldAction):
            code = 'F'
        elif isinstance(action, CallAction):
            code = 'C'
        elif isinstance(action, CheckAction):
            code = 'K'
        else:  # isinstance(action, RaiseAction)
            code = 'R' + str(action.amount)
        self.socketfile.write(code+'\n')
        self.socketfile.flush()

    def run(self):
        game_state = GameState(0, '0.', 1)
        round_state = None
        active = 0
        game_flag = True
        round_flag = True
        for packet in self.receive():
            for clause in packet:
                if clause[0] == 'T':
                    game_state = GameState(game_state.bankroll, float(clause[1:]), game_state.round_num)
                    if game_flag:
                        self.pokerbot.handle_new_game(game_state)
                        game_flag = False
                elif clause[0] == 'P':
                    active = int(clause[1])
                elif clause[0] == 'H':
                    hands = [[], []]
                    hands[active] = clause[1:].split(',')
                    pips = [SMALL_BLIND, BIG_BLIND]
                    stacks = [STARTING_STACK-SMALL_BLIND, STARTING_STACK-BIG_BLIND]
                    round_state = RoundState(0, 0, pips, stacks, hands, [], None)
                    if round_flag:
                        round_state_copy = RoundState(0, 0, list(pips), list(stacks), list(hands), [], None)
                        self.pokerbot.handle_new_round(game_state, round_state_copy, active)
                        round_flag = False
                elif clause[0] == 'F':
                    round_state = round_state.proceed(FoldAction())
                elif clause[0] == 'C':
                    round_state = round_state.proceed(CallAction())
                elif clause[0] == 'K':
                    round_state = round_state.proceed(CheckAction())
                elif clause[0] == 'R':
                    round_state = round_state.proceed(RaiseAction(int(clause[1:])))
                elif clause[0] == 'B':
                    del round_state.deck[:]
                    round_state.deck.extend(clause[1:].split(','))
                elif clause[0] == 'O':
                    round_state.previous_state.hands[1-active].extend(clause[1:].split(','))
                elif clause[0] == 'D':
                    assert(isinstance(round_state, TerminalState))
                    delta = int(clause[1:])
                    deltas = [-delta, -delta]
                    deltas[active] = delta
                    round_state = TerminalState(deltas, round_state.previous_state)
                    game_state = GameState(game_state.bankroll+delta, game_state.game_clock, game_state.round_num)
                    self.pokerbot.handle_round_over(game_state, round_state, active)
                    game_state = GameState(game_state.bankroll, game_state.game_clock, game_state.round_num+1)
                    round_flag = True
                elif clause[0] == 'Q':
                    return
            if round_flag:  # ack the engine
                self.send(CheckAction())
            else:
                assert(active == round_state.button % 2)
                action = self.pokerbot.get_action(game_state, round_state, active)
                self.send(action)


def parse_args():
    parser = argparse.ArgumentParser(prog='python3 player.py')
    parser.add_argument('--host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', type=int, help='Port on host to connect to')
    return parser.parse_args()

def run_bot(pokerbot, args):
    assert(isinstance(pokerbot, Bot))
    try:
        sock = socket.create_connection((args.host, args.port))
    except OSError:
        print('Error connecting to {}:{}, aborting'.format(args.host, args.port))
        exit()
    socketfile = sock.makefile('rw')
    runner = Runner(pokerbot, socketfile)
    runner.run()
    socketfile.close()