# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #18 - Question Generator."""
import os
import sys
import random
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    hstack,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
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
        c.setStrokeColor(colors.black)
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
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def fig_polyomino_numbered(cells, num, s=11):
    """Draw a polyomino piece with a label number above."""
    rs = [p[0] for p in cells]
    cs = [p[1] for p in cells]
    min_r, min_c = min(rs), min(cs)
    norm = {(r - min_r, c - min_c) for r, c in cells}
    nr = max(r for r, _ in norm) + 1
    nc = max(c for _, c in norm) + 1
    w = max(nc * s, 38)
    label_h = 13
    h = nr * s + label_h

    def draw(c, x, y):
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(colors.black)
        c.drawCentredString(x + w / 2, y + h - 10, f"Piece {num}")

        ox = x + (w - nc * s) / 2
        top = y + nr * s
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.Color(0.82, 0.82, 0.82))
        for r, col in norm:
            cx = ox + col * s
            cy = top - (r + 1) * s
            c.rect(cx, cy, s, s, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def _is_connected(cells):
    cell_set = set(cells)
    if not cell_set:
        return False
    start = next(iter(cell_set))
    visited = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = (r + dr, c + dc)
            if nb in cell_set and nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return len(visited) == len(cell_set)


def _normalize_cells(cells):
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return tuple(sorted((r - mr, c - mc) for r, c in cells))


def _rotate_cells(cells, k_rot):
    cur = list(cells)
    for _ in range(k_rot % 4):
        cur = [(c, -r) for r, c in cur]
    return list(_normalize_cells(cur))


def _poly_orientations(cells, allow_flip=False):
    res = set()
    cur = list(cells)
    for _ in range(4):
        res.add(_normalize_cells(cur))
        if allow_flip:
            flipped = [(r, -c) for r, c in cur]
            res.add(_normalize_cells(flipped))
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
    for p in pieces:
        assert _is_connected(p), f"Piece is not connected: {p}"
    empty_cells = [
        (r, c)
        for r in range(len(grid_matrix))
        for c in range(len(grid_matrix[0]))
        if grid_matrix[r][c] == 0
    ]
    assert _is_connected(empty_cells), "White region is not connected"
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


def _grow_random_polyomino(rng, target_size, max_dim=4):
    cells = {(0, 0)}
    while len(cells) < target_size:
        frontier = []
        for r, c in cells:
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nb = (r + dr, c + dc)
                if nb not in cells:
                    rs = [p[0] for p in cells] + [nb[0]]
                    cs = [p[1] for p in cells] + [nb[1]]
                    if max(rs) - min(rs) + 1 <= max_dim and max(cs) - min(cs) + 1 <= max_dim:
                        frontier.append(nb)
        if not frontier:
            break
        cells.add(rng.choice(frontier))
    return list(_normalize_cells(cells))


def _generate_dynamic_cover_problem(rng, grid_n=6):
    """Procedurally generate an N x N black/white grid and 4 numbered polyomino pieces
    where a unique pair of pieces tiles the white region.
    """
    for _ in range(400):
        inner = [(r, c) for r in range(1, grid_n - 1) for c in range(1, grid_n - 1)]
        # Remove 1 to 4 corner/boundary cells of inner while keeping the white region connected
        corners = [(1, 1), (1, grid_n - 2), (grid_n - 2, 1), (grid_n - 2, grid_n - 2)]
        rng.shuffle(corners)
        n_remove = 1 if grid_n == 5 else rng.randint(1, 3)
        empty_set = set(inner) - set(corners[:n_remove])
        min_empty = 8 if grid_n == 5 else 10
        if not _is_connected(empty_set) or len(empty_set) < min_empty:
            continue

        total_empty = len(empty_set)
        size_a = rng.randint(4, total_empty - 4)
        # Grow piece A from a boundary cell of empty_set
        start_cell = min(empty_set)
        pa = {start_cell}
        while len(pa) < size_a:
            nbs = [
                (r + dr, c + dc)
                for r, c in pa
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if (r + dr, c + dc) in empty_set and (r + dr, c + dc) not in pa
            ]
            if not nbs:
                break
            pa.add(rng.choice(nbs))
        if len(pa) != size_a:
            continue
        pb = empty_set - pa
        if not _is_connected(pb):
            continue

        pa_rot = _rotate_cells(pa, rng.randint(0, 3))
        pb_rot = _rotate_cells(pb, rng.randint(0, 3))

        # Generate two distractor polyominoes pc and pd
        pc = _grow_random_polyomino(rng, len(pa) + rng.choice([-1, 0, 1]), max_dim=4)
        pd = _grow_random_polyomino(rng, len(pb) + rng.choice([-1, 1]), max_dim=4)

        raw_pieces = [pa_rot, pb_rot, pc, pd]
        perm = [0, 1, 2, 3]
        rng.shuffle(perm)
        pieces = [raw_pieces[i] for i in perm]
        win_pair_idx = tuple(sorted((perm.index(0) + 1, perm.index(1) + 1)))
        win_str = f"{win_pair_idx[0]} and {win_pair_idx[1]}"

        all_pairs = [f"{i} and {j}" for i in range(1, 5) for j in range(i + 1, 5)]
        # Check that ONLY win_str tiles empty_set (both with and without flips)
        valid_rot = [
            s for s in all_pairs
            if can_tile_empty_with_two_pieces(
                empty_set, pieces[int(s[0]) - 1], pieces[int(s[-1]) - 1], allow_flip=False
            )
        ]
        valid_sym = [
            s for s in all_pairs
            if can_tile_empty_with_two_pieces(
                empty_set, pieces[int(s[0]) - 1], pieces[int(s[-1]) - 1], allow_flip=True
            )
        ]
        if valid_rot != [win_str] or valid_sym != [win_str]:
            continue

        other_pairs = [s for s in all_pairs if s != win_str]
        rng.shuffle(other_pairs)
        opts = [win_str] + other_pairs[:4]
        rng.shuffle(opts)
        ans_idx = opts.index(win_str)

        grid_m = [
            [0 if (r, c) in empty_set else 1 for c in range(grid_n)]
            for r in range(grid_n)
        ]
        check_cover_two_pieces(grid_m, pieces, opts, ans_idx)
        i1, i2 = win_pair_idx
        expl = (
            f"The white area has {total_empty} squares. Piece {i1} ({len(pieces[i1 - 1])} squares) and "
            f"Piece {i2} ({len(pieces[i2 - 1])} squares) have {len(pieces[i1 - 1])} + {len(pieces[i2 - 1])} = "
            f"{total_empty} squares and fit together (after rotation) to cover the white shape without overlap."
        )
        return grid_n, grid_m, pieces, opts, ans_idx, expl

    raise RuntimeError("Failed to generate cover problem")


def q_2003_18(d, key, set_num=6, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Covering an empty shape with two pieces", "Based on 2003, Problem 18")

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

    rng = random.Random(seed)
    for idx in range(1, num_practice + 1):
        gn = 5 if idx % 3 == 0 else 6
        grid_n, grid_m, pieces, opts, ans_idx, expl = _generate_dynamic_cover_problem(rng, grid_n=gn)
        fig_p = hstack([
            fig_grid_black_white(grid_m, s=12),
            hstack([fig_polyomino_numbered(pieces[i], i + 1, s=10) for i in range(4)], gap=12),
        ], gap=18)
        d.problem(
            f"Practice {set_num}.{idx}",
            f"The picture shows a {grid_n} × {grid_n} square with some cells black and the rest white. We want to cover "
            "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
            "Which two pieces should we choose?",
            fig_p,
            "below",
            opts,
            choice_cols=5,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_18

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
