# Model: argon
"""Math Kangaroo 2002, Problem #22 - Question Generator."""
import os
import sys
import math
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    PW,
    PH,
    ML,
    MR,
    MT,
    MB,
    TW,
    LETTERS,
    DARK,
    GRAY,
    BODY,
    NUM_WORDS,
    Doc,
    option_row,
    hstack,
    vstack,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
QUESTION_ID = (2002, 22)


def check_seating_ways(n_total, n_fixed, choices, ans_idx):
    free = n_total - n_fixed
    ways = math.factorial(free)
    matches = [i for i, ch in enumerate(choices) if int(ch) == ways]
    assert matches == [ans_idx], f"Seating ways={ways}, choices={choices}, ans_idx={ans_idx}"


def q_2002_22(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Seating Arrangements with Fixed Seats", "Based on 2002, Problem 22")

    opts0 = ["3", "4", "6", "24", "25"]
    check_seating_ways(4, 1, opts0, 2)
    if include_orig:
        d.problem(
            "Original 2002 #22.",
            "Four friends go to a restaurant and sit down at a table. John always sits at the same spot on the table. "
            "In how many ways can the friends sit around the table?",
            choices=opts0,
        )
        key.append((
            "2002 #22",
            "C",
            "Since John always takes his fixed seat, only the other 3 friends change places among the remaining 3 seats. "
            "The first friend has 3 choices, the second has 2 choices, and the third has 1 choice, giving 3 × 2 × 1 = 6 ways.",
        ))

    practices = [
        # Practice .1: 5 friends, 2 always sit in their favorite chairs -> 3! = 6 ways (Answer: B)
        (
            5,
            2,
            ["3", "6", "12", "24", "120"],
            1,
            "Five friends sit on a bench with 5 seats at the park. Emma always sits on the far left seat, and Lucas "
            "always sits on the far right seat. In how many different ways can the 5 friends sit on the bench?",
            "Emma's and Lucas's seats are fixed, leaving 3 middle seats for the other 3 friends. "
            "Those 3 friends can be arranged in 3 × 2 × 1 = 6 different ways.",
        ),
        # Practice .2: 5 family members at a dinner table, Grandma always sits at the head -> 4! = 24 ways (Answer: D)
        (
            5,
            1,
            ["4", "12", "16", "24", "120"],
            3,
            "Five family members sit around a dinner table with 5 chairs. Grandma always sits in the armchair at the "
            "head of the table. In how many different ways can the family sit around the table?",
            "With Grandma's seat fixed, the remaining 4 family members can sit in the other 4 chairs in "
            "4 × 3 × 2 × 1 = 24 different ways.",
        ),
        # Practice .3: 4 astronauts in a 4-seat spacecraft, Commander and Pilot have fixed seats -> 2! = 2 ways (Answer: A)
        (
            4,
            2,
            ["2", "4", "6", "12", "24"],
            0,
            "Four astronauts board a spacecraft with 4 seats. The Commander must sit in Seat 1 and the Pilot must sit "
            "in Seat 2. In how many different ways can the 4 astronauts be seated?",
            "Seat 1 and Seat 2 are already fixed for the Commander and Pilot. The remaining 2 astronauts can sit in "
            "Seats 3 and 4 in 2 × 1 = 2 ways.",
        ),
        # Practice .4: 4 runners posing for a photo, nobody has a fixed spot -> 4! = 24 ways (Answer: E)
        (
            4,
            0,
            ["4", "8", "12", "16", "24"],
            4,
            "Four friends stand in a line of 4 spots to take a team photo, and anyone can stand in any spot. "
            "In how many different orders can the 4 friends stand in line?",
            "There are 4 choices for the first spot, 3 for the second, 2 for the third, and 1 for the fourth, "
            "giving 4 × 3 × 2 × 1 = 24 different orders.",
        ),
    ]

    for idx, (ntot, nfix, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_seating_ways(ntot, nfix, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_22

if __name__ == "__main__":
    import inspect
    collector = _ProblemCollector()
    key = []
    sig = inspect.signature(GENERATE)
    if "num_practice" in sig.parameters:
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5)
    else:
        GENERATE(collector, key, set_num=1, include_orig=True)
    assert len(collector.problems) == len(key)
    print(f"Verified {QUESTION_ID} (model={MODEL}): {len(collector.problems)} problems generated.")
