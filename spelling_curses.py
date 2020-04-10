#!/usr/bin/env python3

import argparse
import curses
from curses import wrapper
import string

from SpellingWasp import *

parser = argparse.ArgumentParser(description="Spelling Wasp! A venomous clone of the NY Times Spelling Bee",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--dict", default="/usr/share/dict/web2", help="Path to dictionary file")
parser.add_argument("-n", default=7, help="Number of letters to play")
parser.add_argument("--min", default=4, help="Minimum length of a word to accept")
parser.add_argument("--minsolutions", default=50, help="Minimum number of solutions that a letter combination must have")
args = parser.parse_args()

upppoints = [ord(i) for i in string.ascii_uppercase]
lowpoints = [ord(i) for i in string.ascii_lowercase]

def show_header(stdscr):
    """Static header"""
    stdscr.hline(0,0,"-",50)
    stdscr.addstr(1,0, "* * * * * S P E L L I N G * W A S P * * * * *")
    stdscr.hline(2,0,"-",50)
    stdscr.addstr(3,0, "Type word then [Enter] to submit")
    stdscr.addstr(4,0, "[Backspace] cancel word") 
    stdscr.addstr(5,0, "[?] help, [Space] shuffle letters")
    stdscr.addstr(6,0, "[Enter] without letters - quit")
    stdscr.hline(7,0,"-",50)
    stdscr.addstr(8,0, ">>> ")

def show_status(stdscr,game):
    """Update and display score"""
    key, allowed, correctwords, score = game.status()
    stdscr.hline(10,0,"-",50)
    stdscr.addstr(11,0, "letters: *** " + key + " *** " + allowed)
    stdscr.addstr(12,0, "score: " + str(score))
    stdscr.hline(13,0,"-",50)
    stdscr.addstr(14,0, "correct guesses: ")
    stdscr.addstr(15,0, " ".join(correctwords))
   
def main(stdscr):
    # Read dictionary
    words=[]
    with open(args.dict, "r") as fh:
        words = [word.rstrip().upper() for word in fh]
    game = SpellingWasp(args.n, args.minsolutions, args.min, words)
    # Initialize screen
    stdscr.clear()
    show_header(stdscr)
    show_status(stdscr,game)
    wordbuffer = []
    while True:
        c = stdscr.getch() # Input characters
        stdscr.clear()
        show_header(stdscr)
        show_status(stdscr,game)
        if c in upppoints or c in lowpoints:
            char = chr(c)
            wordbuffer.append(char)
            stdscr.addstr(8,4,"".join(wordbuffer))
        elif c == ord("?"):
            stdscr.addstr(9,0, "[help message]")
        elif c == ord(" "):
            game.shuffle_letters()
            show_status(stdscr,game)
            stdscr.addstr(9,0, "[shuffle]")
        elif c == curses.KEY_ENTER or c == 10 or c == 13:
            if len(wordbuffer) == 0: break
            joinword = "".join(wordbuffer)
            stdscr.addstr(8,4, joinword)
            wordbuffer = []
            result, message = game.process_guess(joinword)
            stdscr.addstr(9,0, message)
            show_status(stdscr,game)
        else:
            wordbuffer = []
            stdscr.addstr(8,4, "".join(wordbuffer))

wrapper(main)
