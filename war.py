from enum import Enum
from random import shuffle
from collections import deque
import os
from flask import Flask
import argparse


import mysql.connector


app = Flask(__name__)

MAX_TURNS = 5000     # limiting based on https://boardgames.stackexchange.com/questions/44275/what-is-the-expected-duration-of-a-game-of-war#:~:text=This%20makes%20an%20average%20step,player%20is%20low%20on%20cards.

@app.route("/run-game")
def run_war():
    war = War()
    resp = war.play_game()

    mydb = mysql.connector.connect(
    host="localhost",
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PWD'),
    database="war"
    )
    mycursor = mydb.cursor()

    mycursor.execute('SELECT wins FROM results WHERE player="player' + str(resp[0]) + '"')

    query_result = mycursor.fetchone()

    sql = 'UPDATE results SET wins = ' + str(query_result[0] + 1) + ' WHERE player = "player'+str(resp[0]) +'"'

    mycursor.execute(sql)

    mydb.commit()

    return {"winner" : resp[0], "turns" : resp[1]}

@app.route("/game-history")
def war_history():

    mydb = mysql.connector.connect(
    host="localhost",
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PWD'),
    database="war"
    )
    mycursor = mydb.cursor()

    mycursor.execute('SELECT * FROM results')

    query_result = mycursor.fetchall()

    return {query_result[0][0] : query_result[0][1], query_result[1][0] : query_result[1][1]}

def clear_db():
    mydb = mysql.connector.connect(
    host="localhost",
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PWD'),
    database="war"
    )
    mycursor = mydb.cursor()

    sql = 'UPDATE results SET wins = 0'
    mycursor.execute(sql)

    mydb.commit()

class Suit(Enum):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4

class Value(Enum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

class Card:
    def __init__(self, suit, value) -> None:
        self.suit = suit
        self.value = value
    def disp(self) -> None:
        # print('<%i>' %(self.value.value), end = " ")
        print('<%s, %i>' %(self.suit.name, self.value.value), end = " ")
class War:
    def __init__(self) -> None:
        self.deck = [Card(suit, value) for suit in [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES] for value in [Value.Two, Value.Three, Value.Four, Value.Five, Value.Six, Value.Seven, Value.Eight, Value.Nine, Value.Ten, Value.Jack, Value.Queen, Value.King, Value.Ace]]
        self.player1_hand = None
        self.player2_hand = None
        self.result = 0

    def __deal_cards(self) -> None:
        shuffle(self.deck)
        self.player1_hand = deque(self.deck[:26])
        self.player2_hand = deque(self.deck[26:])


    def __game_eval(self):
        # check if either player is out of cards
        if len(self.player1_hand) == 0:
            self.result = 2
        elif len(self.player2_hand) == 0:
            self.result = 1
        
    def play_game(self, verbose = False) -> bool:
        while(True):
            self.__deal_cards()
            n_turns = 0
            while(self.result == 0 and n_turns < MAX_TURNS):
                n_turns += 1
                current_pool = []
                current_pool.append(self.player1_hand.pop())
                current_pool.append(self.player2_hand.pop())

                # War Condition - add two cards to pool and compare next two cards till one player collects pool or runs out of cards
                while(current_pool[-2].value.value == current_pool[-1].value.value):
                    try:
                        current_pool.append(self.player1_hand.pop())
                        current_pool.append(self.player2_hand.pop())
                        current_pool.append(self.player1_hand.pop())
                        current_pool.append(self.player2_hand.pop())
                    except IndexError:
                        break
                # condition to check whether players had enough cards
                if ((len(current_pool) - 2) % 4) == 0:
                    if current_pool[-2].value.value > current_pool[-1].value.value:
                        self.player1_hand.extendleft(current_pool)
                    elif current_pool[-2].value.value < current_pool[-1].value.value:
                        self.player2_hand.extendleft(current_pool)
                if verbose:
                    print("\nPlayer 1:", end = " ")
                    for card in self.player1_hand:
                        card.disp()
                    print("\nPlayer 2:", end = " ")
                    for card in self.player2_hand:
                        card.disp()
                self.__game_eval()
            if n_turns == MAX_TURNS:    # if game is too long, restart
                continue
            return self.result, n_turns


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Naveen's War Implementation",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="Print hands after every move for one game")
    args = parser.parse_args()
    config = vars(args)

    if config['verbose']:
        war = War()
        resp = war.play_game(True)
        print("Player", resp[0], "wins in", resp[1], "moves!")
    else:
        results = {'player1': 0, 'player2':0}
        clear_db()
        for i in range(100):
            res = run_war()
            results["player"+str(res["winner"])] += 1
        assert(war_history() ==  results)
        print("TESTS PASSED!")