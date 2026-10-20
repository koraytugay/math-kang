# Model: argon
"""Math Kangaroo 2003, Problem #18 - Question Generator."""
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
QUESTION_ID = (2003, 18)


def fig_grid_black_white(grid_matrix, s=12):
    """Draw a grid of squares where 1=black, 0=white."""
    nr = len(grid_matrix)
    nc = len(grid_matrix[0])
    w = nc * s
    h = nr * s

    def draw(c, x, y):
        top = y + h
        c.setLineWidth(0.8)
        for r in range(nr):
            for col in range(nc):
                cx = x + col * s
                cy = top - (r + 1) * s
                if grid_matrix[r][col] == 1:
                    c.setFillColor(colors.black)
                    c.rect(cx, cy, s, s, stroke=1, fill=1)
                else:
                    c.setFillColor(colors.white)
                    c.rect(cx, cy, s, s, stroke=1, fill=1)

    return w, h, draw


def fig_polyomino_numbered(cells, num, s=11):
    """Draw a polyomino piece with a label number above or inside."""
    rs = [p[0] for p in cells]
    cs = [p[1] for p in cells]
    min_r, min_c = min(rs), min(cs)
    norm = {(r - min_r, c - min_c) for r, c in cells}
    nr = max(r for r, _ in norm) + 1
    nc = max(c for _, c in norm) + 1
    w = nc * s
    label_h = 13
    h = nr * s + label_h

    def draw(c, x, y):
        # Draw number label
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(x + w / 2, y + h - 10, f"Piece {num}")

        top = y + nr * s
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.Color(0.82, 0.82, 0.82))
        for r, col in norm:
            cx = x + col * s
            cy = top - (r + 1) * s
            c.rect(cx, cy, s, s, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def _poly_orientations(cells, allow_flip=False):
    res = set()
    cur = list(cells)
    for _ in range(4):
        mr = min(r for r, c in cur)
        mc = min(c for r, c in cur)
        res.add(tuple(sorted((r - mr, c - mc) for r, c in cur)))
        if allow_flip:
            flipped = [(r, -c) for r, c in cur]
            mr_f = min(r for r, c in flipped)
            mc_f = min(c for r, c in flipped)
            res.add(tuple(sorted((r - mr_f, c - mc_f) for r, c in flipped)))
        cur = [(c, -r) for r, c in cur]
    return [set(o) for o in res]


def can_tile_empty_with_two_pieces(empty_cells, p1_cells, p2_cells, allow_flip=False):
    empty_set = set(empty_cells)
    if len(p1_cells) + len(p2_cells) != len(empty_set):
        return False
    R = max(r for r, c in empty_set) + 1
    C = max(c for r, c in empty_set) + 1
    o1s = _poly_orientations(p1_cells, allow_flip=allow_flip)
    o2s = _poly_orientations(p2_cells, allow_flip=allow_flip)
    for o1 in o1s:
        for dr1 in range(-R, R + 1):
            for dc1 in range(-C, C + 1):
                s1 = {(r + dr1, c + dc1) for r, c in o1}
                if s1.issubset(empty_set):
                    rem = empty_set - s1
                    mr = min(r for r, c in rem)
                    mc = min(c for r, c in rem)
                    rem_norm = {(r - mr, c - mc) for r, c in rem}
                    if any(rem_norm == o2 for o2 in o2s):
                        return True
    return False


def check_cover_two_pieces(grid_matrix, pieces, opts, correct_idx):
    empty_cells = [
        (r, c)
        for r in range(len(grid_matrix))
        for c in range(len(grid_matrix[0]))
        if grid_matrix[r][c] == 0
    ]
    rot_matches = []
    sym_matches = []
    for i, pair_str in enumerate(opts):
        parts = pair_str.replace("and", "+").split("+")
        p1, p2 = [int(v.strip()) - 1 for v in parts]
        if can_tile_empty_with_two_pieces(empty_cells, pieces[p1], pieces[p2], allow_flip=False):
            rot_matches.append(i)
        if can_tile_empty_with_two_pieces(empty_cells, pieces[p1], pieces[p2], allow_flip=True):
            sym_matches.append(i)
    assert rot_matches == [correct_idx], (
        f"2D tiling check (rotations) failed: expected {[correct_idx]}, got {rot_matches}"
    )
    assert sym_matches == [correct_idx], (
        f"2D tiling check (with flips) failed: expected {[correct_idx]}, got {sym_matches}"
    )


def q_2003_18(d, key, set_num=6, include_orig=True):
    d.heading(f"Set {set_num} - Covering an empty shape with two pieces", "Based on 2003, Problem 18")

    # Original 2003 #18: 7x7 grid with 17 empty cells (staircase boundary matching 2003.pdf).
    # Pieces: 1 (9 cells), 2 (9 cells), 3 (8 cells), 4 (9 cells).
    # Only Piece 3 (8 cells) and Piece 4 (9 cells) tile the 17-cell empty shape -> E ("3 and 4").
    opts0 = ["1 and 3", "2 and 4", "2 and 3", "1 and 4", "3 and 4"]
    grid0_m = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid0_m) == 17

    p1_cells = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)]
    p2_cells = [(0, 1), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1), (3, 2)]
    p3_cells = [(0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)]
    p4_cells = [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
    check_cover_two_pieces(grid0_m, [p1_cells, p2_cells, p3_cells, p4_cells], opts0, 4)

    if include_orig:
        fig0 = hstack([
            fig_grid_black_white(grid0_m, s=12),
            hstack([
                fig_polyomino_numbered(p1_cells, 1, s=10),
                fig_polyomino_numbered(p2_cells, 2, s=10),
                fig_polyomino_numbered(p3_cells, 3, s=10),
                fig_polyomino_numbered(p4_cells, 4, s=10),
            ], gap=12),
        ], gap=18)
        d.problem(
            "Original 2003 #18.",
            "The picture shows a 7 × 7 square with some cells black and the rest white. We want to cover "
            "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
            "Which two pieces should we choose?",
            fig0,
            "below",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2003 #18",
            "E",
            "The white area has 17 empty squares. Rotating Piece 4 (9 squares) by 90° clockwise covers the left "
            "and top-center part of the white shape, and rotating Piece 3 (8 squares) by 90° counter-clockwise fits "
            "the remaining right part exactly.",
        ))

    # Practice .1: 6x6 grid, 14 empty cells.
    # Piece 1 (6 cells, stepped) + Piece 2 (8 cells, stepped) tile the 14-cell region -> A ("1 and 2")
    opts1 = ["1 and 2", "1 and 3", "2 and 4", "3 and 4", "2 and 3"]
    grid1_m = [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid1_m) == 14
    p1_1 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1)]
    p1_2 = [(0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    p1_3 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    p1_4 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)]
    check_cover_two_pieces(grid1_m, [p1_1, p1_2, p1_3, p1_4], opts1, 0)

    fig1 = hstack([
        fig_grid_black_white(grid1_m, s=12),
        hstack([
            fig_polyomino_numbered(p1_1, 1, s=10),
            fig_polyomino_numbered(p1_2, 2, s=10),
            fig_polyomino_numbered(p1_3, 3, s=10),
            fig_polyomino_numbered(p1_4, 4, s=10),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.1",
        "The picture shows a 6 × 6 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig1,
        "below",
        opts1,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The white area has 14 squares. Placing Piece 1 (6 squares) at the top of the white region leaves "
        "an 8-square stepped shape at the bottom that matches Piece 2 exactly.",
    ))

    # Practice .2: 6x6 grid, 13 empty cells.
    # Piece 1 (5 cells, P-pentomino) + Piece 3 (8 cells, stepped) tile the 13-cell region -> C ("1 and 3")
    opts2 = ["1 and 2", "2 and 3", "1 and 3", "2 and 4", "3 and 4"]
    grid2_m = [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid2_m) == 13
    p2_1 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    p2_2 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)]
    p2_3 = [(0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2)]
    p2_4 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    check_cover_two_pieces(grid2_m, [p2_1, p2_2, p2_3, p2_4], opts2, 2)

    fig2 = hstack([
        fig_grid_black_white(grid2_m, s=12),
        hstack([
            fig_polyomino_numbered(p2_1, 1, s=10),
            fig_polyomino_numbered(p2_2, 2, s=10),
            fig_polyomino_numbered(p2_3, 3, s=10),
            fig_polyomino_numbered(p2_4, 4, s=10),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.2",
        "The picture shows a 6 × 6 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig2,
        "below",
        opts2,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "C",
        "The white area has 13 squares. Placing Piece 1 (5 squares) in the top-left of the white region "
        "leaves an 8-square stepped shape on the right and bottom that matches Piece 3 exactly.",
    ))

    # Practice .3: 5x5 grid, 11 empty cells.
    # Piece 2 (5 cells, P-pentomino) + Piece 3 (6 cells, 2x3 rectangle) tile the 11-cell region -> D ("2 and 3")
    opts3 = ["1 and 2", "1 and 4", "2 and 4", "2 and 3", "3 and 4"]
    grid3_m = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 1],
    ]
    assert sum(row.count(0) for row in grid3_m) == 11
    p3_1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    p3_2 = [(0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    p3_3 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    p3_4 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    check_cover_two_pieces(grid3_m, [p3_1, p3_2, p3_3, p3_4], opts3, 3)

    fig3 = hstack([
        fig_grid_black_white(grid3_m, s=13),
        hstack([
            fig_polyomino_numbered(p3_1, 1, s=11),
            fig_polyomino_numbered(p3_2, 2, s=11),
            fig_polyomino_numbered(p3_3, 3, s=11),
            fig_polyomino_numbered(p3_4, 4, s=11),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.3",
        "The picture shows a 5 × 5 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig3,
        "below",
        opts3,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "D",
        "The white area has 11 squares (a 3 × 3 block on top of 2 extra squares at the bottom-right). "
        "Piece 3 (the 2 × 3 rectangle, 6 squares) covers the top two rows of the white shape, and Piece 2 "
        "(5 squares) covers the remaining 3 + 2 squares at the bottom.",
    ))

GENERATE = q_2003_18

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
