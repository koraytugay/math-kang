# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #22 - Question Generator."""
import os
import sys
import math
import random
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    NUM_WORDS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 22)


def check_seating_ways(n_total, pred_fn, choices, ans_idx):
    """Verify by exact permutation enumeration over S_{n_total} that the number of valid seatings
    matches choices[ans_idx] uniquely.
    """
    ways = sum(1 for perm in itertools.permutations(range(n_total)) if pred_fn(perm))
    matches = [i for i, ch in enumerate(choices) if int(ch) == ways]
    assert matches == [ans_idx], f"Seating ways={ways}, choices={choices}, ans_idx={ans_idx}"
    return ways


SCENARIOS = [
    ("friends", "sit around a restaurant table", "chairs"),
    ("friends", "sit on a park bench", "seats"),
    ("family members", "sit around a dinner table", "chairs"),
    ("astronauts", "board a spacecraft", "seats"),
    ("students", "stand in a line for a class photo", "spots"),
    ("musicians", "sit in a row on stage", "chairs"),
]

NAMES = ["Emma", "Lucas", "Mia", "Noah", "Leo", "Clara", "Sam", "Zoe"]


def _make_seating_choices(rng, ans_val, extra_cands=()):
    cands = {ans_val}
    for c in extra_cands:
        if c > 0 and c != ans_val:
            cands.add(c)
    for d in [2, 3, 4, 6, 8, 12, 16, 24, 36, 48, 120]:
        if len(cands) >= 5:
            break
        cands.add(d)
    vals = sorted(list(cands))[:5]
    if ans_val not in vals:
        vals[-1] = ans_val
        vals.sort()
    if rng.random() < 0.35:
        vals = list(reversed(vals))
    ans_idx = vals.index(ans_val)
    return [str(v) for v in vals], ans_idx


def _generate_dynamic_seating_problem(rng, mode=0):
    """Procedurally generate a seating permutation problem with exact S_n verification."""
    group_noun, action_phrase, seat_noun = rng.choice(SCENARIOS)
    actors = rng.sample(NAMES, 3)
    m = mode % 3

    if m == 0:
        # Mode 0: n_total in {4, 5, 6}, n_fixed in {1, 2, 3} people have fixed seats
        n_total, n_fixed = rng.choice([(4, 1), (4, 2), (5, 1), (5, 2), (6, 2), (6, 3)])
        free = n_total - n_fixed
        ans_val = math.factorial(free)
        pred_fn = lambda perm, nf=n_fixed: all(perm[i] == i for i in range(nf))

        n_word = NUM_WORDS[n_total].capitalize()
        if n_fixed == 1:
            fixed_clause = f"{actors[0]} always takes the exact same favorite {seat_noun[:-1]}."
            fixed_expl = f"{actors[0]}'s {seat_noun[:-1]} is fixed"
        elif n_fixed == 2:
            fixed_clause = (
                f"{actors[0]} always takes the first {seat_noun[:-1]} and {actors[1]} always takes the last {seat_noun[:-1]}."
            )
            fixed_expl = f"{actors[0]}'s and {actors[1]}'s {seat_noun} are fixed"
        else:
            fixed_clause = (
                f"{actors[0]}, {actors[1]}, and {actors[2]} each must sit in their own assigned {seat_noun[:-1]}."
            )
            fixed_expl = f"3 of the {seat_noun} are already fixed"

        mult_str = " × ".join(str(k) for k in range(free, 0, -1))
        text = (
            f"{n_word} {group_noun} {action_phrase} with {n_total} {seat_noun}. "
            f"{fixed_clause} In how many different ways can all {n_total} {group_noun} be arranged?"
        )
        expl = (
            f"Since {fixed_expl}, only the remaining {free} {group_noun} can switch places among the remaining "
            f"{free} {seat_noun}, giving {mult_str} = {ans_val} different ways."
        )
        opts, ans_idx = _make_seating_choices(
            rng, ans_val, extra_cands=[free, n_total, math.factorial(n_total), free * 2]
        )
        check_seating_ways(n_total, pred_fn, opts, ans_idx)
        return n_total, pred_fn, opts, ans_idx, text, expl

    elif m == 1:
        # Mode 1: One person can choose between 2 specific end seats, and any remaining fixed/free people arrange in the rest
        n_total, n_fixed = rng.choice([(4, 0), (4, 1), (5, 1)])
        free_others = n_total - 1 - n_fixed
        ans_val = 2 * math.factorial(free_others)
        # Person 0 sits at index 0 or index (n_total - 1); persons 1..n_fixed sit at fixed indices 1..n_fixed
        pred_fn = lambda perm, nt=n_total, nf=n_fixed: (
            perm[0] in (0, nt - 1) and all(perm[i] == i for i in range(1, 1 + nf))
        )
        n_word = NUM_WORDS[n_total].capitalize()
        mult_str = " × ".join(str(k) for k in range(free_others, 0, -1))
        if n_fixed == 0:
            text = (
                f"{n_word} {group_noun} sit in a row of {n_total} {seat_noun}. {actors[0]} insists on sitting at one of "
                f"the two ends (either the far left or the far right). In how many different ways can the {n_total} "
                f"{group_noun} sit in the row?"
            )
            expl = (
                f"{actors[0]} has 2 choices (the far left or far right end). For each choice, the remaining "
                f"{free_others} {group_noun} can sit in the remaining {free_others} {seat_noun} in {mult_str} = "
                f"{math.factorial(free_others)} ways, giving 2 × {math.factorial(free_others)} = {ans_val} ways in total."
            )
        else:
            text = (
                f"{n_word} {group_noun} sit in a row of {n_total} {seat_noun}. {actors[1]} always sits in the middle "
                f"{seat_noun[:-1]}, and {actors[0]} always sits at one of the two ends (far left or far right). "
                f"In how many different ways can the {n_total} {group_noun} be seated?"
            )
            expl = (
                f"{actors[1]}'s middle spot is fixed (1 choice), and {actors[0]} has 2 choices (either end). "
                f"The remaining {free_others} {group_noun} can fill the other {free_others} {seat_noun} in "
                f"{mult_str} = {math.factorial(free_others)} ways, giving 2 × {math.factorial(free_others)} = {ans_val} ways."
            )
        opts, ans_idx = _make_seating_choices(
            rng, ans_val, extra_cands=[math.factorial(free_others), math.factorial(n_total), ans_val // 2, ans_val + 4]
        )
        check_seating_ways(n_total, pred_fn, opts, ans_idx)
        return n_total, pred_fn, opts, ans_idx, text, expl

    else:
        # Mode 2: Unrestricted permutation of n_total in {3, 4} people, or 5 people with 2 adjacent-pair / fixed rules
        n_total = rng.choice([3, 4])
        ans_val = math.factorial(n_total)
        pred_fn = lambda perm: True
        n_word = NUM_WORDS[n_total].capitalize()
        mult_str = " × ".join(str(k) for k in range(n_total, 0, -1))
        text = (
            f"{n_word} {group_noun} {action_phrase} with {n_total} {seat_noun}, and anyone can take any {seat_noun[:-1]}. "
            f"In how many different orders can the {n_total} {group_noun} be arranged?"
        )
        expl = (
            f"There are {n_total} choices for the first {seat_noun[:-1]}, {n_total - 1} for the second, and so on, "
            f"giving {mult_str} = {ans_val} different arrangements."
        )
        opts, ans_idx = _make_seating_choices(
            rng, ans_val, extra_cands=[n_total, n_total * 2, n_total * n_total, ans_val // 2]
        )
        check_seating_ways(n_total, pred_fn, opts, ans_idx)
        return n_total, pred_fn, opts, ans_idx, text, expl


def q_2002_22(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Seating Arrangements with Fixed Seats", "Based on 2002, Problem 22")

    opts0 = ["3", "4", "6", "24", "25"]
    check_seating_ways(4, lambda perm: perm[0] == 0, opts0, 2)
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

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        ntot, pred_fn, opts, ans_idx, text, expl = _generate_dynamic_seating_problem(rng, mode=m)
        check_seating_ways(ntot, pred_fn, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_22

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
