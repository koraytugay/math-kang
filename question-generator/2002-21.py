# Model: argon
"""Math Kangaroo 2002, Problem #21 - Question Generator."""
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
QUESTION_ID = (2002, 21)


def can_reach_target_3cards(cards, target):
    """Return a string formula if the 3 cards can make `target` using +, -, *, / (exact division) and parentheses, else None."""
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
    unsolvable = [name for name, cards in players_cards if can_reach_target_3cards(cards, target) is None]
    assert unsolvable == expected_unsolvable_names, (
        f"For target={target}, expected unsolvable={expected_unsolvable_names}, got {unsolvable}"
    )


def q_2002_21(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Making a Target Number with Three Digit Cards", "Based on 2002, Problem 21")

    # Original 2002 #21: Alex (7,2,4), Martha (6,5,1), Fred (8,3,9), target = 20 -> Martha cannot get 20 (B)
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

    practices = [
        # Practice .1: Target 18. Leo (9, 4, 2) -> (9-2)*? No, 9*4/2 = 18! Mia (7, 5, 1) -> cannot get 18! Noah (6, 8, 4) -> 6+8+4=18. Answer: B (Mia)
        (
            [("Leo", (9, 4, 2)), ("Mia", (7, 5, 1)), ("Noah", (6, 8, 4))],
            18,
            ["Mia"],
            ["Leo", "Mia", "Noah", "All can get 18", "Leo and Noah"],
            1,
            "Three friends each have 3 digit cards: Leo has 9, 4, and 2; Mia has 7, 5, and 1; and Noah has 6, 8, and 4. "
            "Using the operations +, -, ×, ÷ and each of their own three cards once, who <b>cannot</b> obtain <b>18</b> as a result?",
            "Leo can make 18 as (9 × 4) ÷ 2 = 18. Noah can make 18 as 6 + 8 + 4 = 18. "
            "Mia's cards (7, 5, 1) can make 13, 21, 28, 34, 35, 36, or 42, but never 18. So Mia cannot obtain 18.",
        ),
        # Practice .2: Target 15. Anna (8, 4, 1) -> cannot get 15! Ben (6, 3, 2) -> 6*3-? No: (6+2)*? Wait: 6*2+3 = 15! Clara (9, 5, 1) -> 9+5+1 = 15! Answer: A (Anna)
        (
            [("Anna", (8, 4, 1)), ("Ben", (6, 3, 2)), ("Clara", (9, 5, 1))],
            15,
            ["Anna"],
            ["Anna", "Ben", "Clara", "All can get 15", "Ben and Clara"],
            0,
            "Anna has cards 8, 4, and 1; Ben has cards 6, 3, and 2; and Clara has cards 9, 5, and 1. "
            "Each person uses +, -, ×, ÷ and all three of their own cards exactly once. Who <b>cannot</b> obtain <b>15</b>?",
            "Ben can get 15 with 6 × 2 + 3 = 15, and Clara can get 15 with 9 + 5 + 1 = 15. "
            "With Anna's cards (8, 4, 1), no combination of operations produces 15. So the answer is Anna.",
        ),
        # Practice .3: Target 24. Dan (8, 2, 1) -> 8*(2+1)=24. Eva (9, 7, 8) -> 9+7+8=24. Finn (5, 4, 2) -> cannot get 24! Answer: C (Finn)
        (
            [("Dan", (8, 2, 1)), ("Eva", (9, 7, 8)), ("Finn", (5, 4, 2))],
            24,
            ["Finn"],
            ["Dan", "Eva", "Finn", "All can get 24", "Dan and Eva"],
            2,
            "Dan has cards 8, 2, and 1; Eva has cards 9, 7, and 8; and Finn has cards 5, 4, and 2. "
            "Using +, -, ×, ÷ and each of their own three cards once, who <b>cannot</b> obtain <b>24</b>?",
            "Dan can get 24 with 8 × (2 + 1) = 24. Eva can get 24 with 9 + 7 + 8 = 24. "
            "Finn's cards (5, 4, 2) can make 5 × 4 + 2 = 22 or (5 + 2) × 4 = 28, but never 24. So Finn cannot obtain 24.",
        ),
        # Practice .4: Target 16. Ruby (8, 6, 4) -> 8*6/4 = 12, 8+6+4=18, (8-4)*6=24, (6-4)*8=16!
        # Sam (5, 3, 2) -> (5+3)*2 = 16! Toby (9, 4, 3) -> 9+4+3 = 16! All can get 16 -> Answer: D
        (
            [("Ruby", (8, 6, 4)), ("Sam", (5, 3, 2)), ("Toby", (9, 4, 3))],
            16,
            [],
            ["Ruby", "Sam", "Toby", "All can get 16", "Ruby and Sam"],
            3,
            "Ruby has cards 8, 6, and 4; Sam has cards 5, 3, and 2; and Toby has cards 9, 4, and 3. "
            "Using +, -, ×, ÷ and each of their three cards once, who <b>cannot</b> obtain <b>16</b>?",
            "Ruby can make 16 with 8 × (6 - 4) = 16. Sam can make 16 with (5 + 3) × 2 = 16. "
            "Toby can make 16 with 9 + 4 + 3 = 16. Therefore, all three of them can obtain 16!",
        ),
    ]

    for idx, (p_cards, target, exp_unsolv, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
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
