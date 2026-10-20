# Model: argon
"""Math Kangaroo 2007, Problem #23 - Question Generator."""
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
QUESTION_ID = (2007, 23)


def check_digits_range(start_n, end_n, choices, ans_idx):
    tot = sum(len(str(x)) for x in range(start_n, end_n + 1))
    matches = [i for i, ch in enumerate(choices) if int(ch) == tot]
    assert matches == [ans_idx], f"Digits from {start_n} to {end_n} -> {tot}, choices={choices}, ans_idx={ans_idx}"


def q_2007_23(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Total Digits Written from 1 to N", "Based on 2007, Problem 23")

    opts0 = ["100", "150", "190", "192", "200"]
    check_digits_range(1, 100, opts0, 3)
    if include_orig:
        d.problem(
            "Original 2007 #23.",
            "How many digits are needed to write down all numbers from 1 to 100?",
            choices=opts0,
        )
        key.append((
            "2007 #23",
            "D",
            "Numbers 1 to 9 have 1 digit each (9 × 1 = 9 digits). Numbers 10 to 99 have 2 digits each "
            "(90 × 2 = 180 digits). The number 100 has 3 digits. In total, 9 + 180 + 3 = 192 digits are needed.",
        ))

    practices = [
        # Practice .1: 1 to 50 -> 9*1 + 41*2 = 9 + 82 = 91 digits (Answer: B)
        (
            1, 50,
            ["50", "91", "99", "100", "101"],
            1,
            "How many digits are needed to write down all whole numbers from <b>1 to 50</b>?",
            "The 9 one-digit numbers (1 to 9) use 9 × 1 = 9 digits. The 41 two-digit numbers (10 to 50) use "
            "41 × 2 = 82 digits. Altogether, 9 + 82 = 91 digits are needed.",
        ),
        # Practice .2: 1 to 120 -> 9*1 + 90*2 + 21*3 = 9 + 180 + 63 = 252 digits (Answer: C)
        (
            1, 120,
            ["240", "249", "252", "260", "360"],
            2,
            "How many digits are needed to write down all whole numbers from <b>1 to 120</b>?",
            "Numbers 1–9 use 9 × 1 = 9 digits; numbers 10–99 use 90 × 2 = 180 digits; and the 21 three-digit numbers "
            "from 100 to 120 use 21 × 3 = 63 digits. In total, 9 + 180 + 63 = 252 digits are needed.",
        ),
        # Practice .3: 1 to 80 -> 9*1 + 71*2 = 9 + 142 = 151 digits (Answer: A)
        (
            1, 80,
            ["151", "153", "160", "161", "169"],
            0,
            "A locker hallway has 80 lockers numbered from <b>1 to 80</b>. If each digit is a plastic sticker, "
            "how many digit stickers are needed in total?",
            "Lockers 1–9 need 9 × 1 = 9 stickers, and lockers 10–80 (71 lockers) need 71 × 2 = 142 stickers. "
            "That is 9 + 142 = 151 digit stickers in total.",
        ),
        # Practice .4: 10 to 100 -> 90*2 + 1*3 = 183 digits (Answer: E)
        (
            10, 100,
            ["180", "181", "182", "192", "183"],
            4,
            "How many digits are needed to write down all whole numbers from <b>10 to 100</b> (inclusive)?",
            "There are 90 two-digit numbers from 10 to 99, using 90 × 2 = 180 digits, plus the three-digit number 100, "
            "which uses 3 digits. That gives 180 + 3 = 183 digits.",
        ),
    ]

    for idx, (s_n, e_n, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_digits_range(s_n, e_n, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_23

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
