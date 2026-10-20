# Model: argon
"""Math Kangaroo 2007, Problem #8 - Question Generator."""
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
QUESTION_ID = (2007, 8)


def poly_cells_from_grid(grid):
    cells = set()
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == 1:
                cells.add((r, c))
    return cells


def get_poly_rotations(cells):
    rots = []
    current = cells
    for _ in range(4):
        min_r = min(r for r, c in current)
        min_c = min(c for r, c in current)
        norm = frozenset((r - min_r, c - min_c) for r, c in current)
        if norm not in rots:
            rots.append(norm)
        current = set((c, -r) for r, c in current)
    return rots


def can_form_rect(given_cells, cand_cells):
    for rot in get_poly_rotations(cand_cells):
        for dr in range(-8, 9):
            for dc in range(-8, 9):
                trans = set((r + dr, c + dc) for r, c in rot)
                if not (given_cells & trans):
                    union = given_cells | trans
                    min_r = min(r for r, c in union)
                    max_r = max(r for r, c in union)
                    min_c = min(c for r, c in union)
                    max_c = max(c for r, c in union)
                    h = max_r - min_r + 1
                    w = max_c - min_c + 1
                    if len(union) == h * w:
                        return True
    return False


def check_fit_rectangle(given_grid, opt_grids, correct_idx):
    g_cells = poly_cells_from_grid(given_grid)
    results = [can_form_rect(g_cells, poly_cells_from_grid(opt)) for opt in opt_grids]
    assert results[correct_idx] is True, f"Correct choice {correct_idx} failed to form rectangle!"
    matches = [i for i, r in enumerate(results) if r]
    assert matches == [correct_idx], f"Expected unique match at {correct_idx}, got {matches}"


def fig_poly_grid(grid, s=11, label=None):
    """Draw a polyomino defined by binary 2D grid."""
    nr = len(grid)
    nc = len(grid[0])
    w = nc * s
    label_h = 13 if label else 0
    h = nr * s + label_h

    def draw(c, x, y):
        if label:
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawCentredString(x + w / 2, y + h - 10, label)

        top = y + nr * s
        c.setLineWidth(0.9)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.Color(0.85, 0.85, 0.85))
        for r in range(nr):
            for col in range(nc):
                if grid[r][col] == 1:
                    cx = x + col * s
                    cy = top - (r + 1) * s
                    c.rect(cx, cy, s, s, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def q_2007_8(d, key, set_num=7, include_orig=True):
    d.heading(f"Set {set_num} - Joining pieces to form a rectangle", "Based on 2007, Problem 8")

    # Original 2007 #8:
    # Given shape: column heights [5, 2, 1] (8 cells)
    # Piece B: column heights [5, 4, 1] (10 cells). Rotated 180 -> forms 6x3 rectangle (18 cells).
    g0 = [[1, 1, 1], [1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]
    opts0 = [
        [[1, 1, 1], [1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]],
        [[1, 1, 1], [1, 1, 0], [1, 1, 0], [1, 1, 0], [1, 0, 0]],
        [[1, 1], [1, 1], [1, 1], [1, 1], [0, 1]],
        [[1, 1, 1], [0, 1, 1], [0, 0, 1]],
        [[1, 1, 1], [0, 1, 1], [0, 1, 1], [0, 0, 1]],
    ]
    check_fit_rectangle(g0, opts0, 1)

    if include_orig:
        fig0 = vstack([
            fig_poly_grid(g0, s=12, label="Given piece"),
            option_row([fig_poly_grid(opt, s=12) for opt in opts0], gap=16),
        ], gap=12)
        d.problem(
            "Original 2007 #8.",
            "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
            fig0,
            "below",
        )
        key.append((
            "2007 #8",
            "B",
            "The given shape has column heights 5, 2, and 1 (8 squares in total). Shape B has column heights "
            "5, 4, and 1 (10 squares in total). Turning shape B upside-down gives heights 1, 4, and 5. "
            "Fitting them together gives column heights (5+1=6, 2+4=6, 1+5=6), forming a solid 6 × 3 rectangle.",
        ))

    # Practice .1: given heights [4, 1] (5 cells). Joined with [4, 1] rotated 180 to form 5x2 rectangle. Answer: A
    g1 = [[1, 1], [1, 0], [1, 0], [1, 0]]
    opts1 = [
        [[1, 1], [1, 0], [1, 0], [1, 0]],
        [[1, 1], [1, 1], [1, 0]],
        [[1, 1, 1], [1, 1, 0]],
        [[1, 1], [1, 1]],
        [[1, 1], [1, 0], [1, 0]],
    ]
    check_fit_rectangle(g1, opts1, 0)
    fig1 = vstack([
        fig_poly_grid(g1, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts1], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.1",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
        fig1,
        "below",
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The given shape has column heights 4 and 1 (5 squares). Shape A is identical; turned upside-down "
        "it has column heights 1 and 4. Joining them gives columns of height 4+1=5 each, creating a 5 × 2 rectangle.",
    ))

    # Practice .2: given col heights [3, 1, 1] (5 cells). Joined with 2x2 square (4 cells) to form 3x3 square! Answer: B
    g2 = [[1, 1, 1], [1, 0, 0], [1, 0, 0]]
    opts2 = [
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1, 1, 1]],
        [[1, 1], [0, 1], [0, 1]],
    ]
    check_fit_rectangle(g2, opts2, 1)
    fig2 = vstack([
        fig_poly_grid(g2, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts2], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.2",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid square (or rectangle) without gaps or overlaps?",
        fig2,
        "below",
    )
    key.append((
        f"{set_num}.2",
        "B",
        "The given shape has 5 squares forming a corner inside a 3 × 3 boundary. "
        "A 2 × 2 square (shape B, 4 squares) fits into the empty corner to complete a solid 3 × 3 square.",
    ))

    # Practice .3: given col heights [3, 2, 1] (6 cells). Joined with [3, 2, 1] rotated 180 to form 4x3 rectangle. Answer: C
    g3 = [[1, 1, 1], [1, 1, 0], [1, 0, 0]]
    opts3 = [
        [[1, 1], [1, 1], [1, 1]],
        [[1, 1, 1], [1, 1, 1]],
        [[1, 1, 1], [1, 1, 0], [1, 0, 0]],
        [[1, 1, 1, 1], [1, 1, 0, 0]],
        [[1, 1, 1], [1, 1, 0], [0, 1, 0]],
    ]
    check_fit_rectangle(g3, opts3, 2)
    fig3 = vstack([
        fig_poly_grid(g3, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts3], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.3",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
        fig3,
        "below",
    )
    key.append((
        f"{set_num}.3",
        "C",
        "The given staircase shape has column heights 3, 2, and 1 (6 squares). "
        "Shape C is the same staircase; turned upside-down it has column heights 1, 2, and 3. "
        "Joined together, every column has height 4, forming a solid 4 × 3 rectangle of 12 squares.",
    ))

GENERATE = q_2007_8

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
