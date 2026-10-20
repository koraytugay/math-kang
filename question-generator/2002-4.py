# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #4 - Question Generator."""
import os
import sys
import math
import random
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
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 4)

ROTS = [
    lambda r, c: (r, c),
    lambda r, c: (c, -r),
    lambda r, c: (-r, -c),
    lambda r, c: (-c, r),
]

SYMS = ROTS + [
    lambda r, c: (r, -c),
    lambda r, c: (-c, -r),
    lambda r, c: (-r, c),
    lambda r, c: (c, r),
]

NAMED_SHAPES = [
    ("a single 1×1 square", [(0, 0)]),
    ("a 1×2 domino", [(0, 0), (0, 1)]),
    ("a straight 1×3 bar", [(0, 0), (0, 1), (0, 2)]),
    ("a 3-square corner (L-tromino)", [(0, 0), (0, 1), (1, 1)]),
    ("a 2×2 square", [(0, 0), (0, 1), (1, 0), (1, 1)]),
    ("a straight 1×4 bar", [(0, 0), (0, 1), (0, 2), (0, 3)]),
    ("a 4-square L-shape", [(0, 0), (1, 0), (2, 0), (2, 1)]),
    ("a 4-square T-shape", [(0, 0), (0, 1), (0, 2), (1, 1)]),
    ("a 4-square zigzag (S/Z-shape)", [(0, 1), (0, 2), (1, 0), (1, 1)]),
    ("a 5-square U-shape", [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)]),
    ("a 5-square plus (+) shape", [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)]),
    ("a 5-square P-shape", [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]),
]


def canon(cells, transforms=SYMS):
    best = None
    for f in transforms:
        pts = [f(r, c) for r, c in cells]
        mr = min(p[0] for p in pts)
        mc = min(p[1] for p in pts)
        key = tuple(sorted((p[0] - mr, p[1] - mc) for p in pts))
        best = key if best is None or key < best else best
    return best


def is_connected_polyomino(cells):
    cell_set = set(cells)
    if not cell_set:
        return False
    start = next(iter(cell_set))
    visited = {start}
    queue = [start]
    while queue:
        r, c = queue.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (r + dr, c + dc)
            if nb in cell_set and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited) == len(cell_set)


def pieces_of(grid):
    d = {}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            d.setdefault(ch, []).append((r, c))
    return d


def check_cut(grid, options, answer):
    pcs = pieces_of(grid)
    for label, cells in pcs.items():
        assert is_connected_polyomino(cells), f"Disconnected piece {label} in grid {grid}"
    for opt in options:
        assert is_connected_polyomino(opt), f"Disconnected option polyomino {opt}"
    shapes_sym = {canon(v, SYMS) for v in pcs.values()}
    bad_sym = [i for i, o in enumerate(options) if canon(o, SYMS) not in shapes_sym]
    assert bad_sym == [answer], f"Expected unique unobtained shape at {answer}, got {bad_sym}"


def fig_partition(grid, s=16):
    n_r, n_c = len(grid), len(grid[0])

    def draw(c, x, y):
        c.setLineWidth(1.4)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        top = y + n_r * s
        c.rect(x, y, n_c * s, n_r * s, stroke=1, fill=1)
        for r in range(n_r):
            for col in range(n_c):
                if col + 1 < n_c and grid[r][col] != grid[r][col + 1]:
                    xx = x + (col + 1) * s
                    c.line(xx, top - r * s, xx, top - (r + 1) * s)
                if r + 1 < n_r and grid[r][col] != grid[r + 1][col]:
                    yy = top - (r + 1) * s
                    c.line(x + col * s, yy, x + (col + 1) * s, yy)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return n_c * s, n_r * s, draw


def fig_poly(cells, s=13):
    rs = [p[0] for p in cells]
    cs = [p[1] for p in cells]
    r0, c0 = min(rs), min(cs)
    norm_cells = {(r - r0, c - c0) for r, c in cells}
    n_r = max(r for r, _ in norm_cells) + 1
    n_c = max(c for _, c in norm_cells) + 1

    def draw(c, x, y):
        c.setLineWidth(1.2)
        c.setStrokeColor(colors.black)
        top = y + n_r * s
        for r, col in norm_cells:
            x0, y1 = x + col * s, top - r * s
            if (r - 1, col) not in norm_cells:
                c.line(x0, y1, x0 + s, y1)
            if (r + 1, col) not in norm_cells:
                c.line(x0, y1 - s, x0 + s, y1 - s)
            if (r, col - 1) not in norm_cells:
                c.line(x0, y1, x0, y1 - s)
            if (r, col + 1) not in norm_cells:
                c.line(x0 + s, y1, x0 + s, y1 - s)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return n_c * s, n_r * s, draw


def cut_problem(grid, options, answer):
    check_cut(grid, options, answer)
    return vstack([fig_partition(grid), option_row([fig_poly(o) for o in options], gap=14)], gap=14)


def _random_rotate_cells(rng, cells):
    f = rng.choice(ROTS)
    pts = [f(r, c) for r, c in cells]
    mr = min(p[0] for p in pts)
    mc = min(p[1] for p in pts)
    return sorted((p[0] - mr, p[1] - mc) for p in pts)


def _generate_random_partition_problem(rng, n_size=4):
    """Procedurally partition an n_size x n_size square into connected polyominoes of size 1..4
    such that at least 4 distinct canonical shapes exist, and construct 5 options (4 present + 1 absent).
    """
    shape_name_by_canon = {canon(cells, SYMS): name for name, cells in NAMED_SHAPES}

    while True:
        board = [[None] * n_size for _ in range(n_size)]
        unassigned = {(r, c) for r in range(n_size) for c in range(n_size)}
        piece_idx = 0
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while unassigned:
            start = min(unassigned)
            label = labels[piece_idx]
            piece_idx += 1
            target_sz = rng.choice([2, 3, 3, 4, 4, 4])
            cur = {start}
            unassigned.remove(start)
            board[start[0]][start[1]] = label
            while len(cur) < target_sz:
                frontier = []
                for r, c in cur:
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nb = (r + dr, c + dc)
                        if nb in unassigned and nb not in frontier:
                            frontier.append(nb)
                if not frontier:
                    break
                nxt = rng.choice(frontier)
                cur.add(nxt)
                unassigned.remove(nxt)
                board[nxt[0]][nxt[1]] = label

        grid = ["".join(row) for row in board]
        pcs = pieces_of(grid)
        # Group unique canonical shapes present in this partition
        present_by_canon = {}
        for cells in pcs.values():
            c_key = canon(cells, SYMS)
            if c_key not in present_by_canon:
                present_by_canon[c_key] = cells

        if len(present_by_canon) < 4:
            continue

        # Find candidate absent shapes from NAMED_SHAPES (preferring size 3 or 4)
        absent_candidates = [
            (name, cells)
            for name, cells in NAMED_SHAPES
            if len(cells) in (3, 4, 5) and canon(cells, SYMS) not in present_by_canon
        ]
        if not absent_candidates:
            continue

        chosen_present_keys = rng.sample(list(present_by_canon.keys()), 4)
        present_opts = [_random_rotate_cells(rng, present_by_canon[k]) for k in chosen_present_keys]
        absent_name, absent_cells = rng.choice(absent_candidates)
        absent_opt = _random_rotate_cells(rng, absent_cells)

        all_opts = present_opts + [absent_opt]
        order = list(range(5))
        rng.shuffle(order)
        shuffled_opts = [all_opts[i] for i in order]
        ans_idx = order.index(4)

        # Describe present pieces
        counts = {}
        for cells in pcs.values():
            c_key = canon(cells, SYMS)
            nm = shape_name_by_canon.get(c_key, f"a {len(cells)}-square piece")
            counts[nm] = counts.get(nm, 0) + 1
        desc_parts = [f"{cnt}× ({nm.replace('a ', '')})" if cnt > 1 else nm for nm, cnt in counts.items()]
        expl = (
            f"The {n_size}×{n_size} square is cut into {len(pcs)} pieces: "
            + ", ".join(desc_parts)
            + f". There is no piece shaped like {absent_name} ({LETTERS[ans_idx]})."
        )
        return grid, shuffled_opts, ans_idx, expl


def q_2002_4(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Cutting a square into pieces", "Based on 2002, Problem 4")
    if include_orig:
        orig = ["AABD", "ABBD", "CCBF", "EFFF"]
        opts = [
            [(0, 0)],
            [(0, 0), (0, 1)],
            [(0, 0), (0, 1), (1, 1)],
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
            [(0, 0), (1, 0), (2, 0), (2, 1)],
        ]
        d.problem(
            "Original 2002 #4.",
            "The square was cut along the lines. Which of the shapes below was <b>not</b> obtained this way?",
            cut_problem(orig, opts, 3),
            "below",
        )
        key.append((
            "2002 #4",
            "D",
            "The pieces are: 1 small square, 2 dominoes, an L of 3, a T of 4 and an L of 4. There is no U-shaped piece.",
        ))

    rng = random.Random(seed)
    sizes = [4, 5, 4, 5, 4]
    for idx in range(1, num_practice + 1):
        n_sz = sizes[(idx - 1) % len(sizes)]
        g, o, ans_idx, expl = _generate_random_partition_problem(rng, n_size=n_sz)
        d.problem(
            f"Practice {set_num}.{idx}",
            f"This {n_sz} × {n_sz} square was cut along the bold lines into pieces. "
            "Which of the shapes below was <b>not</b> obtained this way?",
            cut_problem(g, o, ans_idx),
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_4

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
