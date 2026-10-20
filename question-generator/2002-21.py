# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #21 - Question Generator."""
import os
import sys
import random
import itertools
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 21)


def can_reach_target_3cards(cards, target, allow_fractions=False):
    """Return a string formula if the 3 cards can make `target` using +, -, *, / and parentheses, else None."""
    if allow_fractions:
        ops = [
            ("+", lambda a, b: a + b),
            ("-", lambda a, b: a - b),
            ("×", lambda a, b: a * b),
            ("÷", lambda a, b: Fraction(a, b) if b != 0 else None),
        ]
    else:
        ops = [
            ("+", lambda a, b: a + b),
            ("-", lambda a, b: a - b),
            ("×", lambda a, b: a * b),
            ("÷", lambda a, b: a // b if b != 0 and a % b == 0 else None),
        ]
    for x, y, z in itertools.permutations(cards):
        for s1, f1 in ops:
            for s2, f2 in ops:
                r1 = f1(x, y)
                if r1 is not None:
                    r2 = f2(r1, z)
                    if r2 == target:
                        return f"({x} {s1} {y}) {s2} {z} = {target}"
                r3 = f2(y, z)
                if r3 is not None:
                    r4 = f1(x, r3)
                    if r4 == target:
                        return f"{x} {s1} ({y} {s2} {z}) = {target}"
    return None


def check_cards_target(players_cards, target, expected_unsolvable_names):
    unsolvable_int = [name for name, cards in players_cards if can_reach_target_3cards(cards, target, False) is None]
    unsolvable_frac = [name for name, cards in players_cards if can_reach_target_3cards(cards, target, True) is None]
    assert unsolvable_int == unsolvable_frac == expected_unsolvable_names, (
        f"For target={target}, expected unsolvable={expected_unsolvable_names}, got int={unsolvable_int}, frac={unsolvable_frac}"
    )


NAME_TRIPLETS = [
    ("Leo", "Mia", "Noah"),
    ("Anna", "Ben", "Clara"),
    ("Dan", "Eva", "Finn"),
    ("Ruby", "Sam", "Toby"),
    ("Iris", "Jack", "Kate"),
    ("Liam", "Maya", "Owen"),
]


def _generate_dynamic_cards_problem(rng, mode=0):
    """Procedurally generate a 3-card arithmetic target puzzle by partitioning digits 1..9."""
    names = list(rng.choice(NAME_TRIPLETS))
    m = mode % 4

    for _ in range(1000):
        target = rng.randint(14, 26)
        deck = list(range(1, 10))
        rng.shuffle(deck)
        hands = [tuple(sorted(deck[0:3], reverse=True)), tuple(sorted(deck[3:6], reverse=True)), tuple(sorted(deck[6:9], reverse=True))]
        sols_int = [can_reach_target_3cards(h, target, False) for h in hands]
        sols_frac = [can_reach_target_3cards(h, target, True) for h in hands]
        # Require integer and fractional reachability to agree for every hand
        if any((si is None) != (sf is None) for si, sf in zip(sols_int, sols_frac)):
            continue
        unsolv_idxs = [i for i, s in enumerate(sols_int) if s is None]

        if m in (0, 1) and len(unsolv_idxs) == 1:
            bad_i = unsolv_idxs[0]
            good_idxs = [i for i in range(3) if i != bad_i]
            p_cards = [(names[i], hands[i]) for i in range(3)]
            exp_unsolv = [names[bad_i]]
            pair_distractor = f"{names[good_idxs[0]]} and {names[good_idxs[1]]}"
            opts = [names[0], names[1], names[2], f"All three can get {target}", pair_distractor]
            ans_idx = bad_i
            text = (
                f"The digits from 1 to 9 are written on 9 cards. {names[0]} has the digits "
                f"{hands[0][0]}, {hands[0][1]}, and {hands[0][2]}; {names[1]} has "
                f"{hands[1][0]}, {hands[1][1]}, and {hands[1][2]}; and {names[2]} has "
                f"{hands[2][0]}, {hands[2][1]}, and {hands[2][2]}. Each of them uses some of the four basic "
                f"operations +, -, ×, ÷ and each of their own three cards once. Who <b>cannot</b> obtain <b>{target}</b> as a result?"
            )
            expl = (
                f"{names[good_idxs[0]]} can make {target} with {sols_int[good_idxs[0]]}. "
                f"{names[good_idxs[1]]} can make {target} with {sols_int[good_idxs[1]]}. "
                f"With {names[bad_i]}'s cards {hands[bad_i]}, no combination of +, -, ×, ÷ produces {target}. "
                f"So {names[bad_i]} cannot obtain {target}."
            )
            check_cards_target(p_cards, target, exp_unsolv)
            return p_cards, target, exp_unsolv, opts, ans_idx, text, expl

        elif m == 2 and len(unsolv_idxs) == 0:
            p_cards = [(names[i], hands[i]) for i in range(3)]
            exp_unsolv = []
            opts = [names[0], names[1], names[2], f"All three can get {target}", f"{names[0]} and {names[1]}"]
            ans_idx = 3
            text = (
                f"The digits from 1 to 9 are divided among three friends: {names[0]} gets "
                f"{hands[0][0]}, {hands[0][1]}, and {hands[0][2]}; {names[1]} gets "
                f"{hands[1][0]}, {hands[1][1]}, and {hands[1][2]}; and {names[2]} gets "
                f"{hands[2][0]}, {hands[2][1]}, and {hands[2][2]}. Using +, -, ×, ÷ and each of their three cards once, "
                f"who <b>cannot</b> obtain <b>{target}</b>?"
            )
            expl = (
                f"{names[0]} can make {target} with {sols_int[0]}. "
                f"{names[1]} can make {target} with {sols_int[1]}. "
                f"{names[2]} can make {target} with {sols_int[2]}. "
                f"Therefore, all three of them can obtain {target}!"
            )
            check_cards_target(p_cards, target, exp_unsolv)
            return p_cards, target, exp_unsolv, opts, ans_idx, text, expl

        elif m == 3 and len(unsolv_idxs) == 2:
            good_i = [i for i in range(3) if i not in unsolv_idxs][0]
            bad_a, bad_b = unsolv_idxs[0], unsolv_idxs[1]
            p_cards = [(names[i], hands[i]) for i in range(3)]
            exp_unsolv = [names[bad_a], names[bad_b]]
            correct_pair = f"{names[bad_a]} and {names[bad_b]}"
            wrong_pair = f"{names[good_i]} and {names[bad_a]}"
            opts = [names[0], names[1], names[2], wrong_pair, correct_pair]
            ans_idx = 4
            text = (
                f"{names[0]} has cards {hands[0][0]}, {hands[0][1]}, and {hands[0][2]}; "
                f"{names[1]} has cards {hands[1][0]}, {hands[1][1]}, and {hands[1][2]}; and "
                f"{names[2]} has cards {hands[2][0]}, {hands[2][1]}, and {hands[2][2]}. "
                f"Using +, -, ×, ÷ and each of their own three cards once, who <b>cannot</b> obtain <b>{target}</b>?"
            )
            expl = (
                f"{names[good_i]} can make {target} with {sols_int[good_i]}, whereas neither {names[bad_a]} "
                f"({hands[bad_a]}) nor {names[bad_b]} ({hands[bad_b]}) can reach {target}. "
                f"So the correct choice is {correct_pair}."
            )
            check_cards_target(p_cards, target, exp_unsolv)
            return p_cards, target, exp_unsolv, opts, ans_idx, text, expl

    raise RuntimeError("Could not generate 3-card problem")


def q_2002_21(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Making a Target Number with Three Digit Cards", "Based on 2002, Problem 21")

    p0 = [("Alex", (7, 2, 4)), ("Martha", (6, 5, 1)), ("Fred", (8, 3, 9))]
    check_cards_target(p0, 20, ["Martha"])
    if include_orig:
        d.problem(
            "Original 2002 #21.",
            "The digits from 1 to 9 are written on 9 cards. Alex has the digits 7, 2 and 4; Martha has the digits "
            "6, 5 and 1; and Fred has 8, 3 and 9. Each of them uses some of the four basic operations + (addition), "
            "- (subtraction), × (multiplication), ÷ (division), and each of his own cards exactly once. "
            "Who cannot obtain 20 as a result?",
            choices=["Alex", "Martha", "Fred", "All can get 20", "Alex and Martha"],
            choice_cols=3,
        )
        key.append((
            "2002 #21",
            "B",
            "Alex can make 20 with (7 - 2) × 4 = 20. Fred can make 20 with 8 + 3 + 9 = 20. "
            "With Martha's cards (6, 5, 1), no combination of +, -, ×, ÷ gives 20 (the closest results are "
            "6 × (5 - 1) = 24 and 5 × (6 - 1) = 25). So Martha cannot obtain 20.",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2, 3]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        p_cards, target, exp_unsolv, opts, ans_idx, text, expl = _generate_dynamic_cards_problem(rng, mode=m)
        check_cards_target(p_cards, target, exp_unsolv)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_21

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
