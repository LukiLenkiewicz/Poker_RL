import logging
import numpy as np

from hand_handler import HandHandler
from constants import ROUNDS, ACTIONS, HANDS_HIERARCHY

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
        self.num_raises = 0

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
        self.given_bet += bet_value
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
        self.given_bet += bet_value
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
        if bet > self.given_bet + self.cash or self.num_raises == 3:
            allowed_actions.remove("raise")

        return allowed_actions

    def make_action(self):
        pass


class RandomAgent(Agent):
    def __init__(self, name="player"):
        super().__init__(name=name)

    def make_action(self, pot, round, min_bet=0, public_cards=[]):
        allowed_actions = self.get_allowed_actions(min_bet)
        action =  np.random.choice(allowed_actions)
        
        if action == "call":
            bet_size = self.make_bet(action=action, bet=min_bet)
        elif action == "raise":
            if min_bet > self.given_bet:
                bet_size = self.make_bet(action="call", bet=min_bet)
                pot += bet_size
            self.num_raises += 1
            bet_size = self.small_bet() if round in ("preflop", "flop") else self.big_bet()
        elif action == "check":
            bet_size = 0
        elif action == "fold":
            bet_size = 0
            self.folded = True

        message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - {bet_size}"
        logging.info(message)
        return pot + bet_size


class QAgent(Agent):
    def __init__(self, name, train=True):
        super().__init__(name=name)
        self.Q_values = self._generate_q_table()

        self.prev_cash = 0
        self.prev_round = None
        self.prev_hand = {"hand": None}
        self.prev_action = None
        self.last_allowed_actions = []

        self.alpha0 = 0.05
        self.decay = 0.005
        self.gamma = 0.9

        self.hand_handler = HandHandler()
        self.train = train

    def make_action(self, pot, round, min_bet=0, public_cards=[]):
        self.prev_cash = self.cash
        allowed_actions = self.get_allowed_actions(min_bet)
        self.last_allowed_actions = allowed_actions

        if self.train:
            action =  np.random.choice(allowed_actions)
            self.prev_action = action
        else:
            action =  self._make_decision(allowed_actions, round, public_cards)
            self.prev_action = action

        if action == "call":
            bet_size = self.make_bet(action=action, bet=min_bet)
        elif action == "raise":
            if min_bet > self.given_bet:
                bet_size = self.make_bet(action="call", bet=min_bet)
                pot += bet_size
            self.num_raises += 1
            bet_size = self.small_bet() if round in ("preflop", "flop") else self.big_bet()
        elif action == "check":
            bet_size = 0
        elif action == "fold":
            bet_size = 0
            self.folded = True

        message = f"{self.name}: cash - {self.cash}, combined bets - {self.given_bet}, action - {action}, round bet - {bet_size}"
        logging.info(message)
        return pot + bet_size

    def _make_decision(self, allowed_actions, round, public_cards):
        self.hand_handler.public_cards = public_cards
        current_hand = self.hand_handler.check_hand(self)
        possible_decisions = self.Q_values[round][current_hand["hand"]]
        action_choice = {action: possible_decisions[action]  for action in allowed_actions}
        action = max(action_choice, key=lambda k: action_choice[k])

        return action
    
    def evaluate_last_decision(self, round, public_cards, num_iter):
        if self.prev_round is not None:
            self.hand_handler.public_cards = public_cards
            reward = self.cash - self.prev_cash
            current_hand = self.hand_handler.check_hand(self)
            current_state = self.Q_values[self.prev_round][self.prev_hand["hand"]]
            current_state_allowed = {action: current_state[action]  for action in current_state}
            next_value = max(current_state_allowed, key=lambda k: current_state_allowed[k])
            next_value =current_state_allowed[next_value]
            alpha = self.alpha0/(1+num_iter*self.decay)
            self.Q_values[round][current_hand["hand"]][self.prev_action] *= (1 - alpha)
            self.Q_values[round][current_hand["hand"]][self.prev_action] += alpha*(reward + self.gamma*next_value)

            self.prev_hand = current_hand
            self.prev_cash = self.cash

        # save for fututure evaluation
        self.prev_round = round

    @staticmethod
    def _generate_q_table():
        table = {}
        
        for round in ROUNDS:
            table[round] = {}
            for hand in HANDS_HIERARCHY:
                # table[round][hand] = [0. for _ in range(len(ACTIONS))]
                table[round][hand] = {action: 0. for action in ACTIONS}

        return table
