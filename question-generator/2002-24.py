# Model: argon
"""Math Kangaroo 2002, Problem #24 - Question Generator."""
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
QUESTION_ID = (2002, 24)


def next_distinct_digits_distance(start_num):
    n = start_num + 1
    while len(set(str(n))) != len(str(n)):
        n += 1
    return n - start_num, n


def check_odometer_distinct(start_num, choices, ans_idx):
    dist, _ = next_distinct_digits_distance(start_num)
    matches = [i for i, ch in enumerate(choices) if int(ch) == dist]
    assert matches == [ans_idx], f"Odometer start={start_num}, dist={dist}, choices={choices}, ans_idx={ans_idx}"


def q_2002_24(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Odometer with All Different Digits", "Based on 2002, Problem 24")

    opts0 = ["1", "21", "431", "12431", "13776"]
    check_odometer_distinct(187569, opts0, 1)
    if include_orig:
        d.problem(
            "Original 2002 #24.",
            "The odometer of my car indicates 187569. All the digits of this number are different. "
            "After how many more kilometres will this happen again?",
            choices=opts0,
        )
        key.append((
            "2002 #24",
            "B",
            "Starting from 187569, numbers 187570–187579 repeat the digit 7, and 187580–187589 repeat the digit 8. "
            "The very next number is 187590, whose digits (1, 8, 7, 5, 9, 0) are all different! "
            "That takes 187590 - 187569 = 21 km.",
        ))

    practices = [
        # Practice .1: Start = 264359. Next is 264370 (digits 2,6,4,3,7,0 all distinct!). Distance = 11 km (Answer: A)
        (
            264359,
            ["11", "21", "31", "41", "141"],
            0,
            "A car's odometer shows <b>264359</b>, where all six digits are different. "
            "After how many more kilometres will all six digits on the odometer be different again?",
            "From 264359, the numbers 264360 through 264369 all repeat the digit 6. "
            "The next number is 264370, which has digits 2, 6, 4, 3, 7, 0 — all different! "
            "That is 264370 - 264359 = 11 km later.",
        ),
        # Practice .2: Start = 398675.
        # 398676..398679: 398676(6), 398677(7), 398678(8), 398679(9)
        # 39868x(8), 39869x(9), 39870x: 398701 has digits 3,9,8,7,0,1!
        # Distance = 398701 - 398675 = 26 km (Answer: C)
        (
            398675,
            ["5", "15", "26", "35", "126"],
            2,
            "An odometer reads <b>398675</b>, and all of its digits are different. "
            "What is the smallest number of kilometres the car must travel until all six digits are different again?",
            "Checking numbers after 398675: 398676–398679 repeat 6, 7, 8, or 9; 398680–398689 repeat 8; "
            "and 398690–398699 repeat 9. At 398700 the 0 repeats, and then 398701 has all distinct digits (3, 9, 8, 7, 0, 1). "
            "The distance is 398701 - 398675 = 26 km.",
        ),
        # Practice .3: 4-digit bike counter reads 1987.
        # 1988..1989 (repeat 8,9), 1990..1999 (repeat 9), 2000..2011 (repeat 0 or 1), 2012 (repeat 2), 2013!
        # Distance = 2013 - 1987 = 26 km (Answer: D)
        (
            1987,
            ["3", "13", "16", "26", "36"],
            3,
            "A bicycle trip counter shows the 4-digit number <b>1987</b>, whose digits are all different. "
            "After how many more kilometres will the counter next show a number with all four digits different?",
            "Numbers 1988–1999 all repeat 8 or 9, and numbers 2000–2012 repeat 0, 1, or 2. "
            "The first number after 1987 with four different digits is 2013 (digits 2, 0, 1, 3). "
            "That happens after 2013 - 1987 = 26 km.",
        ),
        # Practice .4: Start = 478659.
        # 478660..478689 repeat 6, 7, or 8. Next distinct-digit number is 478690 (4,7,8,6,9,0).
        # Distance = 478690 - 478659 = 31 km (Answer: E)
        (
            478659,
            ["1", "11", "21", "29", "31"],
            4,
            "The odometer of a bus shows <b>478659</b>, where every digit is different. "
            "After how many more kilometres will all six digits be different again?",
            "From 478659, numbers 478660–478669 repeat 6, 478670–478679 repeat 7, and 478680–478689 repeat 8. "
            "The next number is 478690, whose digits (4, 7, 8, 6, 9, 0) are all different! "
            "That happens after 478690 - 478659 = 31 km.",
        ),
    ]

    for idx, (s_num, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_odometer_distinct(s_num, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_24

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
