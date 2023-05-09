import numpy as np

from constants import ACTIONS

class Agent:
    def __init__(self, name):
        self.name = name
        self._cards = []
        self.cash = 0
        self.small_blind = None
        self.big_blind = None
        self.folded = None
        self.hand = None

    def add_card(self, card):
        self._cards.append(card)
    
    def remove_cards(self):
        self._cards.clear()

    def get_hand(self):
        # TODO: code figure getter
        pass

    def small_bet(self):
        if self.cash >= self.big_blind:
            self.cash -= self.big_blind
            bet_value = self.big_blind
        else:
            bet_value = self.cash
            self.cash = 0

        return bet_value

    def big_bet(self):
        big_bet = 2*self.big_blind
        if self.cash >= big_bet:
            self.cash -= big_bet
            bet_value = big_bet
        else:
            bet_value = self.cash
            self.cash = 0
        
        return bet_value

    def bet_small_blind(self):
        if self.cash >= self.small_blind:
            self.cash -= self.small_blind
            bet_value = self.small_blind
        else:
            bet_value = self.cash
            self.cash = 0
        return bet_value

    def bet_big_blind(self):
        if self.cash >= self.big_blind:
            self.cash -= self.big_blind
            bet_value = self.big_blind
        else:
            bet_value = self.cash
            self.cash = 0
        return bet_value

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

    def make_action(self, pot, round):
        action =  np.random.choice(ACTIONS)
        
        if action == "raise" or action == "call":
            bet_size = self.small_bet() if round in ("preflop", "flop") else self.big_bet()
            return pot + bet_size
        elif action == "check":
            pass
        elif action == "fold":
            self.folded = True
