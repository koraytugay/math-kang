# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #12 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 12)


def fig_zigzag_race(names, paths, grid_cols=13, grid_rows=10, s=10.5):
    """Draw the dashed grid and thick orthogonal paths for 3 kangaroos."""
    pad_x = 12
    label_h = 15
    top_ext = 1  # paths stick 1 unit above top dashed line (to y = grid_rows + 1)
    w = grid_cols * s + 2 * pad_x
    h = (grid_rows + top_ext) * s + label_h + 6

    def draw(c, x, y):
        ox = x + pad_x
        oy = y + label_h

        # 1. Dashed grid lines: x in 0..grid_cols, y in 0..grid_rows
        c.setLineWidth(0.6)
        c.setStrokeColor(colors.Color(0.35, 0.35, 0.35))
        c.setDash(1.5, 1.5)
        for gx in range(grid_cols + 1):
            px = ox + gx * s
            c.line(px, oy, px, oy + grid_rows * s)
        for gy in range(grid_rows + 1):
            py = oy + gy * s
            c.line(ox, py, ox + grid_cols * s, py)
        c.setDash([])

        # 2. Thick solid zigzag paths
        c.setStrokeColor(colors.black)
        c.setLineWidth(2.2)
        c.setLineCap(1)
        c.setLineJoin(1)
        for path in paths:
            p = c.beginPath()
            x0, y0 = path[0]
            p.moveTo(ox + x0 * s, oy + y0 * s)
            for px, py in path[1:]:
                p.lineTo(ox + px * s, oy + py * s)
            c.drawPath(p, stroke=1, fill=0)
        c.setLineCap(0)
        c.setLineJoin(0)

        # 3. Runner names centered beneath each starting x-coordinate
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8.5)
        for name, path in zip(names, paths):
            sx = ox + path[0][0] * s
            c.drawCentredString(sx, y + 3, name)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def path_length_and_cells(path, grid_cols=13, grid_rows=10):
    assert path[0][1] == 0, f"Path must start at y=0, got {path[0]}"
    assert path[-1][1] == grid_rows + 1, f"Path must end at y={grid_rows + 1}, got {path[-1]}"
    total = 0
    used_vertices = {path[0]}
    horiz_steps = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert 0 <= x1 <= grid_cols and 0 <= x2 <= grid_cols, f"x out of bounds: {(x1, x2)}"
        assert 0 <= y1 <= grid_rows + 1 and 0 <= y2 <= grid_rows + 1, f"y out of bounds: {(y1, y2)}"
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        assert (dx == 0) ^ (dy == 0), f"Non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}"
        if dx > 0:
            horiz_steps.append(dx)
        step_x = 0 if x2 == x1 else (1 if x2 > x1 else -1)
        step_y = 0 if y2 == y1 else (1 if y2 > y1 else -1)
        steps = dx + dy
        for k in range(1, steps + 1):
            v = (x1 + k * step_x, y1 + k * step_y)
            assert v not in used_vertices, f"Self-intersecting path at {v}"
            used_vertices.add(v)
        total += steps
    return total, used_vertices, horiz_steps


def check_zigzag_race(paths, expected_lengths, answer_idx):
    all_vertices = set()
    lengths = []
    for p in paths:
        L, verts, _ = path_length_and_cells(p)
        assert not (all_vertices & verts), f"Paths overlap at {all_vertices & verts}"
        all_vertices |= verts
        lengths.append(L)
    assert lengths == list(expected_lengths), f"Expected path lengths {expected_lengths}, got {lengths}"
    assert 0 <= answer_idx < 5


def _generate_lane_path(rng, x_min, x_max, x_start, target_h, grid_rows=10):
    """Procedurally generate a non-self-intersecting monotonic-upward orthogonal path
    in lane [x_min, x_max] starting and ending at x_start with exact horizontal length target_h.
    """
    for _ in range(500):
        num_turns = rng.randint(4, 7)
        ys = sorted(rng.sample(range(1, grid_rows + 1), num_turns))
        xs = [x_start]
        for i in range(num_turns - 1):
            cands = [x for x in range(x_min, x_max + 1) if x != xs[-1]]
            xs.append(rng.choice(cands))
        if xs[-1] == x_start:
            continue
        xs.append(x_start)
        h_sum = sum(abs(xs[i + 1] - xs[i]) for i in range(num_turns))
        if h_sum == target_h:
            path = [(x_start, 0)]
            curr_x = x_start
            for y_lvl, next_x in zip(ys, xs[1:]):
                path.append((curr_x, y_lvl))
                path.append((next_x, y_lvl))
                curr_x = next_x
            path.append((x_start, grid_rows + 1))
            return path
    raise RuntimeError(f"Could not generate lane path for target_h={target_h}")


NAME_TRIPLETS = [
    ("Anna", "Ben", "Clara"),
    ("Dan", "Eva", "Finn"),
    ("Leo", "Mia", "Noah"),
    ("Max", "Nina", "Otto"),
    ("Ruby", "Sam", "Toby"),
    ("Iris", "Jack", "Kate"),
    ("Liam", "Maya", "Owen"),
]

LANES = [
    (0, 3, 2),
    (5, 8, 6),
    (10, 13, 11),
]


def _generate_dynamic_zigzag_problem(rng, mode=0):
    """Procedurally generate a 3-kangaroo zigzag race problem with verified unique answer."""
    names = list(rng.choice(NAME_TRIPLETS))
    m = mode % 5

    if m == 0:
        # Mode 0: One unique shortest path -> "<Fastest> is first"
        winner = rng.randint(0, 2)
        h_vals = [10, 10, 10]
        h_vals[winner] = rng.choice([6, 8])
        other_idxs = [i for i in range(3) if i != winner]
        if rng.random() < 0.5:
            h_vals[other_idxs[0]] = h_vals[winner] + 2
            h_vals[other_idxs[1]] = h_vals[winner] + 4
        correct_stmt = f"{names[winner]} is first"
        wrong_stmts = [
            f"{names[other_idxs[0]]} is first",
            f"{names[other_idxs[1]]} is first",
            f"{names[winner]} is last",
            "They all arrive at the same time",
        ]

    elif m == 1:
        # Mode 1: Two kangaroos tie, third has different length -> "<A> and <B> arrive at the same time"
        odd_idx = rng.randint(0, 2)
        tied_idxs = [i for i in range(3) if i != odd_idx]
        tied_h = rng.choice([8, 10])
        odd_h = rng.choice([h for h in [6, 8, 10, 12] if h != tied_h])
        h_vals = [0, 0, 0]
        h_vals[tied_idxs[0]] = tied_h
        h_vals[tied_idxs[1]] = tied_h
        h_vals[odd_idx] = odd_h
        nA, nB = names[tied_idxs[0]], names[tied_idxs[1]]
        nOdd = names[odd_idx]
        correct_stmt = f"{nA} and {nB} arrive at the same time"
        wrong_stmts = [
            f"{nA} and {nOdd} arrive at the same time",
            f"{nB} and {nOdd} arrive at the same time",
            "They all arrive at the same time",
            f"{nOdd} is last" if odd_h < tied_h else f"{nOdd} is first",
        ]

    elif m == 2:
        # Mode 2: All three tie -> "They all arrive at the same time"
        common_h = rng.choice([8, 10])
        h_vals = [common_h, common_h, common_h]
        correct_stmt = "They all arrive at the same time"
        wrong_stmts = [
            f"{names[0]} is first",
            f"{names[1]} is last",
            f"Only {names[0]} and {names[1]} arrive at the same time",
            f"{names[2]} is first",
        ]

    elif m == 3:
        # Mode 3: One unique longest path -> "<Slowest> is last"
        loser = rng.randint(0, 2)
        other_idxs = [i for i in range(3) if i != loser]
        h_vals = [0, 0, 0]
        h_vals[loser] = rng.choice([10, 12])
        h_vals[other_idxs[0]] = h_vals[loser] - 4
        h_vals[other_idxs[1]] = h_vals[loser] - 2
        correct_stmt = f"{names[loser]} is last"
        wrong_stmts = [
            f"{names[loser]} is first",
            f"{names[other_idxs[0]]} is last",
            f"{names[other_idxs[1]]} is first",
            f"{names[other_idxs[0]]} and {names[other_idxs[1]]} arrive at the same time",
        ]

    else:
        # Mode 4: Numeric question asking for shortest or longest path length in meters
        h_perm = [6, 8, 10] if rng.random() < 0.5 else [8, 10, 12]
        rng.shuffle(h_perm)
        h_vals = h_perm
        paths = [_generate_lane_path(rng, *LANES[i], h_vals[i]) for i in range(3)]
        lengths = [11 + h for h in h_vals]
        ask_shortest = rng.random() < 0.6
        target_len = min(lengths) if ask_shortest else max(lengths)
        target_word = "shortest" if ask_shortest else "longest"
        winner_idx = lengths.index(target_len)
        cands = sorted(list({target_len - 2, target_len - 1, target_len, target_len + 2, target_len + 4}))
        opts = [f"{v} m" for v in cands]
        ans_idx = cands.index(target_len)
        check_zigzag_race(paths, lengths, ans_idx)

        step_descs = []
        for i in range(3):
            _, _, h_steps = path_length_and_cells(paths[i])
            s_str = " + ".join(str(s) for s in h_steps)
            step_descs.append(
                f"{names[i]} travels {s_str} = {h_vals[i]} m horizontally (total 11 + {h_vals[i]} = {lengths[i]} m)"
            )
        text = (
            f"Three kangaroos — {names[0]}, {names[1]}, and {names[2]} — jump from the bottom to the top along the "
            f"paths shown on the grid, where each small grid square has a side of 1 m. "
            f"What is the total length of the <b>{target_word}</b> path?"
        )
        expl = (
            f"Every kangaroo travels 11 m upward. Counting horizontal steps: {', '.join(step_descs)}. "
            f"The {target_word} path is {names[winner_idx]}'s path at {target_len} m."
        )
        return names, paths, lengths, opts, ans_idx, 5, text, expl

    paths = [_generate_lane_path(rng, *LANES[i], h_vals[i]) for i in range(3)]
    lengths = [11 + h for h in h_vals]
    opts = [correct_stmt] + wrong_stmts
    rng.shuffle(opts)
    ans_idx = opts.index(correct_stmt)
    check_zigzag_race(paths, lengths, ans_idx)

    step_descs = []
    for i in range(3):
        _, _, h_steps = path_length_and_cells(paths[i])
        s_str = " + ".join(str(s) for s in h_steps)
        step_descs.append(f"{names[i]} takes {s_str} = {h_vals[i]} horizontal steps (total {lengths[i]})")
    text = (
        f"During a zigzag run the kangaroos {names[0]}, {names[1]}, and {names[2]} jump along the paths drawn "
        f"in the picture at the same speed. Which statement is true?"
    )
    expl = (
        f"Each kangaroo travels 11 units upward. Counting horizontal steps: {', '.join(step_descs)}. "
        f"Therefore, \"{correct_stmt}\" is true."
    )
    return names, paths, lengths, opts, ans_idx, 1, text, expl


def q_2002_12(d, key, set_num=3, include_orig=True, num_practice=5, seed=None):
    d.heading(
        f"Problem {set_num}: 2002 #12 - Kangaroo Zigzag Run",
        "Comparing total grid-segment lengths of zigzag paths",
    )

    if include_orig:
        paths0 = [
            [(2, 0), (2, 3), (4, 3), (4, 5), (1, 5), (1, 6), (0, 6), (0, 7), (1, 7), (1, 8), (0, 8), (0, 10), (2, 10), (2, 11)],
            [(6, 0), (6, 1), (7, 1), (7, 2), (5, 2), (5, 3), (6, 3), (6, 4), (5, 4), (5, 5), (6, 5), (6, 6), (8, 6), (8, 8), (7, 8), (7, 9), (6, 9), (6, 11)],
            [(11, 0), (11, 1), (12, 1), (12, 2), (13, 2), (13, 3), (12, 3), (12, 4), (11, 4), (11, 5), (10, 5), (10, 6), (9, 6), (9, 7), (10, 7), (10, 8), (11, 8), (11, 11)],
        ]
        check_zigzag_race(paths0, [21, 21, 19], 4)
        opts0 = [
            "Mary and Oscar arrive at the same time",
            "Norbert is first",
            "Oscar is last",
            "They all arrive at the same time",
            "Mary and Norbert arrive at the same time",
        ]
        d.problem(
            "2002 #12",
            "During a zigzag run the kangaroos Mary, Norbert, and Oscar have to jump as drawn in the picture. "
            "Suppose they jump at the same speed. Which statement is true?",
            fig_zigzag_race(["Mary", "Norbert", "Oscar"], paths0),
            "right",
            opts0,
            choice_cols=1,
        )
        key.append((
            "2002 #12",
            "E",
            "All three kangaroos move upward by the exact same vertical distance (11 grid units) without ever going down. "
            "Counting their horizontal side-to-side steps: Mary makes 2 + 3 + 1 + 1 + 1 + 2 = 10 horizontal steps (total 21), "
            "Norbert makes 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 = 10 horizontal steps (total 21), and Oscar makes "
            "1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 = 8 horizontal steps (total 19). Oscar finishes first (19 steps), "
            "while Mary and Norbert arrive at the same time (21 steps each).",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2, 3, 4]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        names, paths, exp_lens, opts, ans_idx, cols, text, expl = _generate_dynamic_zigzag_problem(rng, mode=m)
        check_zigzag_race(paths, exp_lens, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_zigzag_race(names, paths),
            "right",
            opts,
            choice_cols=cols,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_12

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
