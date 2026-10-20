# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #4 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2007, 4)


def digit_sum(n):
    return sum(int(ch) for ch in str(n))


def next_same_digit_sum(start_n, direction="greater"):
    target = digit_sum(start_n)
    step = 1 if direction == "greater" else -1
    n = start_n + step
    while digit_sum(n) != target:
        n += step
    return n


def check_same_digit_sum(start_n, choices, ans_idx, direction="greater"):
    nxt = next_same_digit_sum(start_n, direction=direction)
    matches = [i for i, ch in enumerate(choices) if int(ch) == nxt]
    assert matches == [ans_idx], (
        f"Same digit sum ({direction}) from {start_n} is {nxt}, choices={choices}, ans_idx={ans_idx}"
    )


def _generate_dynamic_digit_sum_problem(rng, mode_idx=0):
    """Procedurally generate a next/previous number with same digit sum problem."""
    m = mode_idx % 3

    if m == 0:
        # Mode 0: Standard 4-digit next number with same digit sum (nxt = start_n + 9)
        direction = "greater"
        while True:
            d0 = rng.randint(1, 6)
            d1 = rng.choice([0, 0, 1, 2, 3, 4])
            d2 = rng.randint(0, 7)
            d3 = rng.randint(4, 9)
            start_n = d0 * 1000 + d1 * 100 + d2 * 10 + d3
            if start_n != 2007:
                break
        nxt = next_same_digit_sum(start_n, "greater")
        assert nxt == start_n + 9
        s_val = digit_sum(start_n)
        traps = [
            start_n + 1,
            nxt - 1,
            nxt + 1,
            d0 * 1000 + (d1 + 1) * 100 + d2 * 10 + (d3 - 1),
            d0 * 1000 + d1 * 100 + d3 * 10 + d2,
        ]
        sum_expr = " + ".join(str(ch) for ch in str(start_n))
        nxt_expr = " + ".join(str(ch) for ch in str(nxt))
        text = (
            f"What is the smallest number greater than <b>{start_n}</b> such that the sum of its digits is the same as "
            f"the sum of the digits of {start_n}?"
        )
        expl = (
            f"The sum of the digits of {start_n} is {sum_expr} = {s_val}. Increasing the tens digit from {d2} to "
            f"{d2 + 1} and decreasing the ones digit from {d3} to {d3 - 1} gives {nxt} ({nxt_expr} = {s_val}), "
            f"which is the first number greater than {start_n} with digit sum {s_val}."
        )

    elif m == 1:
        # Mode 1: Rollover 4-digit number ending in 90 or 80 (e.g. 3090 -> 3108, 2080 -> 2107)
        direction = "greater"
        d0 = rng.randint(2, 7)
        d2 = rng.choice([8, 9])
        start_n = d0 * 1000 + d2 * 10
        nxt = next_same_digit_sum(start_n, "greater")
        s_val = digit_sum(start_n)
        traps = [
            start_n + 9,
            (d0 * 10 + 1) * 100,
            (d0 * 10 + 1) * 100 + (d2 - 1) * 10,
            nxt + 9,
            nxt - 1,
        ]
        sum_expr = " + ".join(str(ch) for ch in str(start_n))
        nxt_expr = " + ".join(str(ch) for ch in str(nxt))
        text = (
            f"What is the first number greater than <b>{start_n}</b> such that the sum of its digits equals "
            f"the sum of the digits of {start_n}?"
        )
        expl = (
            f"The sum of the digits of {start_n} is {sum_expr} = {s_val}. Every number from {start_n + 1} to "
            f"{(d0 * 10 + 1) * 100 - 1} has a digit sum larger than {s_val}. Moving to the {d0}100s, we need "
            f"the last two digits to sum to {s_val} - ({d0} + 1) = {d2 - 1}, which gives {nxt} ({nxt_expr} = {s_val})."
        )

    else:
        # Mode 2: Largest number SMALLER than start_n with the same sum of digits (nxt = start_n - 9)
        direction = "smaller"
        d0 = rng.randint(1, 6)
        d1 = rng.choice([0, 2, 3, 5])
        d2 = rng.randint(2, 8)
        d3 = rng.randint(0, 6)
        start_n = d0 * 1000 + d1 * 100 + d2 * 10 + d3
        nxt = next_same_digit_sum(start_n, "smaller")
        assert nxt == start_n - 9
        s_val = digit_sum(start_n)
        traps = [
            start_n - 1,
            nxt - 1,
            nxt + 1,
            start_n - 10,
            d0 * 1000 + d1 * 100 + d3 * 10 + d2,
        ]
        sum_expr = " + ".join(str(ch) for ch in str(start_n))
        nxt_expr = " + ".join(str(ch) for ch in str(nxt))
        text = (
            f"What is the largest number <b>smaller</b> than <b>{start_n}</b> such that the sum of its digits is the "
            f"same as the sum of the digits of {start_n}?"
        )
        expl = (
            f"The sum of the digits of {start_n} is {sum_expr} = {s_val}. Decreasing the tens digit from {d2} to "
            f"{d2 - 1} and increasing the ones digit from {d3} to {d3 + 1} gives {nxt} ({nxt_expr} = {s_val}), "
            f"which is the largest number smaller than {start_n} with digit sum {s_val}."
        )

    cands = {nxt}
    for t in traps:
        if len(cands) >= 5:
            break
        if t > 0 and t != nxt and (
            (direction == "greater" and t > start_n) or (direction == "smaller" and t < start_n)
        ):
            cands.add(t)
    for delta in [-9, -2, -1, 1, 2, 8, 9, 10, 18]:
        if len(cands) >= 5:
            break
        v = nxt + delta
        if v > 0 and v != nxt and (
            (direction == "greater" and v > start_n) or (direction == "smaller" and v < start_n)
        ):
            cands.add(v)

    vals = list(cands)[:5]
    rng.shuffle(vals)
    opts = [str(v) for v in vals]
    ans_idx = vals.index(nxt)
    check_same_digit_sum(start_n, opts, ans_idx, direction=direction)
    return start_n, opts, ans_idx, direction, text, expl


def q_2007_4(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Next Number with the Same Sum of Digits", "Based on 2007, Problem 4")

    opts0 = ["2016", "2115", "2008", "7002", "2070"]
    check_same_digit_sum(2007, opts0, 0, direction="greater")
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

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        s_num, opts, ans_idx, direction, text, expl = _generate_dynamic_digit_sum_problem(rng, mode_idx=m)
        check_same_digit_sum(s_num, opts, ans_idx, direction=direction)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_4

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
