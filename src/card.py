class Card:
    def __init__(self, card_num, suit):
        self.card_num = card_num
        self.suit = suit

    def __str__(self):
        return f"{self.card_num}_{self.suit}"
