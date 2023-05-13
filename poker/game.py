import logging

from agent import Agent, RandomAgent
from deck import Deck
from hand_handler import HandHandler

from constants import NUM_PLAYER_CARDS, NUM_FLOP_CARDS, HANDS_HIERARCHY, ROUNDS

class Game:
    def __init__(self, num_players, starting_bankroll, small_blind):
        self.players = self._init_players(num_players)
        self.starting_bankroll = starting_bankroll
        self.small_blind = small_blind
        self.big_blind = small_blind*2
        self.deck = Deck()

        logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w", format="%(message)s")

    def start_game(self):
        num_rounds = 3
        hand_checker = HandHandler()

        for player in self.players:
            player.small_blind = self.small_blind
            player.big_blind = self.big_blind
            player.cash = self.starting_bankroll

        for round in range(num_rounds):
            message = f"   round no. {round+1}"
            logging.info(message)
            pot = 0
            self.public_cards = []
            self.min_bet = 0

            for player in self.players:
                player.folded = False
                player.all_in = False

            self.shuffle_up_and_deal()

            # for round in ROUNDS:
            #     logging.info(f"  {round}")
            #     pot = self._make_actions(pot, game_round=round)

            logging.info("  preflop")
            pot = self._make_actions(pot, game_round="preflop")

            logging.info("  flop")
            cards = self.deck.give_card(round="flop")
            self.public_cards += cards

            pot = self._make_actions(pot, game_round="flop")
            logging.info(f"pot size: {pot}")


            logging.info("  turn")
            card = self.deck.give_card()
            self.public_cards += card

            pot = self._make_actions(pot, game_round="turn")
            logging.info(f"pot size: {pot}")


            logging.info("  river")
            card = self.deck.give_card()
            self.public_cards += card

            pot = self._make_actions(pot, game_round="river")
            logging.info(f"pot size: {pot}")


            logging.info("  finding_winner")
            hand_checker.public_cards = self.public_cards
            current_hands = []
            for player in self.players:
                hand = hand_checker.check_hand(player)
                player.hand = hand
                logging.info(f"{player.name}: {hand['hand']}")
                current_hands.append(hand["hand"])

            strongest_hand = None
            for hand in HANDS_HIERARCHY:
                if hand in current_hands:
                    strongest_hand = hand
                
            winners = []
            logging.info("WINNERS")
            for player in self.players:
                if player.hand["hand"] == strongest_hand:
                    winners.append(player)
                    logging.info(f" -{player.name}")
            
            prize = pot//len(winners)

            for winner in winners:
                winner.cash += prize

            #reset_hand and bets
            for player in self.players:
                player.hand = {"hand": None}

            self._delete_losers()
            self._change_dealer()

    def shuffle_up_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle_deck()
        self.deal()

    def deal(self):
        for _ in range(NUM_PLAYER_CARDS):
            for player in self.players:
                card = self.deck.give_card()
                player.add_card(card)

    def _make_actions(self, pot, game_round="preflop"):
        starting_player = 0
        if game_round == "preflop":
            starting_player = 2

            player = self.players[0]
            message = f"{player.name}: cash - {player.cash}, combined bets - {player.given_bet}, action - small blind, round bet - {0}"
            logging.info(message)

            small_blind = player.make_bet(action="small_blind")
            pot += small_blind
            self.min_bet = small_blind 

            player = self.players[1]
            message = f"{player.name}: cash - {player.cash}, combined bets - {player.given_bet}, action - big blind, round bet - {0}"
            logging.info(message)

            big_blind = player.make_bet(action="small_blind")
            pot += big_blind
            if big_blind > self.min_bet:
                self.min_bet = big_blind

        for player in self.players[starting_player:]:
            if not player.folded and not player.all_in:
                pot = player.make_action(pot, game_round, self.min_bet, self.public_cards)
        return pot

    def _change_dealer(self):
        self.players = self.players[1:] + self.players[:1]

    def _init_players(self, num_players):
        return [RandomAgent(f"player{i+1}") for i in range(num_players)]
    
    def _delete_losers(self):
        i = 0
        while i < len(self.players):
            if self.players[i].cash == 0:
                del self.players[i]
            else:
                i += 1


if __name__ == "__main__":
    arr = [1,2,3]

    arr += 4

    print(arr)
