# Model: argon
"""Math Kangaroo 2003, Problem #17 - Question Generator."""
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
QUESTION_ID = (2003, 17)


def fig_barcode():
    w, h = 88, 36

    def draw(c, x, y):
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        # Left group: wide, narrow, wide
        c.rect(x + 4, y + 4, 6, 28, stroke=0, fill=1)
        c.rect(x + 15, y + 4, 2.2, 28, stroke=0, fill=1)
        c.rect(x + 22, y + 4, 6, 28, stroke=0, fill=1)
        # Dots in middle
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 41, y + 16, ". . . . .")
        # Right group: narrow, wide, wide
        c.rect(x + 56, y + 4, 2.2, 28, stroke=0, fill=1)
        c.rect(x + 63, y + 4, 6, 28, stroke=0, fill=1)
        c.rect(x + 74, y + 4, 6, 28, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_barcode(total_bars, white_minus_wide, choices, ans_idx):
    assert total_bars % 2 == 1, "Total bars must be odd when starting and ending with black"
    n_black = (total_bars + 1) // 2
    n_white = (total_bars - 1) // 2
    n_wide = n_white - white_minus_wide
    n_narrow = n_black - n_wide
    assert n_wide > 0 and n_narrow > 0
    matches = [i for i, ch in enumerate(choices) if int(ch) == n_narrow]
    assert matches == [ans_idx], f"Barcode narrow={n_narrow}, choices={choices}, ans_idx={ans_idx}"


def q_2003_17(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Alternating Black & White Barcode", "Based on 2003, Problem 17")

    opts0 = ["1", "2", "3", "4", "5"]
    check_barcode(17, 3, opts0, 3)
    if include_orig:
        d.problem(
            "Original 2003 #17.",
            "A bar code is formed using 17 black and white bars (the first and last bars are black). "
            "The black bars are two types: wide and narrow. The number of white bars is 3 more than the number "
            "of wide black bars. The number of narrow black bars is:",
            fig_barcode(),
            "right",
            opts0,
        )
        key.append((
            "2003 #17",
            "D",
            "Since the 17 bars alternate black and white and both the first and last bars are black, there are "
            "9 black bars and 8 white bars. The number of white bars (8) is 3 more than the wide black bars, "
            "so there are 8 - 3 = 5 wide black bars. That leaves 9 - 5 = 4 narrow black bars.",
        ))

    practices = [
        # Practice .1: 21 total bars -> 11 black, 10 white. White is 4 more than wide black -> wide = 6, narrow = 11 - 6 = 5 (Answer: E)
        (
            21, 4,
            ["1", "2", "3", "4", "5"],
            4,
            "A bar code is made of 21 alternating black and white bars, starting and ending with a black bar. "
            "Each black bar is either wide or narrow. The number of white bars is 4 more than the number of wide "
            "black bars. How many narrow black bars are there?",
            "Out of 21 alternating bars starting and ending with black, there are 11 black bars and 10 white bars. "
            "Since 10 white bars is 4 more than the wide black bars, there are 10 - 4 = 6 wide black bars, "
            "leaving 11 - 6 = 5 narrow black bars.",
        ),
        # Practice .2: 19 total bars -> 10 black, 9 white. White is 2 more than wide black -> wide = 7, narrow = 10 - 7 = 3 (Answer: C)
        (
            19, 2,
            ["1", "2", "3", "4", "5"],
            2,
            "A label has a bar code of 19 alternating black and white bars (both the first and last bars are black). "
            "The number of white bars is 2 more than the number of wide black bars. "
            "How many narrow black bars are in the bar code?",
            "With 19 alternating bars beginning and ending with black, there are 10 black bars and 9 white bars. "
            "There are 9 - 2 = 7 wide black bars, so there are 10 - 7 = 3 narrow black bars.",
        ),
        # Practice .3: 15 total bars -> 8 black, 7 white. White is 1 more than wide black -> wide = 6, narrow = 8 - 6 = 2 (Answer: B)
        (
            15, 1,
            ["1", "2", "3", "4", "5"],
            1,
            "A ticket bar code has 15 alternating black and white bars, where the first and last bars are black. "
            "The number of white bars is 1 more than the number of wide black bars. "
            "How many narrow black bars are there?",
            "Among 15 alternating bars starting and ending with black, 8 are black and 7 are white. "
            "The number of wide black bars is 7 - 1 = 6, leaving 8 - 6 = 2 narrow black bars.",
        ),
        # Practice .4: 25 total bars -> 13 black, 12 white. White is 5 more than wide black -> wide = 7, narrow = 13 - 7 = 6 (Answer: D)
        (
            25, 5,
            ["3", "4", "5", "6", "7"],
            3,
            "A package bar code uses 25 alternating black and white bars (the first and last bars are black). "
            "The number of white bars is 5 more than the number of wide black bars. "
            "How many narrow black bars does the bar code have?",
            "Out of 25 alternating bars starting and ending with black, there are 13 black bars and 12 white bars. "
            "There are 12 - 5 = 7 wide black bars, which leaves 13 - 7 = 6 narrow black bars.",
        ),
    ]

    for idx, (t_bars, diff_w, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_barcode(t_bars, diff_w, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_barcode(),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2003_17

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
