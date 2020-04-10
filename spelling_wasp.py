#!/usr/bin/env python3

import argparse
import random
import string
import json # for dump
from collections import defaultdict
from SpellingWasp import *

parser = argparse.ArgumentParser(description="Spelling Wasp! A venomous clone of the NY Times Spelling Bee",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--dict", default="/usr/share/dict/web2", help="Path to dictionary file")
parser.add_argument("-n", default=7, help="Number of letters to play")
parser.add_argument("--min", default=4, help="Minimum length of a word to accept")
parser.add_argument("--minsolutions", default=50, help="Minimum number of solutions that a letter combination must have")
args = parser.parse_args()

# Main
# Read dictionary
words=[]
with open(args.dict, "r") as fh:
    words = [word.rstrip().upper() for word in fh]
# Play the game
game = SpellingWasp(args.n, args.minsolutions, args.min, words)
game.play()
