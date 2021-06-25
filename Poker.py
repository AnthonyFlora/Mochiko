#! /usr/bin/python

# EV = Sigma(P(i) * V(i))
# EV = P(W) * V(W) + P(L) * V(L)
# EV = P(W) * V(W) + 1.0 * V(L)
# EV = P(W) * V(W) + V(L)

import random

CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
CARD_SUITS = ['c', 'd', 'h', 's']


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_rank(self):
        return self.rank

    def get_suit(self):
        return self.suit


class Cards:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)

    def draw(self):
        self.cards.pop(0)

    def clear(self):
        self.cards = []

    def shuffle(self):
        random.shuffle(self.cards)


class Deck:
    def __init__(self):
        self.cards = Cards()

    def shuffle(self):
        self.cards.clear()
        for rank in CARD_RANKS:
            for suit in CARD_SUITS:
                self.cards.add(Card(rank, suit))
        self.cards.shuffle()

    def draw(self):
        self.cards.draw()


class Table:
    def __init__(self):
        self.NUM_SEATS = 10
        self.player_names = [None for x in range(self.NUM_SEATS)]
        self.player_cards = [None for x in range(self.NUM_SEATS)]
        self.player_stacks = [None for x in range(self.NUM_SEATS)]
        self.player_controllers = [None for x in range(self.NUM_SEATS)]
        self.buttons = [None for x in range(self.NUM_SEATS)]
        self.stack = [None for x in range(self.NUM_SEATS)]
        self.deck = Deck()
        self.board_cards = Cards()

    def seat_player(self, name, controller, stack, seat_idx):
        self.player_names[seat_idx] = name
        self.player_cards[seat_idx] = []
        self.player_stacks[seat_idx] = stack
        self.player_controllers[seat_idx] = controller



class Game:
    def __init__(self):
        self.table = Table()

    def register_player(self, player):

        self.active_players.append(player)

    def play_round(self):

        self.shuffle()
        self.move_buttons()
        self.take_blinds()
        self.deal_hole_cards()
        self.take_bets()
        self.deal_community_cards(3)
        self.take_bets()
        self.deal_community_cards(1)
        self.take_bets()
        self.deal_community_cards(1)
        self.take_bets()
        self.rank_hands()
        self.pay_winners()
        self.remove_busted_players()

    def shuffle(self):
        self.deck.shuffle()
        self.community_cards.clear()
        for player in self.active_players:
            player.cards.clear()
        for player in self.busted_players:
            player.cards.clear()

    def move_buttons(self):
        None

    def take_blinds(self):
        None

    def take_bets(self):
        None

    def rank_hands(self):
        None

    def pay_winners(self):
        None

    def deal_hole_cards(self):
        for player in self.active_players:
            player.cards.add(self.deck.draw())
            player.cards.add(self.deck.draw())

    def deal_community_cards(self, num_cards):
        for i in range(num_cards):
            self.community_cards.add(self.deck.draw())

    def remove_busted_players(self):
        for player in self.active_players:
            if player.stack <= 0:
                self.busted_players.append(player)
                self.active_players.remove(player)


class Player:
    def __init__(self, name, stack):
        self.name = name
        self.stack = stack
        self.invest = 0.0
        self.cards = Cards()


if __name__ == "__main__":
    game = Game()
    game.register_player(Player('p1', 1000))
    game.register_player(Player('p2', 1000))
    game.play_round()


