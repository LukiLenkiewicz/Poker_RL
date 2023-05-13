import logging
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
        self.all_in = False
        self.given_bet = 0
        self.hand = {"hand": None}

    def add_card(self, card):
        self._cards += card
    
    def remove_cards(self):
        self._cards.clear()

    def small_bet(self):
        if self.cash >= self.big_blind:
            self.cash -= self.big_blind
            bet_value = self.big_blind
        else:
            bet_value = self.cash
            self.cash = 0
            self.all_in = True

        return bet_value

    def big_bet(self):
        big_bet = 2*self.big_blind
        if self.cash >= big_bet:
            self.cash -= big_bet
            bet_value = big_bet
        else:
            bet_value = self.cash
            self.cash = 0
            self.all_in = True
        
        return bet_value
    
    def make_bet(self, action="call", bet=None):
        if action == "call":
            extra_bet = bet - self.given_bet
        elif action == "big_blind":
            extra_bet = self.big_blind
        elif action == "small_blind":
            extra_bet = self.small_blind

        if self.cash >= extra_bet:
            self.cash -= extra_bet
            bet_value = extra_bet
        else:
            bet_value = self.cash
            self.cash = 0
            self.all_in = True
        self.given_bet += bet_value
        return bet_value
    
    def get_allowed_actions(self, bet):
        allowed_actions = ACTIONS.copy()
        if bet > self.given_bet:
            allowed_actions.remove("check")
        if bet > self.given_bet + self.cash:
            allowed_actions.remove("raise")

        return allowed_actions

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

    def make_action(self, pot, round, min_bet=0, *args):
        allowed_actions = self.get_allowed_actions(min_bet)
        action =  np.random.choice(allowed_actions)
        
        if action == "call":
            bet_size = self.make_bet(action=action, bet=min_bet)
            message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - {bet_size}"
            logging.info(message)
            return pot + bet_size
        elif action == "raise":
            if min_bet > self.given_bet:
                bet_size = self.make_bet(action="call", bet=min_bet)
                pot += bet_size
            bet_size = self.small_bet() if round in ("preflop", "flop") else self.big_bet()
            message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - {bet_size}"
            logging.info(message)
            return pot + bet_size
        elif action == "check":
            message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - {0}"
            logging.info(message)
            return pot
        elif action == "fold":
            self.folded = True
            message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - FOLDED"
            logging.info(message)
            return pot


if __name__ == "__main__":
    pass
