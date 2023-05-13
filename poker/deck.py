import numpy as np

from card import Card
from constants import CARD_NUMS, SUITS, NUM_FLOP_CARDS

class Deck():
    def __init__(self):
        self.deck = self._init_deck()

    def _init_deck(self):
        deck = []
        for num in CARD_NUMS:
            for suit in SUITS:
                card = Card(num, suit)
                deck.append(card)

        return deck

    def give_card(self, round=None):
        cards = []
        if round=="flop":
            for _ in range(NUM_FLOP_CARDS-1):
               card = self.deck.pop()
               cards.append(card)
        card = self.deck.pop()
        cards.append(card)
        return cards

    def shuffle_deck(self):
        np.random.shuffle(self.deck)

    def __str__(self):
        return str([str(card) for card in self.deck])
