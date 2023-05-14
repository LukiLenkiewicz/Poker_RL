import logging

from agent import Agent, RandomAgent
from deck import Deck
from hand_handler import HandHandler

from constants import NUM_PLAYER_CARDS, HANDS_HIERARCHY, ROUNDS

class Game:
    def __init__(self, num_players, starting_bankroll, small_blind):
        self.players = self._init_players(num_players)
        self.starting_bankroll = starting_bankroll
        self.small_blind = small_blind
        self.big_blind = small_blind*2
        self.num_folded_players = 0
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

            for round in ROUNDS:
                logging.info(f"  {round}")
                pot = self._make_actions(pot, game_round=round)
                cards = self.deck.give_card(round=round)
                self.public_cards += cards
                logging.info(f"pot size: {pot}")
                if self.num_folded_players == len(self.players) - 1:
                    break

            logging.info("  finding_winner")
            hand_checker.public_cards = self.public_cards
            current_hands = []
            for player in self.players:
                hand = hand_checker.check_hand(player)
                player.hand = hand
                if not player.folded:
                    current_hands.append(hand["hand"])
                logging.info(f"{player.name}: {hand['hand']}")

            strongest_hand = None
            for hand in HANDS_HIERARCHY:
                if hand in current_hands:
                    strongest_hand = hand
                
            winners = []
            logging.info("WINNERS")
            for player in self.players:
                if player.hand["hand"] == strongest_hand and not player.folded:
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
            blinds = ["small_blind", "big_blind"]
            for blind, player in zip(blinds, self.players[:2]):
                blind_bet = player.make_bet(action=blind)
                pot += blind_bet
                message = f"{player.name}: cash - {player.cash}, combined bets - {player.given_bet}, action - small blind, round bet - {self.small_blind}"
                logging.info(message)
                if blind_bet > self.min_bet:
                    self.min_bet = blind_bet

        self.num_folded_players = 0
        for player in self.players[starting_player:]:
            if not player.folded and not player.all_in:
                self.min_bet = max(map(lambda player: player.given_bet, self.players))
                pot = player.make_action(pot, game_round, self.min_bet, self.public_cards)
                if player.folded:
                    self.num_folded_players += 1
                if self.num_folded_players == len(self.players) - 1:
                    break
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
    class Something:
        def __init__(self, val):
            self.val = val

    s1 = Something(1)
    s2 = Something(2)
    s3 = Something(3)
    arr = [s1, s2, s3]

    winner = max(map(lambda x: x.val, arr))
    print(winner)