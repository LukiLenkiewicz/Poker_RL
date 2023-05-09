from agent import Agent, RandomAgent
from deck import Deck

from constants import NUM_PLAYER_CARDS, NUM_FLOP_CARDS

class Game:
    def __init__(self, num_players, starting_bankroll, small_blind):
        self.players = self._init_players(num_players)
        self.starting_bankroll = starting_bankroll
        self.small_blind = small_blind
        self.big_blind = small_blind*2
        self.deck = Deck()

    def start_game(self):  # TODO: handle prohibited actions
        num_rounds = 100

        for player in self.players:
            player.small_blind = self.small_blind
            player.big_blind = self.big_blind

        for _ in range(num_rounds):
            pot = 0
            public_cards = []

            for player in self.players:
                player.folded = False
            self.shuffle_up_and_deal()

            # preflop
            pot = self._make_actions(pot, round="preflop")

            #flop
            for _ in range(NUM_FLOP_CARDS):
                card = self.deck.give_card()
                public_cards.append(card)

            pot = self._make_actions(pot, round="flop")

            #turn
            card = self.deck.give_card()
            public_cards.append(card)

            pot = self._make_actions(pot, round="turn")

            #river
            card = self.deck.give_card()
            public_cards.append(card)

            pot = self._make_actions(pot, round="river")

            #finding winner
            for player in self.players:
                pass
                
            #reset_hand
            for player in self.players:
                player.hand = None

            self._change_dealer()

    def shuffle_up_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle_deck()
        self.deal()

    def deal(self):
        for _ in range(NUM_PLAYER_CARDS):
            for player in self.players:
                card = self.deck()
                player.add_card(card)

    def _make_actions(self, pot, round="preflop"):
        starting_player = 0
        if round == "preflop":
            starting_player = 2
            pot += self.players[0].bet_small_blind()
            pot += self.players[1].bet_big_blind()

        for player in self.players[starting_player:]:
            if not player.folded:
                pot = player.make_action(pot, round)

        return pot

    def _change_dealer(self):
        self.players.append(self.players.pop())

    def _init_players(self, num_players):
        return [RandomAgent(f"player{i+1}") for i in range(num_players)]
