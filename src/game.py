from agent import Agent, RandomAgent
from deck import Deck

from constants import NUM_CARDS


class Game:
    def __init__(self, num_players, starting_bankroll, small_blind):
        self.players = self._init_players(num_players)
        self.starting_bankroll = starting_bankroll
        self.small_blind = small_blind
        self.deck = Deck()

    def start_game(self):
        num_rounds = 100

        for _ in range(num_rounds):
            self.shuffle_up_and_deal()

            # game

            self._change_dealer()

    def shuffle_up_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle_deck()
        self.deal()

    def deal(self):
        for _ in range(NUM_CARDS):
            for player in self.players:
                card = self.deck()
                player.add_card(card)

    def _change_dealer(self):
        self.players.append(self.players.pop())

    def _init_players(self, num_players):
        return [RandomAgent(f"player{i+1}") for i in range(num_players)]
