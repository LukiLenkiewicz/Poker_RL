import numpy as np

from card import Card
from constants import CARD_NUMS, SUITS

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
    
    def __str__(self):
        return str([str(card) for card in self.deck])
    
    def shuffle_deck(self):
        np.random.shuffle(self.deck)
