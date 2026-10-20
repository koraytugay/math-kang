# Model: argon
"""Math Kangaroo 2007, Problem #1 - Question Generator."""
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
QUESTION_ID = (2007, 1)


def valid_fork_groups(forks):
    """Given a list of forks (e.g. [(1, 2), (3, 4), (5, 6)]), return all valid tuples picking 1 per fork."""
    res = [()]
    for branch in forks:
        res = [prev + (item,) for prev in res for item in branch]
    return set(res)


def check_fork_road(forks, option_tuples, answer_idx):
    valid = valid_fork_groups(forks)
    good = [i for i, opt in enumerate(option_tuples) if tuple(opt) in valid]
    assert good == [answer_idx], (forks, good, answer_idx)


def fig_fork_road(forks):
    """Draw a walker on the left and a sequence of road forks with labels."""
    n = len(forks)
    seg_w = 88
    lead_w = 24
    walker_w = 24
    W = walker_w + lead_w + n * seg_w
    H = 54

    def draw(c, x, y):
        cy = y + H / 2
        c.setLineWidth(1.2)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.black)

        # Draw little walker on the left
        wx = x + 10
        c.circle(wx, cy + 11, 3.2, stroke=1, fill=0)  # head
        c.line(wx, cy + 7.8, wx, cy + 2)               # neck/torso
        c.line(wx - 6, cy + 5, wx + 6, cy + 8)         # arms
        p = c.beginPath()                              # skirt/dress
        p.moveTo(wx, cy + 2)
        p.lineTo(wx - 5, cy - 6)
        p.lineTo(wx + 5, cy - 6)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.line(wx - 2.5, cy - 6, wx - 2.5, cy - 12)    # left leg
        c.line(wx + 2.5, cy - 6, wx + 2.5, cy - 12)    # right leg

        # Road parameters
        rh = 5.5   # half-width of main road
        bh = 13.0  # vertical offset of top/bottom branch centerlines
        rx = x + walker_w

        # Initial straight road segment
        c.line(rx, cy + rh, rx + lead_w, cy + rh)
        c.line(rx, cy - rh, rx + lead_w, cy - rh)
        cx = rx + lead_w

        for branch in forks:
            # Outer boundary curves (top and bottom of road)
            f_len = 66
            s_len = seg_w - f_len
            mid = cx + f_len / 2
            end = cx + f_len

            # Top outer & inner walls of upper branch, bottom outer & inner walls of lower branch
            for sign in (+1, -1):
                # Outer wall: from cy + sign*rh up to cy + sign*(bh + 4.5) and back
                p_out = c.beginPath()
                p_out.moveTo(cx, cy + sign * rh)
                p_out.curveTo(cx + 16, cy + sign * rh, mid - 14, cy + sign * (bh + 4.5), mid, cy + sign * (bh + 4.5))
                p_out.curveTo(mid + 14, cy + sign * (bh + 4.5), end - 16, cy + sign * rh, end, cy + sign * rh)
                c.drawPath(p_out, stroke=1, fill=0)

                # Inner island wall: from (cx + 7, cy) to (mid, cy + sign*(bh - 4.5)) to (end - 7, cy)
                p_in = c.beginPath()
                p_in.moveTo(cx + 7, cy)
                p_in.curveTo(cx + 18, cy + sign * 2, mid - 12, cy + sign * (bh - 4.5), mid, cy + sign * (bh - 4.5))
                p_in.curveTo(mid + 12, cy + sign * (bh - 4.5), end - 18, cy + sign * 2, end - 7, cy)
                c.drawPath(p_in, stroke=1, fill=0)

            # White label boxes and bold labels at top (branch[0]) and bottom (branch[1])
            for idx_b, sign in ((0, +1), (1, -1)):
                ly = cy + sign * bh
                c.setFillColor(colors.white)
                c.rect(mid - 5.5, ly - 5.5, 11, 11, stroke=0, fill=1)
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(mid, ly - 3.5, str(branch[idx_b]))

            # Straight connector to next fork
            c.line(end, cy + rh, end + s_len, cy + rh)
            c.line(end, cy - rh, end + s_len, cy - rh)
            cx = end + s_len

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return W, H, draw


def q_2007_1(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Choosing paths along a road", "Based on 2007, Problem 1")

    # Original 2007 #1
    if include_orig:
        forks = [(1, 2), (3, 4), (5, 6)]
        opts = [(1, 2, 4), (2, 3, 4), (2, 3, 5), (1, 5, 6), (1, 2, 5)]
        check_fork_road(forks, opts, 2)
        d.problem(
            "Original 2007 #1.",
            "Zita walked from the left to the right and wrote the numbers she saw along the roads in her "
            "notepad. Which of the following groups of numbers could be the numbers written by Zita?",
            fig_fork_road(forks),
            "below",
            [f"{a}, {b} and {c}" for a, b, c in opts],
            choice_cols=3,
        )
        key.append((
            "2007 #1",
            "C",
            "At the 1st fork Zita picks 1 or 2; at the 2nd fork 3 or 4; at the 3rd fork 5 or 6. Only (2, 3 and 5) has one from each fork.",
        ))

    # Practice .1
    forks1 = [(1, 2), (3, 4), (5, 6)]
    opts1 = [(1, 2, 3), (1, 4, 6), (2, 3, 4), (1, 5, 6), (3, 4, 5)]
    check_fork_road(forks1, opts1, 1)
    d.problem(
        f"Practice {set_num}.1",
        "Leo walked from the left to the right along the roads and wrote down the three numbers he passed. "
        "Which group of numbers could Leo have written?",
        fig_fork_road(forks1),
        "below",
        [f"{a}, {b} and {c}" for a, b, c in opts1],
        choice_cols=3,
    )
    key.append((
        f"{set_num}.1",
        "B",
        "Leo must pick one from (1, 2), one from (3, 4), and one from (5, 6). Only (1, 4 and 6) picks one from each fork.",
    ))

    # Practice .2 (letters on the forks)
    forks2 = [("A", "B"), ("C", "D"), ("E", "F")]
    opts2 = [("A", "B", "E"), ("B", "C", "D"), ("A", "E", "F"), ("B", "D", "E"), ("C", "D", "F")]
    check_fork_road(forks2, opts2, 3)
    d.problem(
        f"Practice {set_num}.2",
        "Mia walked from left to right and wrote down the letters she passed along her path. "
        "Which three letters could Mia have written?",
        fig_fork_road(forks2),
        "below",
        [f"{a}, {b} and {c}" for a, b, c in opts2],
        choice_cols=3,
    )
    key.append((
        f"{set_num}.2",
        "D",
        "Mia picks A or B first, then C or D, then E or F. Only (B, D and E) has one letter from each fork.",
    ))

    # Practice .3 (twist: sum of the numbers along the road)
    forks3 = [(2, 5), (3, 6), (4, 8)]
    valid_sums = {a + b + c for a, b, c in valid_fork_groups(forks3)}  # {9, 13, 12, 16, 15, 19}
    sum_choices = [10, 11, 14, 16, 20]
    good_sums = [i for i, s in enumerate(sum_choices) if s in valid_sums]
    assert good_sums == [3], (valid_sums, good_sums)
    d.problem(
        f"Practice {set_num}.3",
        "Sam walked from left to right and <b>added up</b> the three numbers he passed along his road. "
        "Which of the following could be Sam's total?",
        fig_fork_road(forks3),
        "below",
        sum_choices,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "D",
        "Possible sums are 2+3+4=9, 2+6+4=12, 5+3+4=12, 2+3+8=13, 5+6+4=15, 2+6+8=16, 5+3+8=16, 5+6+8=19. From the choices, only 16 is possible (for example 2 + 6 + 8 = 16).",
    ))

GENERATE = q_2007_1

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
