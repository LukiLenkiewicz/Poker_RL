import logging

from agent import Agent, RandomAgent, QAgent
from deck import Deck
from hand_handler import HandHandler

from constants import NUM_PLAYER_CARDS, HANDS_HIERARCHY, ROUNDS

class Game:
    def __init__(self, num_players, starting_bankroll, small_blind, num_deals=3, q_agent=False):
        self.players = self._init_players(num_players, q_agent=q_agent)
        self.starting_bankroll = starting_bankroll
        self.small_blind = small_blind
        self.big_blind = small_blind*2
        self.num_folded_players = 0
        self.num_deals = num_deals
        self.deck = Deck()

        logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w", format="%(message)s")

    def start_game(self):
        self.hand_checker = HandHandler()

        for player in self.players:
            player.small_blind = self.small_blind
            player.big_blind = self.big_blind
            player.cash = self.starting_bankroll

        for deal_num in range(self.num_deals):
            for player in self.players:
                if isinstance(player, QAgent):
                    player.prev_cash = player.cash
                    player.prev_round = None
                    player.prev_hand = {"hand": None}

            pot = self.prepare_new_deal(deal_num)

            for round in ROUNDS:
                pot, quit = self._play_round(round, pot, deal_num)
                if quit:
                    break

            winners = self._get_round_winners()         

            prize = pot//len(winners)

            for winner in winners:
                logging.info(f"-{winner.name}")
                winner.cash += prize

            self._evaluate_last_decisions(round, self.public_cards, deal_num)

            #reset_hand and bets
            for player in self.players:
                player._cards = []
                player.hand = {"hand": None}
                player.given_bet = 0

            self._delete_losers()
            self._change_dealer()

    def prepare_new_deal(self, num_deal):
        message = f"###### Round no. {num_deal+1} #######"
        logging.info("##########################")
        logging.info(message)
        logging.info("##########################")
        pot = 0
        self.public_cards = []
        self.min_bet = 0

        for player in self.players:
            player.folded = False
            player.all_in = False

        self.shuffle_up_and_deal()

        logging.info("##### PLAYER CARDS #######")
        for player in self.players:
            logging.info(f"-{player.name}; {player._cards[0]}\t{player._cards[1]}")

        self.num_folded_players = 0

        return pot

    def shuffle_up_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle_deck()
        self.deal()

    def deal(self):
        for _ in range(NUM_PLAYER_CARDS):
            for player in self.players:
                card = self.deck.give_card()
                player.add_card(card)

    def _play_round(self, round, pot, deal_num):
        logging.info(f"  {round}")

        for player in self.players:
            player.num_raises = 0

        self._evaluate_last_decisions(round, self.public_cards, deal_num)
        pot = self._make_actions(pot, game_round=round, beginning=True)
        cards = self.deck.give_card(round=round)
        self.public_cards += cards
        logging.info(f"pot size: {pot}")
        while self._non_equal_bets():
            self._evaluate_last_decisions(round, self.public_cards, deal_num)
            pot = self._make_actions(pot, game_round=round, beginning=False)
        if self.num_folded_players == len(self.players) - 1:
            return pot, True

        return pot, False
    
    def _get_round_winners(self):

        logging.info("########### finding_winner ##########")
        strongest_hand = self._get_strongest_hand()

        strongest_hand_players = []
        logging.info("------getting strongest hands------")
        for player in self.players:
            if player.hand["hand"] == strongest_hand and not player.folded:
                strongest_hand_players.append(player)
                logging.info(f" -{player.name}")

        logging.info("------printing cards----------")
        cards = [str(card) for card in self.public_cards]
        logging.info("\t".join(cards))
        logging.info("------finding winners----------")
        if len(strongest_hand_players) > 1:
            winners = self.hand_checker.compare_strongest_hands(strongest_hand_players)
        else:
            winners = strongest_hand_players            

        return winners
    
    def _get_strongest_hand(self):
        self.hand_checker.public_cards = self.public_cards
        current_hands = []
        for player in self.players:
            hand = self.hand_checker.check_hand(player)
            player.hand = hand
            if not player.folded:
                current_hands.append(hand["hand"])
            logging.info(f"{player.name}: {hand['hand']}")

        strongest_hand = None
        for hand in HANDS_HIERARCHY:
            if hand in current_hands:
                strongest_hand = hand

        logging.info("------STRONGEST HAND------")
        logging.info(f"{strongest_hand}")

        return strongest_hand

    def _make_actions(self, pot, game_round="preflop", beginning=False):
        starting_player = 0
        if game_round == "preflop" and beginning:
            starting_player = 2
            blinds = ["small_blind", "big_blind"]
            for blind, player in zip(blinds, self.players[:2]):
                blind_bet = player.make_bet(action=blind)
                pot += blind_bet
                message = f"{player.name}: cash - {player.cash}, combined bets - {player.given_bet}, action - {blind}, round bet - {eval(f'self.'+f'{blind}')}"
                logging.info(message)
                if blind_bet > self.min_bet:
                    self.min_bet = blind_bet

        for player in self.players[starting_player:]:
            if self.num_folded_players == len(self.players) - 1:
                logging.info("one player left")
                break
            if not player.folded and not player.all_in:
                self.min_bet = max(map(lambda player: player.given_bet, self.players))
                pot = player.make_action(pot, game_round, self.min_bet, self.public_cards)
                if player.folded:
                    self.num_folded_players += 1
        return pot

    def _change_dealer(self):
        self.players = self.players[1:] + self.players[:1]

    def _init_players(self, num_players, q_agent=False):
        if q_agent:
            players = [RandomAgent(f"player{i+1}") for i in range(num_players-1)]
            self.q_agent = QAgent(f"player{num_players}", train=False)
            players.append(self.q_agent)
            return players
        return [RandomAgent(f"player{i+1}") for i in range(num_players)]
    
    def _delete_losers(self):
        i = 0
        while i < len(self.players):
            if self.players[i].cash == 0:
                del self.players[i]
            else:
                i += 1

    def _non_equal_bets(self):
        if self.num_folded_players == len(self.players) - 1:
            return False

        for player in self.players:
            if player.given_bet != self.min_bet and not player.all_in and not player.folded:
                return True
            
        return False

    def _evaluate_last_decisions(self, round, public_cards, deal_num):
        for player in self.players:
            if isinstance(player, QAgent):
                player.evaluate_last_decision(round, public_cards, deal_num)

if __name__ == "__main__":
    class Something:
        def __init__(self, folded):
            self.folded = folded

    s1 = Something(False)
    s2 = Something(True)
    s3 = Something(True)
    arr = [1,2,3]

    print(arr[0:])
