# Model: argon
"""Math Kangaroo 2007, Problem #4 - Question Generator."""
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
QUESTION_ID = (2007, 4)


def digit_sum(n):
    return sum(int(ch) for ch in str(n))


def next_same_digit_sum(start_n):
    target = digit_sum(start_n)
    n = start_n + 1
    while digit_sum(n) != target:
        n += 1
    return n


def check_same_digit_sum(start_n, choices, ans_idx):
    nxt = next_same_digit_sum(start_n)
    matches = [i for i, ch in enumerate(choices) if int(ch) == nxt]
    assert matches == [ans_idx], f"Next same digit sum after {start_n} is {nxt}, choices={choices}, ans_idx={ans_idx}"


def q_2007_4(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Next Number with the Same Sum of Digits", "Based on 2007, Problem 4")

    opts0 = ["2016", "2115", "2008", "7002", "2070"]
    check_same_digit_sum(2007, opts0, 0)
    if include_orig:
        d.problem(
            "Original 2007 #4.",
            "The numbers 34 and 142 have the same sum of their digits (3+4=7 and 1+4+2=7). "
            "What is the first number greater than 2007 such that the sum of its digits is the same as the sum "
            "of the digits of 2007?",
            choices=opts0,
        )
        key.append((
            "2007 #4",
            "A",
            "The sum of the digits of 2007 is 2 + 0 + 0 + 7 = 9. To find the smallest number greater than 2007 "
            "with digit sum 9, increase the tens digit from 0 to 1 and decrease the ones digit from 7 to 6, giving 2016 "
            "(2 + 0 + 1 + 6 = 9).",
        ))

    practices = [
        # Practice .1: Start = 2026 (sum = 10) -> next is 2035 (2+0+3+5 = 10) (Answer: C)
        (
            2026,
            ["2027", "2034", "2035", "2116", "2062"],
            2,
            "What is the smallest number greater than <b>2026</b> such that the sum of its digits is the same as "
            "the sum of the digits of 2026?",
            "The sum of the digits of 2026 is 2 + 0 + 2 + 6 = 10. Increasing the tens digit from 2 to 3 and "
            "decreasing the ones digit from 6 to 5 gives 2035, which is the first number after 2026 with digit sum 10.",
        ),
        # Practice .2: Start = 1408 (sum = 13) -> next is 1417 (1+4+1+7 = 13) (Answer: B)
        (
            1408,
            ["1409", "1417", "1426", "1507", "1480"],
            1,
            "What is the first number greater than <b>1408</b> whose digits add up to the same sum as the digits of 1408?",
            "The digits of 1408 add up to 1 + 4 + 0 + 8 = 13. The first number after 1408 with digit sum 13 is "
            "1417 (1 + 4 + 1 + 7 = 13).",
        ),
        # Practice .3: Start = 3059 (sum = 17) -> 3068 (3+0+6+8 = 17) (Answer: D)
        (
            3059,
            ["3060", "3067", "3069", "3068", "3158"],
            3,
            "What is the smallest number greater than <b>3059</b> that has the same sum of digits as 3059?",
            "The digit sum of 3059 is 3 + 0 + 5 + 9 = 17. Increasing the tens digit by 1 (from 5 to 6) and decreasing "
            "the ones digit by 1 (from 9 to 8) gives 3068, whose digits also sum to 3 + 0 + 6 + 8 = 17.",
        ),
        # Practice .4: Start = 4090 (sum = 13) -> 4091..4099 have sums 14..22; 4100..4108: 4108 has sum 4+1+0+8 = 13! (Answer: E)
        (
            4090,
            ["4099", "4100", "4190", "4180", "4108"],
            4,
            "What is the first number greater than <b>4090</b> such that the sum of its digits equals the sum of the digits of 4090?",
            "The sum of the digits of 4090 is 4 + 0 + 9 + 0 = 13. Every number from 4091 to 4099 has a digit sum larger "
            "than 13. Moving to the 4100s, we need the last two digits to sum to 13 - (4 + 1) = 8, which gives 4108.",
        ),
    ]

    for idx, (s_num, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_same_digit_sum(s_num, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_4

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
