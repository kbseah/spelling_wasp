#!/usr/bin/env python3

import argparse
import random
import string
import json # for dump
from collections import defaultdict

parser = argparse.ArgumentParser(description="Spelling Wasp! A venomous clone of the NY Time's Spelling Bee",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--dict", default="/usr/share/dict/web2", help="Path to dictionary file")
parser.add_argument("-n", default=7, help="Number of letters to play")
parser.add_argument("--min", default=4, help="Minimum length of a word to accept")
parser.add_argument("--minsolutions", default=50, help="Minimum number of solutions that a letter combination must have")
args = parser.parse_args()

def _generate_key_allowed(n: int):
    """Pick n random letters, one is key, remainder are allowed"""
    picked = random.sample(string.ascii_uppercase, n)
    return(picked[0], "".join(picked[1:n]))

def all_solutions(key,allowed,min_wordlength,wordlist):
    """Get all solutions given a key letter and string of allowed letters, and wordlist.
    Return a list of solutions.
    """
    solutions = []
    for word in wordlist:
        word = word.upper()
        if key in word:
            scores = 0
            for letter in word:
                if letter not in key + allowed:
                    scores += 1
            if scores == 0 and len(word) >= min_wordlength:
                solutions.append(word)
    return(solutions)

def encourage():
    """Say something encouraging"""
    encouragement = ["Yes!", "Good job!", "Great!", "Fantastic!", "Wonderful!", "Yeah!"]
    return(random.sample(encouragement, 1)[0])

def discourage():
    """Say something discouraging"""
    discouragement = ["Nope", "No", "Wrong", "Sorry", "Meh", "Are you kidding me?"]
    return(random.sample(discouragement,1)[0])

class SpellingBee(object):
    """SpellingBee game"""

    def __init__(self, length, min_solutions, min_wordlength, wordlist):
        """Initialize new SpellingBee object, comprising:
        - Key letter 
        - Other allowed letters
        - list of solutions
        - dict of correct solutions from user (values are number of tries)
        - dict of incorrect solutions from user (values are number of tries)

        Arguments:
        length -- Number of letters to play
        min_solutions -- Minimum number of solutions
        """
        num_solutions = 0
        # Reject letter combinations that give insufficient solutions
        while num_solutions < min_solutions: 
            self._key, self._allowed = _generate_key_allowed(length)
            self._solutions = all_solutions(self._key, self._allowed, min_wordlength, wordlist)
            num_solutions = len(self._solutions)
        self._usercorrect = defaultdict(int)
        self._userwrong = defaultdict(int)

    def dump(self):
        print("key:\t" + self._key)
        print("allowed:\t" + self._allowed)
        print("solutions:\t" + " ".join(self._solutions))
        print("user correct guesses:")
        print(json.dumps(self._usercorrect,indent=2))
        print("user wrong guesses:")
        print(json.dumps(self._userwrong,indent=2))

    def status(self):
        """Display current status of the game"""
        print("--------------------------------------------------------------")
        print("Letters: *** " + self._key + " *** " + " ".join(self._allowed))
        print("Correct: " + " ".join(sorted(self._usercorrect.keys())))
        score = sum([len(key) for key in self._usercorrect.keys()])
        print("Score: " + str(score))

    def play(self):
        self.status()
        guess = input("... Try a word, or press Enter to quit >>> ")
        while guess != "":
            if guess == " ":
                self._allowed = "".join(random.sample(self._allowed, len(self._allowed)))
                self.status()
            else:
                guess = guess.upper()
                if guess in self._usercorrect.keys() and self._usercorrect[guess] > 0:
                    print("--------------------------------------------------------------")
                    print("Correct, but you have already played that word "+str(self._usercorrect[guess]) + " times")
                    self._usercorrect[guess] += 1
                elif guess in self._userwrong.keys() and self._userwrong[guess] > 0:
                    print("--------------------------------------------------------------")
                    print("Word not in dictionary, and you have already tried it "+str(self._userwrong[guess]) + " times")
                    self._userwrong[guess] += 1
                else:
                    if guess in self._solutions:
                        self._usercorrect[guess] += 1
                        print("--------------------------------------------------------------")
                        print(encourage())
                    else:
                        self._userwrong[guess] += 1
                        print("--------------------------------------------------------------")
                        print(discourage())
                    self.status()
            guess = input("... Try a word, or press Enter to quit >>> ")
        # Goodbye message
        print("--------------------------------------------------------------")
        print("Thank you for playing Spelling Wasp")
        print("Words that you missed:")
        print(" ".join([word for word in self._solutions if word not in self._usercorrect.keys()]))
        print("--------------------------------------------------------------")

# Main
# Read dictionary
words=[]
with open(args.dict, "r") as fh:
    words = [word.rstrip().upper() for word in fh]
# Play the game
game = SpellingBee(args.n, args.minsolutions, args.min, words)
game.play()
