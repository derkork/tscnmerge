from enum import Enum

from model.Printable import Printable


class Resolution(Enum):
    MINE = 1
    THEIRS = 2


def always_mine(_decision: str, _mine: Printable, _theirs: Printable) -> Resolution:
    return Resolution.MINE


def always_theirs(_decision: str, _mine: Printable, _theirs: Printable) -> Resolution:
    return Resolution.THEIRS


def always_both(_decision: str, _mine: Printable, _theirs: Printable) -> Resolution:
    return Resolution.BOTH


def interactive(decision: str, mine: Printable, theirs: Printable) -> Resolution:
    print("")
    print("")
    print(decision)
    print("MINE -------------------------------------------")
    print(mine.to_string())
    print("THEIRS -----------------------------------------")
    print(theirs.to_string())
    while True:
        result = input("use (m)ine, (t)heirs or (a)bort?: ")
        if result == "m":
            print("Using mine.")
            return Resolution.MINE
        if result == "t":
            print("Using theirs.")
            return Resolution.THEIRS
        if result == "a":
            print("Aborting merge.")
            exit(2)
