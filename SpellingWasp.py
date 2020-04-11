#!/usr/bin/env python3

import argparse
import random
import string
import json # for dump
from collections import defaultdict

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
    solutions = set(solutions) # Convert to set to take only unique elements
    return(solutions)

def encourage():
    """Say something encouraging"""
    encouragement = ["Yes!", "Good job!", "Great!", "Fantastic!", "Wonderful!", "Yeah!"]
    return(random.sample(encouragement, 1)[0])

def discourage():
    """Say something discouraging"""
    discouragement = ["Nope", "No", "Wrong", "Sorry", "Meh", "Are you kidding me?"]
    return(random.sample(discouragement,1)[0])

def wasp_facts():
    facts = ["Parasitoid wasps lay eggs in living hosts, eventually killing them",
             "Bees and ants actually evolved from wasp ancestors",
             "The sting of a wasp is actually a modified ovipositor",
             "Social wasps live in nests with a queen and sister workers",
             "Most wasp species are solitary and don't live in nests",
             "Male wasps develop from unfertilized eggs",
             "Figs need tiny fig wasps to fertilize their fruit"]
    return(random.choice(facts))

class SpellingWasp(object):
    """SpellingWasp game"""

    SEPARATOR = "--------------------------------------------------------------"

    def __init__(self, length, min_solutions, min_wordlength, wordlist):
        """Initialize new SpellingWasp object, comprising:
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
        self._numsolutions = num_solutions

    def dump(self):
        print("key:\t" + self._key)
        print("allowed:\t" + self._allowed)
        print("solutions:\t" + " ".join(self._solutions))
        print("user correct guesses:")
        print(json.dumps(self._usercorrect,indent=2))
        print("user wrong guesses:")
        print(json.dumps(self._userwrong,indent=2))

    def print_status(self):
        """Display current status of the game"""
        print(SpellingWasp.SEPARATOR)
        print("Letters: *** " + self._key + " *** " + " ".join(self._allowed))
        print("Correct: " + " ".join(sorted(self._usercorrect.keys())))
        score = sum([len(key) for key in self._usercorrect.keys()])
        print("Score: " + str(score) + " / Unguessed: " + str(self._numsolutions - len(self._usercorrect.keys())))

    def status(self):
        """Return current status of game"""
        key = self._key
        allowed = self._allowed
        correct = sorted(self._usercorrect.keys())
        score = sum([len(key) for key in self._usercorrect.keys()])
        return(key, allowed, correct, score)

    def shuffle_letters(self):
        self._allowed = "".join(random.sample(self._allowed, len(self._allowed)))

    def welcome(self):
        print(SpellingWasp.SEPARATOR)
        print("Bzz! Welcome to Spelling Wasp!")
        print("Unlike a Spelling Bee, we can sting you multiple times in a day")

    def help(self):
        print("Form a word from the allowed letters.")
        print("The word must contain the highlighted key letter " + self._key)
        print("Letters may be repeated.")
        print("You may type the word in upper or lower case")
        print("Type ? to see this help message again.")
        print("Type Space to shuffle the letters around")
        print("Type Enter only to end the game and see the solutions")

    def hint(self):
        """Give a hint for one of the unguessed words"""
        # Use set for set operation, back to list for random sampling
        pick = random.choice(list(self._solutions - set(self._usercorrect.keys()))) 
        pick = list(pick)
        # Blank out randomly a third of the letters
        blankpos = random.sample(range(0,len(pick)), int(len(pick)/3))
        for i in blankpos:
            pick[i] = '-'
        return("".join(pick))

    def process_guess(self, guess):
        guess = guess.upper()
        result = ""
        message = ""
        if guess in self._usercorrect.keys() and self._usercorrect[guess] > 0:
            result = "correct_played"
            message = "Correct, but you have already played that word "+str(self._usercorrect[guess]) + " times"
            self._usercorrect[guess] += 1
        elif guess in self._userwrong.keys() and self._userwrong[guess] > 0:
            result = "wrong_played"
            message = "Word not in dictionary, and you have already tried it "+str(self._userwrong[guess]) + " times"
            self._userwrong[guess] += 1
        else:
            if guess in self._solutions:
                self._usercorrect[guess] += 1
                result = "correct_new"
                message = encourage()
            else:
                self._userwrong[guess] += 1
                result = "wrong_new"
                message = discourage()
        unguessed = self._numsolutions - len(self._usercorrect.keys())
        return(result, message, unguessed)

    def play(self):
        self.welcome()
        self.print_status()
        guess = input("... Try a word / [Space] shuffle / [?] help / [!] hint / [Enter] quit >>> ")
        while guess != "":
            # Shuffle letters if user types Space
            if guess == " ":
                self._allowed = "".join(random.sample(self._allowed, len(self._allowed)))
                self.print_status()
            elif guess == "?":
                self.help()
            elif guess == "!":
                hintword = self.hint()
                print("Hint: "+hintword)
            # Check the guess
            else:
                result, message, unguessed = self.process_guess(guess)
                print(SpellingWasp.SEPARATOR)
                print(message)
                if result in ["correct_new", "wrong_new"]:
                    self.print_status()
                if unguessed == 0:
                    print ("You have guessed all the words! Wow!")
                    self.goodbye()
                    break
            guess = input("... Try a word / [Space] shuffle / [?] help / [!] hint / [Enter] quit >>> ")
        self.goodbye()

    def goodbye(self):
        # Goodbye message
        print(SpellingWasp.SEPARATOR)
        print("Thank you for playing Spelling Wasp")
        print("Words that you missed:")
        print(" ".join([word for word in self._solutions if word not in self._usercorrect.keys()]))
        print(SpellingWasp.SEPARATOR)
