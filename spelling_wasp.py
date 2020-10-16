#!/usr/bin/env python3

import argparse
import random
import string
import json  # for dump
import unicodedata
import curses
import time
from curses import wrapper
from textwrap import wrap
from collections import defaultdict
from SpellingWasp import *

parser = argparse.ArgumentParser(
    description="Spelling Wasp! A venomous clone of the NY Times Spelling Bee",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "--dict", "-d", default="/usr/share/dict/web2",
    help="Path to dictionary file")
parser.add_argument(
    "-n", default=7, help="Number of letters to play")
parser.add_argument(
    "--min", default=4, help="Minimum length of a word to accept")
parser.add_argument(
    "--minsolutions", default=50,
    help="Minimum number of solutions that a letter combination must have")
parser.add_argument(
    "--fullscreen", "-f", action="store_true",
    help="Play in fullscreen mode (requires python curses module)")
parser.add_argument(
    "--skip_splash", "-s", action="store_true",
    help="Skip splash screen in fullscreen mode")
args = parser.parse_args()


def main_cli(args):
    """Command-line version of the game"""
    # Main
    # Read dictionary
    words = []
    with open(args.dict, "r") as fh:
        words = [word.rstrip().upper() for word in fh]
    # Play the game
    game = SpellingWasp(args.n, args.minsolutions, args.min, words)
    game.play()


upppoints = [ord(i) for i in string.ascii_uppercase]
lowpoints = [ord(i) for i in string.ascii_lowercase]


def fs_show_title(stdscr):
    stdscr.hline(0, 0, "-", 50)
    stdscr.addstr(1, 0, " - - - - - S P E L L I N G  *  W A S P - - - - - ")
    stdscr.hline(2, 0, "-", 50)


def fs_splash_screen(stdscr):
    """Splash when starting the game"""
    fs_show_title(stdscr)
    stdscr.refresh()
    curses.napms(500)
    stdscr.addstr(3, 0, "...Loading dictionary...")
    stdscr.refresh()
    curses.napms(500)
    stdscr.addstr(4, 0, "...Gesticulating spines...")
    stdscr.refresh()
    curses.napms(500)
    stdscr.addstr(5, 0, "...Recomporting buzzwords...")
    stdscr.refresh()
    for i in range(0, 50):
        curses.napms(20)
        stdscr.addstr(6, i, "-")
        stdscr.refresh()
    stdscr.addstr(7, 0, "Bzz! Welcome to Spelling Wasp!")
    stdscr.addstr(8, 0, "Unlike a Spelling Bee, we can sting you multiple")
    stdscr.addstr(9, 0, "times in a day")
    stdscr.addstr(10, 0, " >>> Press any key to start playing <<<")
    stdscr.refresh()


def fs_show_header(stdscr):
    """Static header"""
    fs_show_title(stdscr)
    stdscr.addstr(3, 0, "Type word then [Enter] to submit")
    stdscr.addstr(4, 0, "[Backspace] cancel word / [!] hint")
    stdscr.addstr(5, 0, "[?] help / [Space] shuffle letters")
    stdscr.addstr(6, 0, "[Enter] without letters - quit")
    stdscr.hline(7, 0, "-", 50)
    stdscr.addstr(8, 0, ">>> ")


def fs_show_status(stdscr, game):
    """Update and display score"""
    key, allowed, correctwords, score = game.status()
    stdscr.hline(10, 0, "-", 50)
    stdscr.addstr(11, 0, "letters: *** " + key + " *** " + " ".join(allowed))
    stdscr.addstr(12, 0, "score: " + str(score) + " | unguessed: " +
                  str(game._numsolutions - len(game._usercorrect)))
    stdscr.hline(13, 0, "-", 50)
    stdscr.addstr(14, 0, "correct guesses: ")
    # Report correctly guessed words, but wrap the string if the
    # list gets too long
    correctstr = " ".join(correctwords)
    correctwrap = wrap(correctstr, 50)
    for i in range(0, len(correctwrap)):
        stdscr.addstr(15+i, 0, correctwrap[i])


def fs_exit_report(stdscr, game):
    """Report unguessed words and say goodbye"""
    key, allowed, correctwords, score = game.status()
    fs_show_title(stdscr)
    stdscr.addstr(3, 0, "Thank you for playing Spelling Wasp")
    stdscr.addstr(4, 0, "Press any key to exit")
    stdscr.hline(5, 0, "-", 50)
    stdscr.addstr(6, 0, "final score: " + str(score))
    stdscr.hline(7, 0, "-", 50)
    stdscr.addstr(8, 0, "These are the words you didn't guess:")
    unguessedstr = " ".join(sorted(
        [word for word in game._solutions if word not in game._usercorrect.keys()]))
    unguessedwrap = wrap(unguessedstr, 50)
    for i in range(0, len(unguessedwrap)):
        stdscr.addstr(9+i, 0, unguessedwrap[i])


def main_fullscreen(stdscr):
    """Full-screen version of the game, which requires curses module"""
    # Initialize screen
    stdscr.clear()
    fs_show_title(stdscr)
    stdscr.refresh()
    # Read dictionary
    words = []
    with open(args.dict, "r") as fh:
        words = [word.rstrip().upper() for word in fh]
    game = SpellingWasp(args.n, args.minsolutions, args.min, words)
    if not args.skip_splash:
        while True:
            # Splash screen
            fs_splash_screen(stdscr)
            v = stdscr.getch()
            break
    stdscr.clear()
    fs_show_header(stdscr)
    fs_show_status(stdscr, game)
    wordbuffer = []
    while True:
        c = stdscr.getch()  # Input characters
        stdscr.clear()
        fs_show_header(stdscr)
        fs_show_status(stdscr, game)
        if c in upppoints or c in lowpoints:
            char = chr(c)
            wordbuffer.append(char)
            stdscr.addstr(8, 4, "".join(wordbuffer))
        elif c == ord("?"):
            stdscr.addstr(9, 0, wasp_facts())
        elif c == ord("!"):
            stdscr.addstr(9, 0, "Hint: " + game.hint())
        elif c == ord(" "):
            game.shuffle_letters()
            fs_show_status(stdscr, game)
            stdscr.addstr(9, 0, "[shuffle]")
        elif c == curses.KEY_ENTER or c == 10 or c == 13:
            if len(wordbuffer) == 0:
                stdscr.clear()
                fs_exit_report(stdscr, game)
                d = stdscr.getch()
                break
            joinword = "".join(wordbuffer)
            stdscr.addstr(8, 4, joinword)
            wordbuffer = []
            result, message, unguessed = game.process_guess(joinword)
            stdscr.addstr(9, 0, message)
            fs_show_status(stdscr, game)
            if unguessed == 0:
                stdscr.clear()
                stdscr.addstr(
                    1, 0, "bzzzz bzzzz bzzzz YOU GUESSED ALL THE WORDS! bzzz bzzz bzzz")
                stdscr.addstr(2, 0, "Press any key to exit")
                fs_show_status(stdscr, game)
                d = stdscr.getch()
                break
        else:
            wordbuffer = []
            stdscr.addstr(8, 4, "".join(wordbuffer))


# Main
if args.fullscreen:
    wrapper(main_fullscreen)
else:
    main_cli(args)
