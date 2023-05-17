from copy import deepcopy
from constants import SUITS, CARD_NUMS

class HandHandler:
    def __init__(self):
        self.public_cards = None

    def check_hand(self, player):
        self.cards = player._cards + self.public_cards

        card_counter = self.generate_card_counter()
        current_hand = {"hand": None}

        for card in self.cards:
            card_counter[card.card_num] += 1
            card_counter[card.suit] += 1

        possible_hands = [self.check_pair, self.check_two_pairs, self.check_three, self.check_straight, self.check_flush,
                          self.check_full_house, self.check_four, self.check_straight_flush]

        for check in possible_hands:
            
            hand = check(card_counter)
            if hand is not None:
                current_hand = hand

        return current_hand

    def compare_strongest_hands(self, players):
        winner_handler = {
            "one pair": ["first"],
            "two pairs": ["first", "second"],
            "three": ["cards"],
            "straight": ["high card"],
            "flush": ["high card"],
            "full house": ["three", "pair"],
            "four": ["cards"],
            "straight flush": []
        }
        winning_hand = players[0].hand
        
        for hand_num in winner_handler[winning_hand]:
            current_nums = set()
            for player in players:
                current_nums.add(player.hand[hand_num])
            
            current_strongest = None
            for card_num in CARD_NUMS:
                if card_num in current_nums:
                    current_strongest = card_num
            
            current_winners = []
            for player in players:
                if player.hand[card_num] == current_strongest:
                    current_winners.append(player)
            
            if len(current_winners) == 1:
                return current_winners
        
        return current_winners        


    @staticmethod
    def generate_card_counter():
        counter = {}
        for val in SUITS + CARD_NUMS:
            counter[val] = 0
        return counter

    @staticmethod
    def check_pair(card_counter):
        paired_cards = None
        for card, count in list(card_counter.items())[4:]:
            if count >= 2:
                paired_cards = card
        
        if paired_cards:
            return {"hand": "one pair", "first": paired_cards}

    def check_two_pairs(self, card_counter):
        first_pair = self.check_pair(card_counter)
        new_card_counter = deepcopy(card_counter)
        
        if not first_pair:
            return None
        
        del new_card_counter[first_pair["first"]]
        second_pair = self.check_pair(new_card_counter)

        if second_pair:
            return {"hand": "two pairs", "first": first_pair, "second": second_pair}
        
    @staticmethod
    def check_three(card_counter):
        tripled_cards = None
        for card, count in list(card_counter.items())[4:]:
            if count >= 3:
                tripled_cards = card
        
        if tripled_cards:
            return {"hand": "three", "cards": tripled_cards}


    @staticmethod
    def check_straight(card_counter):
        counter = 0 
        high_card = "2"
        best_straight = None
        for card, on_table in list(card_counter.items())[4:]:
            if on_table:
                high_card = card
                counter += 1
            else:
                counter = 0

            if counter >= 5:
                best_straight = {"hand": "straight", "high card": high_card}
            
        return best_straight

    def check_flush(self, card_counter):
        for color, count in list(card_counter.items())[:4]:
            if count >= 5:
                high_card = self.check_high_card_for_flush(color)
                return {"hand": "flush", "high_card": high_card, "color": color}
            
    def check_high_card_for_flush(self, color):
        suits_ = set()
        for card in self.cards:
            if card.suit == color:
                suits_.add(card.card_num)
        for card in CARD_NUMS:
            if card in suits_:
                high_card = card
        return high_card

    def check_full_house(self, card_counter):
        tripled = self.check_three(card_counter)
        new_card_counter = deepcopy(card_counter)
        
        if not tripled:
            return None
        
        del new_card_counter[tripled["cards"]]
        pair = self.check_pair(new_card_counter)

        if pair:
            return {"hand": "full house", "three": tripled, "pair": pair}

    @staticmethod
    def check_four(card_counter):
        four_cards = None
        for card, count in list(card_counter.items())[4:]:
            if count >= 4:
                four_cards = card
        
        if four_cards:
            return {"hand": "four", "cards": four_cards}

    def check_straight_flush(self, card_counter):
        flush = self.check_flush(card_counter)
        color_cards = []
        if flush:
            for card in self.cards:
                if card.suit == flush["color"]:
                    color_cards.append(deepcopy(card))
                    
            card_counter = self.generate_card_counter()
            for card in self.cards:
                card_counter[card.card_num] += 1
                card_counter[card.suit] += 1

            straight = self.check_straight(card_counter)
            if straight and flush:
                return {"hand": "straight flush"}
            

if __name__ == "__main__":
    class Player:
        def __init__(self, cards):
            self._cards = cards

    from card import Card
    p1 = Player([Card("A", "clovers"), Card("5", "pikes")])
    handler = HandHandler()
    handler.public_cards = [Card("6", "hearts"), Card("K", "hearts"), Card("Q", "hearts"), Card("T", "tiles")]
    result = handler.check_hand(p1)
    print(result)