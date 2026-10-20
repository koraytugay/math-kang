# Model: argon
"""Math Kangaroo 2007, Problem #3 - Question Generator."""
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
QUESTION_ID = (2007, 3)


def check_common_letters(w1, w2, choices, ans_idx):
    common = set(w1.upper()) & set(w2.upper())
    cnt = len(common)
    matches = [i for i, ch in enumerate(choices) if int(ch) == cnt]
    assert matches == [ans_idx], f"Common letters between {w1} and {w2}: {common} ({cnt}), choices={choices}, ans_idx={ans_idx}"


def q_2007_3(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Common Letters in Two Words", "Based on 2007, Problem 3")

    opts0 = ["1", "2", "3", "4", "5"]
    check_common_letters("KANGAROO", "PROBLEM", opts0, 1)
    if include_orig:
        d.problem(
            "Original 2007 #3.",
            "How many common letters do the words <b>KANGAROO</b> and <b>PROBLEM</b> have?",
            choices=opts0,
        )
        key.append((
            "2007 #3",
            "B",
            "The distinct letters in KANGAROO are {K, A, N, G, R, O}, and in PROBLEM are {P, R, O, B, L, E, M}. "
            "The letters that appear in both words are R and O, so they have 2 common letters.",
        ))

    practices = [
        # Practice .1: TRIANGLE and RECTANGLE -> {T, R, I, A, N, G, L, E} & {R, E, C, T, A, N, G, L} = {T, R, A, N, G, L, E} = 7 (Answer: D)
        (
            "TRIANGLE", "RECTANGLE",
            ["4", "5", "6", "7", "8"],
            3,
            "How many different letters do the words <b>TRIANGLE</b> and <b>RECTANGLE</b> have in common?",
            "The distinct letters of TRIANGLE are {T, R, I, A, N, G, L, E} and of RECTANGLE are {R, E, C, T, A, N, G, L}. "
            "They share the 7 letters T, R, A, N, G, L, and E.",
        ),
        # Practice .2: DOLPHIN and PENGUIN -> {D, O, L, P, H, I, N} & {P, E, N, G, U, I} = {P, I, N} = 3 (Answer: C)
        (
            "DOLPHIN", "PENGUIN",
            ["1", "2", "3", "4", "5"],
            2,
            "How many common letters do the words <b>DOLPHIN</b> and <b>PENGUIN</b> have?",
            "Checking each letter of DOLPHIN against PENGUIN: P, I, and N appear in both words. "
            "So they have 3 common letters.",
        ),
        # Practice .3: BALLOON and BANANA -> {B, A, L, O, N} & {B, A, N} = {B, A, N} = 3 (Answer: B)
        (
            "BALLOON", "BANANA",
            ["2", "3", "4", "5", "6"],
            1,
            "How many different letters appear in <b>both</b> the word <b>BALLOON</b> and the word <b>BANANA</b>?",
            "The distinct letters in BANANA are B, A, and N, and all three of them also appear in BALLOON. "
            "Counting distinct shared letters gives 3 common letters (B, A, and N).",
        ),
        # Practice .4: SUMMER and WINTER -> {S, U, M, E, R} & {W, I, N, T, E, R} = {E, R} = 2 (Answer: A)
        (
            "SUMMER", "WINTER",
            ["2", "3", "4", "5", "6"],
            0,
            "How many common letters do the words <b>SUMMER</b> and <b>WINTER</b> have?",
            "The letters in SUMMER are {S, U, M, E, R} and in WINTER are {W, I, N, T, E, R}. "
            "Only E and R appear in both words, giving 2 common letters.",
        ),
    ]

    for idx, (w1, w2, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_common_letters(w1, w2, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_3

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
