import json
from datetime import date
from random import shuffle, randint
from itertools import product
from os import system


def get_input(prompt, *args):
    inp = input(prompt)
    if inp not in args:
        return get_input(prompt, *args)
    return inp


def get_int(prompt):
    inp = input(prompt)
    try:
        return int(inp)
    except ValueError:
        return get_int(prompt)


def header(words):
    return words + f"\n{'-' * len(words)}"


def color(string, color, bold=False):
    if not bold:
        return f"\033[{color}m{string}\033[0m"
    return f"\033[{color};1m{string}\033[0m"


def bold(string):
    return f"\033[1m{string}\033[0m"


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __str__(self):
        message = f"{self.suit} {self.rank}"
        if self.suit in ('♦', '♥'):
            return color(message, ANSI_COLORS["Red"])
        return message

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value}, {self.rank})"

    def __int__(self):
        return self.value


class Deck:
    def __init__(self):
        self.deck = []
        self.shuffle()

    def __str__(self):
        return f"There are {len(self.deck)} cards in the deck."

    def __repr__(self):
        return str(self.deck)

    def shuffle(self):
        self.deck = [Card(rank, suit) for rank, suit in product(RANKS, SUITS)]
        shuffle(self.deck)

    def draw(self):
        if len(self.deck) == 26:
            self.shuffle()
        return self.deck.pop(0)


class Player:
    def __init__(self, name):
        self.cards = []
        self.name = name
        self.stay = False
        with open(BANK_FILE) as f:
            registered = json.load(f)
        try:
            user = registered[name]
            self.money = user["Money"]
            if user["Last Log"] != date.isoformat(date.today()):
                self.money += 20
        except KeyError:
            self.money = 100
        self.bet = 0

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, new_money):
        self._money = new_money
        if self._money < 0:
            print(f"{self.name} has no more money!")
            self._money = 0

    def add_card(self, card):
        self.cards.append(card)

    def get_tally(self):
        return sum([int(card) for card in self.cards])

    def reset(self):
        self.cards = []
        self.stay = False

    def __str__(self):
        hand_show = ", ".join([str(card) for card in self.cards])
        total = self.get_tally()
        if total > 21:
            total = color(total, ANSI_COLORS["Red"], True)
        elif total == 21:
            total = color(total, ANSI_COLORS["Green"], True)
        else:
            total = bold(total)
        return hand_show + f" --- Sum is {total}"


class Blackjack:
    def __init__(self):
        player_num = get_int("How many human players are playing? Max 6. ") + 1
        if player_num > 6:
            player_num = 6
        print()
        self.players = [Player(input(f"Enter name {i}: ")) for i in range(1, player_num)]
        player_names = [player.name for player in self.players]
        if len(player_names) > len(set(player_names)):
            raise NameError("Cannot have two users of the same name")
        system("clear")
        self.deck = Deck()

    @staticmethod
    def handle_ace(total):
        if total >= 11:
            return 1
        return 11

    @staticmethod
    def handle_player_ace():
        val = int(get_input("You got an ace! 1 or 11? ", "1", "11"))
        print()
        return val

    @staticmethod
    def check_win(player_sum, dealer_sum):
        win = player_sum > dealer_sum
        if player_sum == -1:
            win = False
        elif dealer_sum == player_sum:
            return "T"
        elif dealer_sum > 21:
            win = True
        if not win:
            return "L"
        else:
            return "W"

    def handle_win(self, player, result):
        if result == "W":
            message = f"{player.name} wins!"
            if BETTING:
                if player.get_tally() == 21:
                    player.money += int(player.bet + player.bet/2)
                else:
                    player.money += player.bet
        elif result == "L":
            message = f"{player.name} loses..."
            if BETTING:
                player.money -= player.bet
        else:
            message = f"{player.name} ties."
        printing = [f"Total: {player.get_tally()}"]
        if BETTING:
            money = color(f"${player.money}", ANSI_COLORS["Green"])
            printing.append(f"Money: {money}")
        print(message, *printing, sep=" --- ")
        player.bet = 0

    def compute_dealer(self, first_card):
        total = int(first_card)
        while total < 17:
            card_add = int(self.deck.draw())
            if card_add == 11:
                card_add = self.handle_ace(total)
            total += card_add
        return total

    def deal_initial(self):
        for player in self.players:
            for _ in range(2):
                player.add_card(self.deck.draw())

    @staticmethod
    def cheat(player):
        cheat_fail = randint(0, 2)
        if not cheat_fail:
            print("\nYou cheated successfully!")
            cheat_val = get_int("What value from 2-11 do you want to add to your hand?\n")
            if cheat_val > 11:
                cheat_val = 11
            elif cheat_val < 2:
                cheat_val = 2
            rank = RANKS[VALUES.index(cheat_val)]
            player.add_card(Card(rank, "?"))
        else:
            print("\nUnsuccessful cheat attempt... subtracting 30 dollars!")
            player.money -= 30

    def player_turn(self, player):
        print(header(f"\n{player.name}'s hand"))
        print(player)
        if BETTING:
            money = color(f"${player.money}", ANSI_COLORS["Green"])
            print(f"{player.name}'s money is {money}")
        inp = get_input("Do you want to hit or stay? h to hit, s to stay\n",
                        "h", "s", "cheat")

        if inp == "h":
            card = self.deck.draw()
            print(f"\nYou drew a {card}!\n")
            if int(card) == 11:
                card.value = self.handle_player_ace()
            player.add_card(card)
            print(header("Your new hand"))
            print(player)
            input("\nEnter anything to proceed: ")
            tally = player.get_tally()
            if tally > 21:
                player.stay = True
                return -1
            if tally == 21:
                player.stay = True

        elif inp == "cheat":
            self.cheat(player)
            input("\nEnter anything to proceed: ")

        else:
            player.stay = True
        return player.get_tally()

    def round(self):
        self.deal_initial()
        dealer_first = self.deck.draw()
        dealer_sum = self.compute_dealer(dealer_first)
        if BETTING:
            for player in self.players:
                player.bet = get_int(f"How much does {player.name} want to bet?\n")
                print()
                if player.bet > player.money:
                    player.bet = player.money
            system("clear")
        results = {}
        while any([not player.stay for player in self.players]):
            for index, player in enumerate(self.players):
                if not player.stay:
                    message = f"\nDealer's first card is: {dealer_first}"
                    if not index:
                        # Prevents empty newline on first turn of the game
                        message = message.lstrip()
                    print(message)
                    print(str(self.deck) + "\n")
                    result = self.player_turn(player)
                    if player.stay:
                        results[player] = result
                    system("clear")
                    if len(self.players) != 1:
                        input("Enter anything to proceed: ")
        system("clear")
        print(header("Results"))
        print(f"Dealer sum is {bold(dealer_sum)}\n")
        for player in self.players:
            result = self.check_win(results[player], dealer_sum)
            self.handle_win(player, result)
        print()

    def update_bank(self):
        with open(BANK_FILE) as f:
            current_bank = json.load(f)
        with open(BANK_FILE, "w") as f:
            for player in self.players:
                current_bank[player.name] = {"Money": player.money,
                                             "Last Log": date.isoformat(date.today())}
            json.dump(current_bank, f, indent=4)

    def main(self):
        while self.players:
            self.round()
            new_players = []
            for player in self.players:
                if player.money >= 0:
                    again = get_input(f"Does {player.name} want to play again? y/n\n",
                                      "y", "n")
                    if again == "y":
                        new_players.append(player)
                    player.reset()
            if BETTING:
                self.update_bank()
            self.players = new_players
            if self.players:
                system("clear")


if __name__ == "__main__":
    RANKS = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
             'Ten', 'Jack', 'Queen', 'King', 'Ace')
    SUITS = ('♣', '♦', '♥', '♠')
    VALUES = (2,  3,  4,  5,  6,  7,  8,  9,  10,  10,  10,  10,  11)
    RANK_VALUES = dict(zip(RANKS, VALUES))
    ANSI_COLORS = {"Red": "91", "Green": "92"}
    BANK_FILE = ".banking.json"

    if get_input("Do you want to enable betting? y/n\n", "y", "n") == "y":
        BETTING = True
    else:
        BETTING = False

    system("clear")
    Blackjack().main()

