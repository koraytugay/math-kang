# Model: argon
"""Math Kangaroo 2003, Problem #9 - Question Generator."""
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
QUESTION_ID = (2003, 9)


def fig_brick(Wn, Hn, Dn, s=13):
    k = 0.45 * s  # oblique offset per depth unit
    w = Wn * s + Dn * k; h = Hn * s + Dn * k

    def draw(c, x, y):
        c.setLineWidth(0.9)
        c.setFillColor(colors.white)
        for i in range(Wn + 1):
            c.line(x + i * s, y, x + i * s, y + Hn * s)
        for j in range(Hn + 1):
            c.line(x, y + j * s, x + Wn * s, y + j * s)
        top = y + Hn * s
        for i in range(Wn + 1):  # top receding lines
            c.line(x + i * s, top, x + i * s + Dn * k, top + Dn * k)
        for d in range(Dn + 1):
            c.line(x + d * k, top + d * k, x + Wn * s + d * k, top + d * k)
        rx = x + Wn * s
        for j in range(Hn + 1):  # right side receding lines
            c.line(rx, y + j * s, rx + Dn * k, y + j * s + Dn * k)
        for d in range(Dn + 1):
            c.line(rx + d * k, y + d * k, rx + d * k, top + d * k)
        c.setLineWidth(1.5)
        p = c.beginPath()
        p.moveTo(x, y); p.lineTo(rx, y); p.lineTo(rx + Dn * k, y + Dn * k); p.lineTo(rx + Dn * k, top + Dn * k)
        p.lineTo(x + Dn * k, top + Dn * k); p.lineTo(x, top); p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(colors.black)
    return w, h, draw


def q_2003_9(d, key, set_num=4, include_orig=True):
    d.heading(f"Set {set_num} - Red outside, blue inside", "Based on 2003, Problem 9")
    if include_orig:
        d.problem("Original 2003 #9.", "Chris built the brick in the picture using red and blue cubes of the same "
                  "size. The outside of the brick is completely red, but all cubes used inside are blue. "
                  "How many blue cubes did Chris use?", fig_brick(5, 4, 4), "right", [12, 24, 36, 40, 48])
        key.append(("2003 #9", "A", "Brick is 5 x 4 x 4. Remove the outer layer: inside is 3 x 2 x 2 = 12 blue cubes."))

    d.problem(f"Practice {set_num}.1", "Maya built this brick (4 cubes wide, 4 cubes tall, 3 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did she use?",
              fig_brick(4, 4, 3), "right", [2, 4, 6, 8, 12])
    key.append((f"{set_num}.1", "B", "Inside is (4-2) x (4-2) x (3-2) = 2 x 2 x 1 = 4."))

    d.problem(f"Practice {set_num}.2", "Leo built this brick (6 cubes wide, 3 cubes tall, 4 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did he use?",
              fig_brick(6, 3, 4), "right", [4, 6, 8, 12, 16])
    key.append((f"{set_num}.2", "C", "Inside is (6-2) x (3-2) x (4-2) = 4 x 1 x 2 = 8."))

    d.problem(f"Practice {set_num}.3", "Anna built this brick (5 cubes wide, 3 cubes tall, 3 cubes deep). The outside "
              "is completely red and the cubes inside are blue. How many <b>red</b> cubes did she use?",
              fig_brick(5, 3, 3), "right", [30, 36, 39, 42, 45])
    key.append((f"{set_num}.3", "D", "Total = 5 x 3 x 3 = 45. Inside (blue) = 3 x 1 x 1 = 3. Red = 45 - 3 = 42."))

GENERATE = q_2003_9

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
