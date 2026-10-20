# Model: argon
"""Math Kangaroo 2002, Problem #9 - Question Generator."""
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
QUESTION_ID = (2002, 9)


def fig_balance(left, right, tilt):
    """left/right: lists of radii; tilt: +1 right side down, -1 left down, 0 level."""
    W, H = 220, 95

    def draw(c, x, y):
        cx = x + W / 2
        c.setFillColor(GRAY); c.ellipse(cx - 32, y, cx + 32, y + 8, stroke=0, fill=1)
        c.setFillColor(colors.black); c.setLineWidth(1.6)
        piv = y + 34
        c.line(cx, y + 4, cx, piv)
        ang = -0.09 * tilt
        L = 80
        lx, ly = cx - L * math.cos(ang), piv - L * math.sin(ang)
        rx, ry = cx + L * math.cos(ang), piv + L * math.sin(ang)
        c.setLineWidth(2.2); c.line(lx, ly, rx, ry)
        c.setLineWidth(1.2)
        for px, py, items in ((lx, ly, left), (rx, ry, right)):
            ty = py + 16
            c.line(px, py, px, ty)
            c.line(px - 36, ty, px + 36, ty)
            c.line(px - 36, ty, px - 42, ty + 8); c.line(px + 36, ty, px + 42, ty + 8)
            total = sum(2 * r for r in items) + 1.5 * (len(items) - 1)
            ox = px - total / 2
            for r in items:
                if r >= 6:
                    c.setFillColor(GRAY if r < 8 else colors.Color(0.55, 0.55, 0.55))
                    c.circle(ox + r, ty + r, r, stroke=1, fill=1)
                else:
                    c.setFillColor(colors.white)
                    c.circle(ox + r, ty + r, r, stroke=1, fill=1)
                c.setFillColor(colors.black)
                ox += 2 * r + 1.5
    return W, H, draw


def q_2002_9(d, key, set_num=3, include_orig=True):
    d.heading(f"Set {set_num} - Balance scales", "Based on 2002, Problem 9")
    if include_orig:
        d.problem("Original 2002 #9.", "On one plate of a balance there are 6 oranges (small circles) and on the "
                  "other there are melons (big circles). When we put one more melon, exactly like the others, on the "
                  "orange plate, the balance is level. The weight of one melon is the same as:",
                  fig_balance([4] * 6, [9, 9], 1), "right",
                  ["2 oranges", "3 oranges", "4 oranges", "5 oranges", "6 oranges"], 3)
        key.append(("2002 #9", "E", "6 oranges + 1 melon = 2 melons. Take one melon off each side: 6 oranges = 1 melon."))

    d.problem(f"Practice {set_num}.1", "On one plate there are 8 plums (small circles) and on the other 3 lemons "
              "(gray circles). When we put one more lemon on the plum plate, the balance is level. "
              "One lemon weighs the same as:",
              fig_balance([4] * 8, [7, 7, 7], 1), "right",
              ["2 plums", "3 plums", "4 plums", "5 plums", "8 plums"], 3)
    key.append((f"{set_num}.1", "C", "8 plums + 1 lemon = 3 lemons, so 8 plums = 2 lemons, so 1 lemon = 4 plums."))

    d.problem(f"Practice {set_num}.2", "On one plate there are 10 cherries (small circles) and on the other 4 apples "
              "(gray circles). When we put 2 more apples on the cherry plate, the balance is level. "
              "One apple weighs the same as:",
              fig_balance([3.4] * 10, [7, 7, 7, 7], 1), "right",
              ["2 cherries", "3 cherries", "4 cherries", "5 cherries", "10 cherries"], 3)
    key.append((f"{set_num}.2", "D", "10 cherries + 2 apples = 4 apples, so 10 cherries = 2 apples, so 1 apple = 5 cherries."))

    d.problem(f"Practice {set_num}.3", "The balance is level. On the left plate there is 1 melon (big circle) and 3 "
              "oranges; on the right plate there are 9 oranges. How many oranges weigh the same as "
              "<b>2 melons</b>?",
              fig_balance([9, 4, 4, 4], [4] * 9, 0), "right", [6, 8, 9, 12, 18])
    key.append((f"{set_num}.3", "D", "Take 3 oranges off each side: 1 melon = 6 oranges, so 2 melons = 12 oranges."))

GENERATE = q_2002_9

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
