from .actions import FoldAction, CallAction, CheckAction, RaiseAction
from collections import namedtuple

'''
Encapsulates game and round state information for the player.
'''

GameState = namedtuple('GameState', ['bankroll', 'game_clock', 'round_num'])
TerminalState = namedtuple('TerminalState', ['deltas', 'previous_state'])

ROUNDS = 1000
STARTING_STACK = 400
BIG_BLIND = 2
SMALL_BLIND = 1


class RoundState():

    def __init__(self, button, street, pips, stacks, hands, deck, previous_state):
        self.button = button
        self.street = street
        self.pips = pips
        self.stacks = stacks
        self.hands = hands
        # first five deck cards are the board
        self.deck = deck
        self.previous_state = previous_state

    def showdown(self):
        return TerminalState([0, 0], self)

    def legal_actions(self):
        active = self.button % 2
        continue_cost = self.pips[1-active] - self.pips[active]
        if continue_cost == 0:
            # we can only raise the stakes if both players can afford it
            bets_forbidden = (self.stacks[0] == 0 or self.stacks[1] == 0)
            return {CheckAction} if bets_forbidden else {CheckAction, RaiseAction}
        else:  # continue_cost > 0
            # similarly, re-raising is only allowed if both players can afford it
            raises_forbidden = (continue_cost == self.stacks[active] or self.stacks[1-active] == 0)
            return {FoldAction, CallAction} if raises_forbidden else {FoldAction, CallAction, RaiseAction}

    def raise_bounds(self):
        active = self.button % 2
        continue_cost = self.pips[1-active] - self.pips[active]
        max_contribution = min(self.stacks[active], self.stacks[1-active] + continue_cost)
        min_contribution = min(max_contribution, self.pips[1-active] + max(continue_cost, BIG_BLIND))
        return (self.pips[active] + min_contribution, self.pips[active] + max_contribution)

    def proceed_street(self):
        if self.street == 5:
            return self.showdown()
        else:
            new_street = 3 if self.street == 0 else self.street + 1
            return RoundState(1, new_street, [0, 0], self.stacks, self.hands, self.deck, self)

    def proceed(self, action):
        active = self.button % 2
        if isinstance(action, FoldAction):
            delta = self.stacks[0] - STARTING_STACK if active == 0 else STARTING_STACK - self.stacks[1]
            return TerminalState([delta, -delta], self)
        elif isinstance(action, CallAction):
            if self.button == 0:  # sb calls bb
                return RoundState(1, 0, [BIG_BLIND] * 2, [STARTING_STACK-BIG_BLIND] * 2, self.hands, self.deck, self)
            else:  # both players acted
                new_pips = list(self.pips)
                new_stacks = list(self.stacks)
                contribution = new_pips[1-active] - new_pips[active]
                new_stacks[active] -= contribution
                new_pips[active] += contribution
                state = RoundState(self.button + 1, self.street, new_pips, new_stacks, self.hands, self.deck, self)
                return state.proceed_street()
        elif isinstance(action, CheckAction):
            if (self.street == 0 and self.button > 0) or self.button > 1:  # both players acted
                return self.proceed_street()
            else:  # let opponent act
                return RoundState(self.button + 1, self.street, self.pips, self.stacks, self.hands, self.deck, self)
        else:  # isinstance(action, RaiseAction)
            new_pips = list(self.pips)
            new_stacks = list(self.stacks)
            contribution = action.amount - new_pips[active]
            new_stacks[active] -= contribution
            new_pips[active] += contribution
            return RoundState(self.button + 1, self.street, new_pips, new_stacks, self.hands, self.deck, self)