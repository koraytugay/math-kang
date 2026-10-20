# Model: argon
"""Math Kangaroo 2002, Problem #7 - Question Generator."""
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
QUESTION_ID = (2002, 7)


def tok_path(tokens):
    """Yield drawing segments and bbox for a skyline token list."""
    x = y = 0
    pts = [(0, 0)]
    segs = []
    for t in tokens:
        k = t[0]
        if k == "H":
            segs.append(("L", x, y, x + t[1], y)); x += t[1]
        elif k == "V":
            segs.append(("L", x, y, x, y + t[1])); y += t[1]
        elif k == "D":
            segs.append(("L", x, y, x + t[1], y + t[2])); x += t[1]; y += t[2]
        elif k == "A":
            w = t[1]; hh = w * 0.42
            segs.append(("C", x, y, w, hh)); pts.append((x, y + hh)); x += w
        pts.append((x, y))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return segs, (min(xs), min(ys), max(xs), max(ys))


def fig_tokens(tokens, sc, lw=1.3):
    segs, (x0, y0, x1, y1) = tok_path(tokens)

    def draw(c, x, y):
        c.setLineWidth(lw)
        for s in segs:
            if s[0] == "L":
                c.line(x + (s[1] - x0) * sc, y + (s[2] - y0) * sc, x + (s[3] - x0) * sc, y + (s[4] - y0) * sc)
            else:
                _, ax, ay, w, hh = s
                X, Y = x + (ax - x0) * sc, y + (ay - y0) * sc
                p = c.beginPath(); p.moveTo(X, Y)
                p.curveTo(X, Y + hh * sc * 4 / 3, X + w * sc, Y + hh * sc * 4 / 3, X + w * sc, Y)
                c.drawPath(p, stroke=1, fill=0)
    return (x1 - x0) * sc, (y1 - y0) * sc, draw


def _tok_match(t_sky, t_pc, is_end):
    if t_sky[0] != t_pc[0]:
        return False
    kind = t_sky[0]
    if kind == "A":
        return t_sky[1] == t_pc[1]
    if kind in ("H", "V"):
        if not is_end:
            return t_sky[1] == t_pc[1]
        return (t_sky[1] > 0 and t_pc[1] > 0 and abs(t_pc[1]) <= abs(t_sky[1])) or (
            t_sky[1] < 0 and t_pc[1] < 0 and abs(t_pc[1]) <= abs(t_sky[1])
        )
    if kind == "D":
        if not is_end:
            return t_sky[1] == t_pc[1] and t_sky[2] == t_pc[2]
        return (
            t_sky[1] * t_pc[2] == t_sky[2] * t_pc[1]
            and (t_sky[1] > 0) == (t_pc[1] > 0)
            and (t_sky[2] > 0) == (t_pc[2] > 0)
            and abs(t_pc[1]) <= abs(t_sky[1])
        )
    return False


def is_subpath_of_skyline(sky, pc):
    m = len(pc)
    for i in range(len(sky) - m + 1):
        if all(_tok_match(sky[i + j], pc[j], j == 0 or j == m - 1) for j in range(m)):
            return True
    return False


def skyline_problem(sky, pieces, sc, ans_idx=None):
    if ans_idx is not None:
        cannot_belong = [i for i, p in enumerate(pieces) if not is_subpath_of_skyline(sky, p)]
        assert cannot_belong == [ans_idx], f"Skyline check failed: expected {[ans_idx]}, got {cannot_belong}"
    return vstack([fig_tokens(sky, sc), option_row([fig_tokens(p, sc) for p in pieces], gap=26)], gap=18)


def q_2002_7(d, key, set_num=2, include_orig=True):
    d.heading(f"Set {set_num} - Pieces of a skyline", "Based on 2002, Problem 7")
    if include_orig:
        sky = [("A", 40), ("A", 40), ("H", 42), ("V", 40), ("H", 83), ("V", 42), ("D", 42, 43), ("D", 43, -43),
               ("V", -42), ("H", 83), ("V", -40), ("H", 42), ("D", 40, 40), ("D", 40, -40), ("V", 80), ("A", 40),
               ("A", 40), ("V", -80), ("H", 40), ("V", 40), ("H", 45), ("V", 85), ("H", 15), ("V", -85), ("H", 40),
               ("V", -40), ("H", 40)]
        pcs = [[("V", -30), ("H", 40), ("V", -40), ("H", 30)],
               [("D", 40, -40), ("V", 80), ("A", 40)],
               [("A", 40), ("V", -50), ("H", 25), ("V", 50), ("A", 40)],
               [("H", 40), ("V", -40), ("H", 42), ("D", 40, 40)],
               [("A", 40), ("A", 40), ("V", -50)]]
        d.problem("Original 2002 #7.", "Far away we see the skyline of a castle. Which of the pieces "
                  "<b>cannot</b> belong to the skyline?", skyline_problem(sky, pcs, 0.36, ans_idx=2), "below")
        key.append(("2002 #7", "C", "Wherever there are two arches, they sit right next to each other. There is never a U-shaped dip between two arches."))

    sky = [("H", 60), ("A", 35), ("A", 35), ("H", 40), ("V", 75), ("H", 30), ("D", 25, 35), ("D", 25, -35),
           ("H", 30), ("V", -75), ("H", 40), ("V", 110), ("H", 20), ("V", -110), ("H", 60)]
    pcs = [[("V", 50), ("D", 25, 35), ("D", 25, -35), ("H", 30)],
           [("D", 25, -35), ("H", 30), ("V", -75), ("H", 25)],
           [("A", 35), ("A", 35), ("H", 40), ("V", 50)],
           [("V", 40), ("H", 30), ("D", 25, 35)],
           [("H", 25), ("V", 110), ("H", 20), ("V", -110), ("H", 25)]]
    d.problem(f"Practice {set_num}.1", "Here is the skyline of a town. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.48, ans_idx=0), "below")
    key.append((f"{set_num}.1", "A", "In the skyline there is a flat part between the wall and the pointed roof. Piece A has the roof sitting straight on the wall."))

    sky = [("H", 50), ("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -15), ("H", 20),
           ("V", 15), ("H", 25), ("V", -50), ("H", 40), ("A", 50), ("H", 40), ("D", 35, 50), ("H", 40),
           ("D", 35, -50), ("H", 40)]
    pcs = [[("V", -30), ("H", 40), ("A", 50), ("H", 20)],
           [("A", 50), ("H", 40), ("D", 35, 50), ("H", 20)],
           [("H", 20), ("D", 35, -50), ("H", 40)],
           [("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50), ("H", 20)],
           [("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50)]]
    d.problem(f"Practice {set_num}.2", "Here is the skyline of a castle. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.42, ans_idx=4), "below")
    key.append((f"{set_num}.2", "E", "The castle wall has TWO notches at the top. Piece E shows a whole tower top with only one notch."))

    sky = [("H", 50), ("A", 30), ("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40), ("V", -60), ("H", 40),
           ("A", 60), ("H", 25), ("V", 90), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 50)]
    pcs = [[("A", 60), ("H", 25), ("V", 60)],
           [("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40)],
           [("V", 50), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 20)],
           [("A", 30), ("H", 25), ("V", -40)],
           [("V", -40), ("H", 40), ("A", 60)]]
    d.problem(f"Practice {set_num}.3", "Here is a skyline with a small arch, a tower and a dome. Which piece "
              "<b>cannot</b> belong to it?", skyline_problem(sky, pcs, 0.45, ans_idx=3), "below")
    key.append((f"{set_num}.3", "D", "After each arch the line goes flat and then UP. Piece D goes down after the arch."))

GENERATE = q_2002_7

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
