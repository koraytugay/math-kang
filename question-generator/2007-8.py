# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #8 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    option_row,
    vstack,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2007, 8)


def poly_cells_from_grid(grid):
    cells = set()
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == 1:
                cells.add((r, c))
    return cells


def _cells_to_grid(cells):
    min_r = min(r for r, c in cells)
    max_r = max(r for r, c in cells)
    min_c = min(c for r, c in cells)
    max_c = max(c for r, c in cells)
    H = max_r - min_r + 1
    W = max_c - min_c + 1
    norm = {(r - min_r, c - min_c) for r, c in cells}
    return [[1 if (r, c) in norm else 0 for c in range(W)] for r in range(H)]


def get_poly_orientations(cells, allow_flip=False):
    rots = []
    current = set(cells)
    for _ in range(4):
        min_r = min(r for r, c in current)
        min_c = min(c for r, c in current)
        norm = frozenset((r - min_r, c - min_c) for r, c in current)
        if norm not in rots:
            rots.append(norm)
        if allow_flip:
            flipped = {(r, -c) for r, c in current}
            mr_f = min(r for r, c in flipped)
            mc_f = min(c for r, c in flipped)
            norm_f = frozenset((r - mr_f, c - mc_f) for r, c in flipped)
            if norm_f not in rots:
                rots.append(norm_f)
        current = {(c, -r) for r, c in current}
    return rots


def can_form_rect(given_cells, cand_cells, allow_flip=False):
    for rot in get_poly_orientations(cand_cells, allow_flip=allow_flip):
        for dr in range(-6, 7):
            for dc in range(-6, 7):
                trans = {(r + dr, c + dc) for r, c in rot}
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
    results_rot = [can_form_rect(g_cells, poly_cells_from_grid(opt), allow_flip=False) for opt in opt_grids]
    results_flip = [can_form_rect(g_cells, poly_cells_from_grid(opt), allow_flip=True) for opt in opt_grids]
    matches_rot = [i for i, r in enumerate(results_rot) if r]
    matches_flip = [i for i, r in enumerate(results_flip) if r]
    assert matches_rot == [correct_idx], f"Expected unique rotation match at {correct_idx}, got {matches_rot}"
    assert matches_flip == [correct_idx], f"Expected unique dihedral match at {correct_idx}, got {matches_flip}"


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
        c.setLineWidth(1)

    return w, h, draw


def _grid_from_col_heights(col_heights):
    H = max(col_heights)
    W = len(col_heights)
    return [[1 if r < col_heights[c] else 0 for c in range(W)] for r in range(H)]


def _rotate_grid(grid, k_rot):
    cells = poly_cells_from_grid(grid)
    for _ in range(k_rot % 4):
        cells = {(c, -r) for r, c in cells}
    return _cells_to_grid(cells)


def _generate_dynamic_rect_join_problem(rng):
    """Procedurally generate a stepped polyomino and 5 candidate pieces where a unique piece
    joins with the given shape to form a solid rectangle.
    """
    for _ in range(400):
        W = rng.choice([2, 3, 4])
        H = rng.choice([4, 5, 6])
        # Pick non-increasing column heights h_0 >= h_1 >= ... >= h_{W-1} >= 1 with h_0 > h_{W-1}
        heights = sorted([rng.randint(1, H - 1) for _ in range(W)], reverse=True)
        if heights[0] == heights[-1]:
            heights[0] = min(H - 1, heights[0] + 1)
            heights[-1] = max(1, heights[-1] - 1)
        if heights[0] == heights[-1] or heights == [5, 2, 1]:
            continue

        given_grid = _grid_from_col_heights(heights)
        g_cells = poly_cells_from_grid(given_grid)

        # Complementary column heights when turned upside-down (reversed order)
        comp_heights = [H - h for h in reversed(heights)]
        win_grid = _rotate_grid(_grid_from_col_heights(comp_heights), rng.choice([0, 0, 1, 2]))

        # Generate 4 distractor grids that cannot form ANY rectangle with g_cells (even with flips)
        distractor_grids = []
        seen_norms = {get_poly_orientations(poly_cells_from_grid(win_grid), allow_flip=True)[0]}
        for _ in range(80):
            if len(distractor_grids) >= 4:
                break
            d_w = W if rng.random() < 0.75 else max(2, W + rng.choice([-1, 1]))
            d_heights = sorted([rng.randint(1, H) for _ in range(d_w)], reverse=True)
            cand_g = _rotate_grid(_grid_from_col_heights(d_heights), rng.choice([0, 0, 1]))
            cand_cells = poly_cells_from_grid(cand_g)
            canon = get_poly_orientations(cand_cells, allow_flip=True)[0]
            if canon in seen_norms:
                continue
            if not can_form_rect(g_cells, cand_cells, allow_flip=True):
                seen_norms.add(canon)
                distractor_grids.append(cand_g)

        if len(distractor_grids) < 4:
            continue

        all_opts = distractor_grids + [win_grid]
        order = list(range(5))
        rng.shuffle(order)
        opt_grids = [all_opts[i] for i in order]
        ans_idx = order.index(4)
        check_fit_rectangle(given_grid, opt_grids, ans_idx)

        h_str = ", ".join(str(h) for h in heights)
        c_str = ", ".join(str(H - h) for h in heights)
        expl = (
            f"The given shape has {W} columns of heights {h_str} ({sum(heights)} squares). "
            f"Joining it with shape {LETTERS[ans_idx]} (rotated to supply column heights {c_str}) "
            f"makes every column height equal to {H}, forming a solid {H} × {W} rectangle."
        )
        return given_grid, opt_grids, ans_idx, expl

    raise RuntimeError("Failed to generate rectangle join problem")


def q_2007_8(d, key, set_num=7, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Joining pieces to form a rectangle", "Based on 2007, Problem 8")

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

    rng = random.Random(seed)
    for idx in range(1, num_practice + 1):
        g_grid, opt_grids, ans_idx, expl = _generate_dynamic_rect_join_problem(rng)
        fig_p = vstack([
            fig_poly_grid(g_grid, s=12, label="Given piece"),
            option_row([fig_poly_grid(opt, s=12) for opt in opt_grids], gap=16),
        ], gap=12)
        d.problem(
            f"Practice {set_num}.{idx}",
            "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
            fig_p,
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_8

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
