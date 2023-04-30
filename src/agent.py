import numpy as np

from constants import ACTIONS

class Agent:
    def __init__(self, name):
        self.name = name
        self._cards = []
        self.cash = 0

    def add_card(self, card):
        self._cards.append(card)
    
    def remove_cards(self):
        self._cards.clear()

    def get_hand(self):
        # TODO: code figure getter
        pass

    def make_action(self):
        pass

    def _raise(self):
        pass

    def _check(self):
        pass
    
    def _call(self):
        pass

    def _fold(self):
        pass


class RandomAgent(Agent):
    def __init__(self, name="player"):
        super().__init__(name=name)

    def make_action(self):
        action = np.random.choice(ACTIONS)
        