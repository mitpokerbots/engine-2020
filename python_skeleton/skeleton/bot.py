'''
This file contains the base class that you should implement for your pokerbot.
'''


class Bot():

    def handle_new_round(self, game_state, round_state, active):
        raise NotImplemented('handle_new_round')

    def handle_round_over(self, game_state, terminal_state, active):
        raise NotImplemented('handle_round_over')

    def get_action(self, game_state, round_state, active):
        raise NotImplemented('get_action')