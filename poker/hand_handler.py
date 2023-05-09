from copy import deepcopy
from constants import SUITS, CARD_NUMS

class HandHandler:
    def __init__(self):
        self.public_cards = None

    def check_hand(self, player):
        cards = player._cards + self.public_cards

        card_counter = self.generate_card_counter()
        current_hand = {}

        for card in cards:
            card_counter[card.card_num] += 1
            card_counter[card.card_suit] += 1

        # for num in CARD_NUMS:
        #     if card_counter[num] > 0:
        #         cards["high_card"] = num

        possible_hands = [self.check_pair, self.check_two_pairs, self.check_three, self.check_straight, self.check_flush,
                          self.check_full_house, self.check_four, self.check_straight_flush]

        for check in possible_hands:
            
            hand = check(card_counter)
            if hand is not None:
                current_hand = hand

        return current_hand



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
        
        del new_card_counter[first_pair]
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
        high_card = "A"
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

    @staticmethod
    def check_flush(card_counter):
        # The highest card of the five determines the strength of the flush
        for color, count in list(card_counter.items())[:4]:
            if count >= 3:
                return {"hand": "flush", "color": color}

    def check_full_house(self, card_counter):
        tripled = self.check_three(card_counter)
        new_card_counter = deepcopy(card_counter)
        
        if not tripled:
            return None
        
        del new_card_counter[tripled]
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


    def check_straight_flush(self):
        pass


if __name__ == "__main__":
    dict_ = {1:2, 3:4}
    # [0, 1,1,1,1,1, 1] ->