# Model: argon
"""Math Kangaroo 2002, Problem #4 - Question Generator."""
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
QUESTION_ID = (2002, 4)


SYMS = [lambda r, c: (r, c), lambda r, c: (c, -r), lambda r, c: (-r, -c), lambda r, c: (-c, r),
        lambda r, c: (r, -c), lambda r, c: (-c, -r), lambda r, c: (-r, c), lambda r, c: (c, r)]


def canon(cells):
    best = None
    for f in SYMS:
        pts = [f(r, c) for r, c in cells]
        mr = min(p[0] for p in pts); mc = min(p[1] for p in pts)
        key = tuple(sorted((p[0] - mr, p[1] - mc) for p in pts))
        best = key if best is None or key < best else best
    return best


def pieces_of(grid):
    d = {}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            d.setdefault(ch, []).append((r, c))
    return d


def check_cut(grid, options, answer):
    shapes = {canon(v) for v in pieces_of(grid).values()}
    bad = [i for i, o in enumerate(options) if canon(o) not in shapes]
    assert bad == [answer], (grid, bad, answer)


def fig_partition(grid, s=16):
    n_r, n_c = len(grid), len(grid[0])

    def draw(c, x, y):
        c.setLineWidth(1.4)
        top = y + n_r * s
        c.rect(x, y, n_c * s, n_r * s)
        for r in range(n_r):
            for col in range(n_c):
                if col + 1 < n_c and grid[r][col] != grid[r][col + 1]:
                    xx = x + (col + 1) * s
                    c.line(xx, top - r * s, xx, top - (r + 1) * s)
                if r + 1 < n_r and grid[r][col] != grid[r + 1][col]:
                    yy = top - (r + 1) * s
                    c.line(x + col * s, yy, x + (col + 1) * s, yy)
    return n_c * s, n_r * s, draw


def fig_poly(cells, s=13):
    rs = [p[0] for p in cells]; cs = [p[1] for p in cells]
    r0, c0 = min(rs), min(cs)
    cells = {(r - r0, c - c0) for r, c in cells}
    n_r = max(r for r, _ in cells) + 1; n_c = max(c for _, c in cells) + 1

    def draw(c, x, y):
        c.setLineWidth(1.2)
        top = y + n_r * s
        for r, col in cells:
            x0, y1 = x + col * s, top - r * s
            if (r - 1, col) not in cells: c.line(x0, y1, x0 + s, y1)
            if (r + 1, col) not in cells: c.line(x0, y1 - s, x0 + s, y1 - s)
            if (r, col - 1) not in cells: c.line(x0, y1, x0, y1 - s)
            if (r, col + 1) not in cells: c.line(x0 + s, y1, x0 + s, y1 - s)
    return n_c * s, n_r * s, draw


def cut_problem(grid, options, answer):
    check_cut(grid, options, answer)
    return vstack([fig_partition(grid), option_row([fig_poly(o) for o in options], gap=14)], gap=14)


def q_2002_4(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Cutting a square into pieces", "Based on 2002, Problem 4")
    if include_orig:
        orig = ["AABD", "ABBD", "CCBF", "EFFF"]
        opts = [[(0, 0)], [(0, 0), (0, 1)], [(0, 0), (0, 1), (1, 1)],
                [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)], [(0, 0), (1, 0), (2, 0), (2, 1)]]
        d.problem("Original 2002 #4.", "The square was cut along the lines. Which of the shapes below was "
                  "<b>not</b> obtained this way?", cut_problem(orig, opts, 3), "below")
        key.append(("2002 #4", "D", "The pieces are: 1 small square, 2 dominoes, an L of 3, a T of 4 and an L of 4. There is no U-shaped piece."))

    g = ["AAAB", "CDAB", "CDDD", "CEEF"]
    o = [[(0, 0)], [(0, 0), (0, 1), (0, 2), (1, 1)], [(0, 0), (0, 1), (0, 2)],
         [(0, 0), (1, 0), (2, 0), (0, 1)], [(0, 0), (1, 0)]]
    d.problem(f"Practice {set_num}.1", "The square was cut along the lines. Which of the shapes below was "
              "<b>not</b> obtained this way?", cut_problem(g, o, 1), "below")
    key.append((f"{set_num}.1", "B", "Pieces: two L-shapes of 4, a straight 3, two dominoes, one small square. No T-shape."))

    g = ["AABBB", "ACCBE", "ACDDE", "FCDEE", "FFDGG"]
    o = [[(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1)], [(0, 1), (0, 2), (1, 0), (1, 1)],
         [(0, 1), (1, 0), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)]]
    d.problem(f"Practice {set_num}.2", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 2), "below")
    key.append((f"{set_num}.2", "C", "Pieces: four L-shapes of 4, one T, one L of 3, one domino. There is no zig-zag (S) piece."))

    g = ["AAABB", "ACCCB", "DDCEB", "DFFEE", "DFGGG"]
    o = [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 0), (2, 0)],
         [(0, 0), (0, 1), (1, 0), (2, 0)], [(0, 0), (0, 1), (1, 0), (1, 1)]]
    d.problem(f"Practice {set_num}.3", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 4), "below")
    key.append((f"{set_num}.3", "E", "Pieces: three L-shapes of 4, one T, two L-shapes of 3, one straight 3. No 2x2 square."))

GENERATE = q_2002_4

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
