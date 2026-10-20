# Model: argon
"""Math Kangaroo 2003, Problem #14 - Question Generator."""
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
QUESTION_ID = (2003, 14)


def shoelace(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2


def fig_letter(gw, gh, polys, s=15):
    def draw(c, x, y):
        c.setLineWidth(0.6)
        for i in range(gw + 1): c.line(x + i * s, y, x + i * s, y + gh * s)
        for j in range(gh + 1): c.line(x, y + j * s, x + gw * s, y + j * s)
        c.setLineWidth(2.2)
        for pts in polys:
            pa = c.beginPath(); pa.moveTo(x + pts[0][0] * s, y + pts[0][1] * s)
            for q in pts[1:]: pa.lineTo(x + q[0] * s, y + q[1] * s)
            pa.close()
            c.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.85))
            c.drawPath(pa, stroke=1, fill=1)
        c.setFillColor(colors.black)
    return gw * s, gh * s, draw


def letter_area(polys):
    return sum(shoelace(p) for p in polys)


def q_2003_14(d, key, set_num=6, include_orig=True):
    d.heading(f"Set {set_num} - Area of a letter on squared paper", "Based on 2003, Problem 14")
    q = "If the side of each little square is 1 cm, what is the area of the letter %s (in square cm)?"
    if include_orig:
        N = [[(1, 0), (2, 0), (2, 6), (1, 6)], [(5, 0), (6, 0), (6, 6), (5, 6)], [(2, 6), (3, 6), (5, 0), (4, 0)]]
        assert letter_area(N) == 18
        d.problem("Original 2003 #14.", q % "N", fig_letter(7, 6, N), "right", [14, 15, 16, 17, 18])
        key.append(("2003 #14", "E", "Each side bar is 6. The slanted part is a parallelogram 1 wide and 6 tall = 6 (cut-off triangles fit together). 6+6+6 = 18."))

    Z = [[(1, 6), (6, 6), (6, 7), (1, 7)], [(1, 0), (6, 0), (6, 1), (1, 1)], [(4, 6), (6, 6), (3, 1), (1, 1)]]
    assert letter_area(Z) == 20
    d.problem(f"Practice {set_num}.1", q % "Z", fig_letter(7, 7, Z, 14), "right", [16, 18, 20, 22, 24])
    key.append((f"{set_num}.1", "C", "Top bar 5 + bottom bar 5 + slanted part (2 wide, 5 tall) 10 = 20."))

    V = [[(1, 5), (3, 5), (4, 2), (5, 5), (7, 5), (5, 0), (3, 0)]]
    assert letter_area(V) == 17
    d.problem(f"Practice {set_num}.2", q % "V", fig_letter(8, 5, V), "right", [15, 16, 17, 18, 20])
    key.append((f"{set_num}.2", "C", "Without the notch the shape is a 2 x 5 rectangle (10) plus two side triangles (each half of 2 x 5 = 5), so 20. The white triangle notch at the top is half of 2 x 3 = 3. 20 - 3 = 17."))

    M = [[(1, 0), (2, 0), (2, 5), (1, 5)], [(8, 0), (9, 0), (9, 5), (8, 5)],
         [(2, 5), (5, 2), (8, 5), (8, 3), (5, 0), (2, 3)]]
    assert letter_area(M) == 22
    d.problem(f"Practice {set_num}.3", q % "M", fig_letter(10, 5, M, 14), "right", [18, 20, 22, 24, 26])
    key.append((f"{set_num}.3", "C", "Two side bars: 5 + 5 = 10. The middle V is two slanted strips, each 3 across and 2 tall = 6. 10 + 6 + 6 = 22."))

GENERATE = q_2003_14

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
