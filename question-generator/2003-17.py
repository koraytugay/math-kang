# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #17 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2003, 17)


def fig_barcode(left_pat=("W", "N", "W"), right_pat=("N", "W", "W")):
    w, h = 92, 36

    def draw(c, x, y):
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        cx = x + 4
        for b in left_pat:
            bw = 5.8 if b == "W" else 2.2
            c.rect(cx, y + 4, bw, 28, stroke=0, fill=1)
            cx += bw + 4.5
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 45, y + 16, ". . . . .")
        cx = x + 58
        for b in right_pat:
            bw = 5.8 if b == "W" else 2.2
            c.rect(cx, y + 4, bw, 28, stroke=0, fill=1)
            cx += bw + 4.5
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def solve_barcode(total_bars, n_wide, n_narrow):
    """Exact verification of an alternating black/white barcode starting and ending with black."""
    assert n_wide > 0 and n_narrow > 0
    n_black = n_wide + n_narrow
    n_white = n_black - 1
    assert total_bars == n_black + n_white, f"Total bars mismatch: {total_bars} != {n_black} + {n_white}"
    return n_black, n_white


def check_barcode(total_bars, white_minus_wide, choices, ans_idx, query="narrow"):
    assert total_bars % 2 == 1, "Total bars must be odd when starting and ending with black"
    n_black = (total_bars + 1) // 2
    n_white = (total_bars - 1) // 2
    n_wide = n_white - white_minus_wide
    n_narrow = n_black - n_wide
    solve_barcode(total_bars, n_wide, n_narrow)
    target = {"narrow": n_narrow, "wide": n_wide, "total": total_bars}[query]
    matches = [i for i, ch in enumerate(choices) if int(ch) == target]
    assert matches == [ans_idx], f"Barcode target={target}, choices={choices}, ans_idx={ans_idx}"


CONTEXT_NOUNS = [
    "A product bar code",
    "A library label bar code",
    "A train ticket bar code",
    "A parcel bar code",
    "A badge bar code",
]


def _generate_dynamic_barcode_problem(rng, mode=0):
    """Procedurally generate an alternating black-and-white barcode problem."""
    ctx = rng.choice(CONTEXT_NOUNS)
    left_pat = tuple(rng.choice(["W", "N"]) for _ in range(3))
    right_pat = tuple(rng.choice(["W", "N"]) for _ in range(3))
    m = mode % 3

    if m == 0:
        # Mode 0: Given total_bars and (n_white - n_wide), find n_narrow
        while True:
            n_black = rng.randint(8, 16)
            total_bars = 2 * n_black - 1
            n_white = n_black - 1
            diff_w = rng.randint(1, n_white - 2)
            if (total_bars, diff_w) != (17, 3):
                break
        n_wide = n_white - diff_w
        n_narrow = n_black - n_wide
        query = "narrow"
        ans_val = n_narrow
        text = (
            f"{ctx} is formed using {total_bars} alternating black and white bars (the first and last bars are black). "
            f"Each black bar is either wide or narrow. The number of white bars is {diff_w} more than the number of "
            f"wide black bars. How many <b>narrow black bars</b> are there?"
        )
        expl = (
            f"Out of {total_bars} alternating bars starting and ending with black, there are {n_black} black bars "
            f"and {n_white} white bars. Since {n_white} white bars is {diff_w} more than the wide black bars, "
            f"there are {n_white} - {diff_w} = {n_wide} wide black bars, leaving {n_black} - {n_wide} = {n_narrow} narrow black bars."
        )
    elif m == 1:
        # Mode 1: Given total_bars and (n_white - n_wide), ask for n_wide (or give n_white - n_narrow and ask for n_narrow)
        n_black = rng.randint(8, 15)
        total_bars = 2 * n_black - 1
        n_white = n_black - 1
        diff_n = rng.randint(2, n_white - 2)
        n_narrow = n_white - diff_n
        n_wide = n_black - n_narrow
        diff_w = n_white - n_wide
        query = "narrow"
        ans_val = n_narrow
        text = (
            f"{ctx} has {total_bars} alternating black and white bars, where the first and last bars are black. "
            f"Every black bar is either wide or narrow. If there are {n_wide} wide black bars, how many "
            f"<b>narrow black bars</b> are in the bar code?"
        )
        expl = (
            f"Among {total_bars} alternating bars starting and ending with black, there are ({total_bars} + 1) ÷ 2 = "
            f"{n_black} black bars and {n_white} white bars. Since {n_wide} of the black bars are wide, "
            f"the remaining {n_black} - {n_wide} = {n_narrow} black bars are narrow."
        )
    else:
        # Mode 2: Given n_wide and n_narrow black bars, find total bars (black + white) in the barcode
        n_wide = rng.randint(4, 9)
        n_narrow = rng.randint(3, 8)
        n_black = n_wide + n_narrow
        n_white = n_black - 1
        total_bars = n_black + n_white
        diff_w = n_white - n_wide
        query = "total"
        ans_val = total_bars
        text = (
            f"{ctx} is made of alternating black and white bars, starting and ending with a black bar. "
            f"It contains {n_wide} wide black bars and {n_narrow} narrow black bars. "
            f"How many bars (black and white altogether) are in the bar code?"
        )
        expl = (
            f"There are {n_wide} + {n_narrow} = {n_black} black bars in total. Because the bars alternate and both "
            f"the first and last bars are black, there is 1 fewer white bar than black bars: {n_black} - 1 = {n_white} "
            f"white bars. Altogether there are {n_black} + {n_white} = {total_bars} bars."
        )

    cands = {ans_val}
    for delta in [-2, -1, 1, 2, 3, -3, 4]:
        if len(cands) >= 5:
            break
        v = ans_val + delta
        if v >= 1:
            cands.add(v)
    vals = sorted(list(cands))[:5]
    if ans_val not in vals:
        vals[-1] = ans_val
        vals.sort()
    opts = [str(v) for v in vals]
    ans_idx = vals.index(ans_val)
    check_barcode(total_bars, diff_w, opts, ans_idx, query=query)
    return total_bars, diff_w, opts, ans_idx, query, left_pat, right_pat, text, expl


def q_2003_17(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Alternating Black & White Barcode", "Based on 2003, Problem 17")

    opts0 = ["1", "2", "3", "4", "5"]
    check_barcode(17, 3, opts0, 3, query="narrow")
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

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        t_bars, diff_w, opts, ans_idx, query, l_pat, r_pat, text, expl = _generate_dynamic_barcode_problem(rng, mode=m)
        check_barcode(t_bars, diff_w, opts, ans_idx, query=query)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_barcode(l_pat, r_pat),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_17

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
