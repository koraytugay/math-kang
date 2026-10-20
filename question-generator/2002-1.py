# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #1 - Question Generator."""
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
QUESTION_ID = (2002, 1)


def _draw_strokes(c, ox, oy, s, strokes, lw=1.4):
    """Render strokes inside a tile whose bottom-left corner is (ox, oy) with side length s."""
    c.setLineWidth(lw)
    c.setStrokeColor(colors.black)
    for kind, pts in strokes:
        if kind == "line":
            (x1, y1), (x2, y2) = pts
            c.line(ox + x1 * s, oy + y1 * s, ox + x2 * s, oy + y2 * s)
        elif kind == "curve":
            (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pts
            p = c.beginPath()
            p.moveTo(ox + x1 * s, oy + y1 * s)
            p.curveTo(
                ox + cx1 * s,
                oy + cy1 * s,
                ox + cx2 * s,
                oy + cy2 * s,
                ox + x2 * s,
                oy + y2 * s,
            )
            c.drawPath(p, stroke=1, fill=0)
        elif kind == "poly":
            p = c.beginPath()
            x0, y0 = pts[0]
            p.moveTo(ox + x0 * s, oy + y0 * s)
            for xk, yk in pts[1:]:
                p.lineTo(ox + xk * s, oy + yk * s)
            c.drawPath(p, stroke=1, fill=0)


def fig_tile(strokes, s=30):
    """Draw a single candidate square tile of size s with strokes."""
    w = h = s

    def draw(c, x, y):
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.rect(x, y, s, s, stroke=1, fill=1)
        _draw_strokes(c, x, y, s, strokes, lw=1.4)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def fig_tile_grid(n_rows, n_cols, cell_strokes, missing_rc, s=30):
    """Draw a grid of tiles where missing_rc is left open/dashed with a question mark."""
    w = n_cols * s
    h = n_rows * s

    def draw(c, x, y):
        top = y + h
        for r in range(n_rows):
            for col in range(n_cols):
                cx = x + col * s
                cy = top - (r + 1) * s
                if (r, col) == missing_rc:
                    c.setLineWidth(0.9)
                    c.setStrokeColor(colors.Color(0.45, 0.45, 0.45))
                    c.setDash(2, 2)
                    c.rect(cx, cy, s, s, stroke=1, fill=0)
                    c.setDash([])
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 13)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 4.5, "?")
                else:
                    c.setLineWidth(0.85)
                    c.setStrokeColor(colors.black)
                    c.setFillColor(colors.white)
                    c.rect(cx, cy, s, s, stroke=1, fill=1)
                    strokes = cell_strokes.get((r, col), [])
                    _draw_strokes(c, cx, cy, s, strokes, lw=1.4)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def _stroke_endpoints(strokes):
    """Return all start and end points of strokes in a tile."""
    pts = []
    for kind, data in strokes:
        if kind == "line":
            pts.append(data[0])
            pts.append(data[1])
        elif kind == "curve":
            pts.append(data[0])
            pts.append(data[3])
        elif kind == "poly":
            pts.append(data[0])
            pts.append(data[-1])
    return pts


def tile_boundary_signature(strokes, tol=1e-3):
    """Extract sorted boundary crossing coordinates (top, bot, left, right) directly from stroke geometry."""
    top, bot, left, right = set(), set(), set(), set()
    for x, y in _stroke_endpoints(strokes):
        if abs(y - 1.0) <= tol:
            top.add(round(x, 2))
        if abs(y - 0.0) <= tol:
            bot.add(round(x, 2))
        if abs(x - 0.0) <= tol:
            left.add(round(y, 2))
        if abs(x - 1.0) <= tol:
            right.add(round(y, 2))
    return {
        "top": sorted(top),
        "bot": sorted(bot),
        "left": sorted(left),
        "right": sorted(right),
    }


def check_missing_tile_geometry(n_rows, n_cols, cell_strokes, missing_rc, opt_strokes_list, correct_idx):
    """Verify directly from the drawn stroke coordinates that:
    1. Every internal edge between two non-missing cells in cell_strokes has matching boundary crossings.
    2. Strictly one candidate tile in opt_strokes_list matches all neighbors of missing_rc, at correct_idx.
    """
    sigs = {
        (r, c): tile_boundary_signature(cell_strokes.get((r, c), []))
        for r in range(n_rows)
        for c in range(n_cols)
        if (r, c) != missing_rc
    }

    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) == missing_rc:
                continue
            if r + 1 < n_rows and (r + 1, c) != missing_rc:
                assert sigs[(r, c)]["bot"] == sigs[(r + 1, c)]["top"], (
                    f"Vertical discontinuity between {(r, c)} bot={sigs[(r, c)]['bot']} "
                    f"and {(r + 1, c)} top={sigs[(r + 1, c)]['top']}"
                )
            if c + 1 < n_cols and (r, c + 1) != missing_rc:
                assert sigs[(r, c)]["right"] == sigs[(r, c + 1)]["left"], (
                    f"Horizontal discontinuity between {(r, c)} right={sigs[(r, c)]['right']} "
                    f"and {(r, c + 1)} left={sigs[(r, c + 1)]['left']}"
                )

    mr, mc = missing_rc
    req = {}
    if mr > 0:
        req["top"] = sigs[(mr - 1, mc)]["bot"]
    if mr + 1 < n_rows:
        req["bot"] = sigs[(mr + 1, mc)]["top"]
    if mc > 0:
        req["left"] = sigs[(mr, mc - 1)]["right"]
    if mc + 1 < n_cols:
        req["right"] = sigs[(mr, mc + 1)]["left"]

    matches = []
    for idx, opt_strokes in enumerate(opt_strokes_list):
        osig = tile_boundary_signature(opt_strokes)
        if all(osig[edge] == coords for edge, coords in req.items()):
            matches.append(idx)

    assert matches == [correct_idx], (
        f"Missing tile geometry check failed: required={req}, matches={matches}, expected={[correct_idx]}"
    )


def _rot90_cw(strokes):
    return [(kind, tuple((round(y, 2), round(1.0 - x, 2)) for x, y in pts)) for kind, pts in strokes]


def _rot90_ccw(strokes):
    return [(kind, tuple((round(1.0 - y, 2), round(x, 2)) for x, y in pts)) for kind, pts in strokes]


def _rot180(strokes):
    return [(kind, tuple((round(1.0 - x, 2), round(1.0 - y, 2)) for x, y in pts)) for kind, pts in strokes]


def _flip_h(strokes):
    return [(kind, tuple((round(1.0 - x, 2), round(y, 2)) for x, y in pts)) for kind, pts in strokes]


def _flip_v(strokes):
    return [(kind, tuple((round(x, 2), round(1.0 - y, 2)) for x, y in pts)) for kind, pts in strokes]


def _make_smooth_connector(p1, p2, use_curve=True):
    """Connect two boundary points p1=(x1,y1) and p2=(x2,y2) smoothly inside [0,1]^2."""
    x1, y1 = p1
    x2, y2 = p2
    if not use_curve:
        return ("line", ((round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2))))
    # Inward tangent control points
    def inward(x, y):
        dx, dy = 0.0, 0.0
        if abs(x - 0.0) < 1e-3:
            dx = 0.32
        elif abs(x - 1.0) < 1e-3:
            dx = -0.32
        if abs(y - 0.0) < 1e-3:
            dy = 0.32
        elif abs(y - 1.0) < 1e-3:
            dy = -0.32
        return (round(min(0.92, max(0.08, x + dx)), 2), round(min(0.92, max(0.08, y + dy)), 2))

    c1 = inward(x1, y1)
    c2 = inward(x2, y2)
    return ("curve", ((round(x1, 2), round(y1, 2)), c1, c2, (round(x2, 2), round(y2, 2))))


def _generate_dynamic_sailboat(rng):
    """Procedurally generate a parameterized sailboat on waves (3x3 grid, missing (1, 1))."""
    mast_x = rng.choice([0.45, 0.50, 0.55])
    jib_top = rng.choice([0.18, 0.22, 0.26])
    main_top = rng.choice([0.78, 0.82, 0.86])
    jib_left_y = rng.choice([0.34, 0.38, 0.42])
    main_right_y = rng.choice([0.22, 0.26, 0.30])
    jib_top_left_y = rng.choice([0.76, 0.82, 0.86])
    main_top_right_y = rng.choice([0.68, 0.72, 0.78])

    if rng.random() < 0.5:
        # Swap left and right sail heights for variety
        jib_left_y, main_right_y = main_right_y, jib_left_y
        jib_top_left_y, main_top_right_y = main_top_right_y, jib_top_left_y

    grid = {
        (0, 1): [
            ("line", ((mast_x, 0.0), (mast_x, 0.90))),
            ("poly", ((mast_x, 0.90), (round(mast_x + 0.22, 2), 0.82), (mast_x, 0.74))),
            ("line", ((mast_x, 0.72), (jib_top, 0.0))),
            ("line", ((mast_x, 0.86), (main_top, 0.0))),
        ],
        (1, 0): [
            ("poly", ((1.0, jib_left_y), (0.62, jib_left_y), (1.0, jib_top_left_y))),
        ],
        (1, 2): [
            ("poly", ((0.0, main_right_y), (0.42, main_right_y), (0.0, main_top_right_y))),
        ],
        (2, 0): [
            ("poly", ((1.0, 0.75), (0.35, 0.75), (0.65, 0.30), (1.0, 0.30))),
            ("curve", ((0.10, 0.15), (0.40, 0.28), (0.70, 0.02), (1.0, 0.15))),
        ],
        (2, 1): [
            ("line", ((mast_x, 1.0), (mast_x, 0.75))),
            ("line", ((0.0, 0.75), (1.0, 0.75))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (1.0, 0.15))),
        ],
        (2, 2): [
            ("poly", ((0.0, 0.75), (0.65, 0.75), (0.40, 0.30), (0.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (0.90, 0.15))),
        ],
    }
    true_tile = [
        ("line", ((mast_x, 1.0), (mast_x, 0.0))),
        ("line", ((jib_top, 1.0), (0.0, jib_top_left_y))),
        ("line", ((0.0, jib_left_y), (mast_x, jib_left_y))),
        ("line", ((main_top, 1.0), (1.0, main_top_right_y))),
        ("line", ((mast_x, main_right_y), (1.0, main_right_y))),
    ]
    no_booms_distractor = [
        ("line", ((mast_x, 1.0), (mast_x, 0.0))),
        ("line", ((jib_top, 1.0), (0.0, jib_left_y))),
        ("line", ((main_top, 1.0), (1.0, main_right_y))),
    ]
    distractors = [
        _rot90_cw(true_tile),
        _flip_h(true_tile),
        _rot180(true_tile),
        no_booms_distractor,
    ]
    opts = [true_tile] + distractors
    idxs = list(range(5))
    rng.shuffle(idxs)
    shuffled_opts = [opts[i] for i in idxs]
    ans_idx = idxs.index(0)
    ans_letter = LETTERS[ans_idx]
    text = "Which of the squares below is missing from the picture of the sailboat?"
    expl = (
        f"In the missing center square, the vertical mast runs from the top ({mast_x:.2f}) to the bottom ({mast_x:.2f}), "
        f"the two upper sail edges enter from the top at {jib_top:.2f} and {main_top:.2f}, and the horizontal sail booms "
        f"sit at heights {jib_left_y:.2f} (left) and {main_right_y:.2f} (right). Only square {ans_letter} matches all four edges."
    )
    return 3, 3, grid, (1, 1), shuffled_opts, ans_idx, text, expl


def _generate_dynamic_network_puzzle(rng, theme="tracks"):
    """Procedurally generate a continuous multi-cell network puzzle with randomized coordinates & missing cell."""
    n_rows, n_cols = rng.choice([(3, 3), (3, 4)])
    # Choose missing cell (row 1, col 1 or col 2)
    missing_rc = (1, rng.choice([1, n_cols - 2]))
    mr, mc = missing_rc

    # Pick distinct asymmetric coordinates on the 4 edges of missing_rc
    pool_low = [0.20, 0.25, 0.30, 0.35]
    pool_high = [0.65, 0.70, 0.75, 0.80]
    t1, t2 = rng.choice(pool_low), rng.choice(pool_high)
    l1, l2 = rng.choice([x for x in pool_low if x != t1]), rng.choice([x for x in pool_high if x != t2])
    b1 = rng.choice([0.38, 0.42, 0.58, 0.62])
    r1 = rng.choice([x for x in [0.28, 0.32, 0.52, 0.68] if x != b1])

    use_curve = theme in ("tracks", "paths")

    # Build true tile for (mr, mc): connects (left=l2 -> top=t1), (left=l1 -> bot=b1), (top=t2 -> right=r1)
    true_tile = [
        _make_smooth_connector((0.0, l2), (t1, 1.0), use_curve=use_curve),
        _make_smooth_connector((0.0, l1), (b1, 0.0), use_curve=use_curve),
        _make_smooth_connector((t2, 1.0), (1.0, r1), use_curve=use_curve),
    ]

    # Build continuous neighboring tiles around (mr, mc) so every internal edge matches 100%
    mid_r = rng.choice([0.45, 0.55])
    bot_r = rng.choice([0.30, 0.40])
    grid = {
        # Top neighbor (mr - 1, mc): bot must be [t1, t2], right is [mid_r]
        (mr - 1, mc): [
            _make_smooth_connector((t1, 0.0), (1.0, mid_r), use_curve=use_curve),
            _make_smooth_connector((t2, 0.0), (1.0, round(mid_r - 0.20, 2)), use_curve=use_curve),
        ],
        # Top-right neighbor (mr - 1, mc + 1): left is [mid_r - 0.20, mid_r], bot is [0.65]
        (mr - 1, mc + 1): [
            _make_smooth_connector((0.0, mid_r), (0.65, 0.0), use_curve=use_curve),
            _make_smooth_connector((0.0, round(mid_r - 0.20, 2)), (0.30, 0.0), use_curve=use_curve),
        ],
        # Left neighbor (mr, mc - 1): right must be [l1, l2], no other internal crossings
        (mr, mc - 1): [
            ("curve", ((1.0, l2), (0.30, l2), (0.30, l1), (1.0, l1)))
            if use_curve
            else ("poly", ((1.0, l2), (0.30, 0.50), (1.0, l1))),
        ],
        # Right neighbor (mr, mc + 1): left must be [r1], top is [0.30, 0.65], bot is [0.65]
        (mr, mc + 1): [
            _make_smooth_connector((0.30, 1.0), (0.0, r1), use_curve=use_curve),
            ("line", ((0.65, 1.0), (0.65, 0.0))),
        ],
        # Bottom neighbor (mr + 1, mc): top must be [b1], right is [bot_r]
        (mr + 1, mc): [
            _make_smooth_connector((b1, 1.0), (1.0, bot_r), use_curve=use_curve),
        ],
        # Bottom-right neighbor (mr + 1, mc + 1): left is [bot_r], top is [0.65]
        (mr + 1, mc + 1): [
            _make_smooth_connector((0.0, bot_r), (0.65, 1.0), use_curve=use_curve),
        ],
    }

    distractors = [
        _rot90_cw(true_tile),
        _rot90_ccw(true_tile),
        _rot180(true_tile),
        _flip_h(true_tile),
    ]
    opts = [true_tile] + distractors
    idxs = list(range(5))
    rng.shuffle(idxs)
    shuffled_opts = [opts[i] for i in idxs]
    ans_idx = idxs.index(0)
    ans_letter = LETTERS[ans_idx]

    if theme == "tracks":
        text = (
            f"A model train track loops across the {n_rows} × {n_cols} board below. "
            "Which tile (A through E) belongs in the missing square marked with a question mark (?) "
            "to make the track continuous?"
        )
    elif theme == "paths":
        text = (
            f"Park paths wind across the {n_rows} × {n_cols} map below, and one square tile has been removed. "
            "Which of the tiles (A through E) belongs in the square marked with a question mark (?)?"
        )
    else:
        text = (
            f"One square tile is missing from the {n_rows} × {n_cols} geometric line pattern below. "
            "Which tile (A through E) fits in the empty square marked with a question mark (?)?"
        )

    expl = (
        f"Checking the four edges of the missing square (?): two lines enter from the top (at {t1:.2f} and {t2:.2f}), "
        f"two enter from the left (at {l1:.2f} and {l2:.2f}), one exits through the bottom (at {b1:.2f}), and one exits "
        f"through the right (at {r1:.2f}). Only tile {ans_letter} connects all six boundary points in the proper orientation."
    )
    return n_rows, n_cols, grid, missing_rc, shuffled_opts, ans_idx, text, expl


def q_2002_1(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Missing puzzle tile", "Based on 2002, Problem 1")

    # Original 2002 #1: 3x4 grid drawing of a Kangaroo, missing tile (1, 3) -> Answer: B
    grid0 = {
        (0, 3): [
            ("poly", ((0.22, 0.0), (0.26, 0.22), (0.14, 0.42), (0.08, 0.90), (0.16, 0.78),
                      (0.24, 0.92), (0.42, 0.56), (0.76, 0.32), (0.62, 0.10), (0.48, 0.0))),
        ],
        (1, 2): [
            ("curve", ((0.0, 0.72), (0.35, 0.95), (0.70, 0.95), (1.0, 0.88))),
            ("curve", ((0.0, 0.15), (0.04, 0.12), (0.05, 0.06), (0.05, 0.0))),
        ],
        (1, 1): [
            ("curve", ((0.15, 0.0), (0.42, 0.28), (0.72, 0.54), (1.0, 0.72))),
            ("curve", ((0.45, 0.0), (0.65, 0.15), (0.85, 0.20), (1.0, 0.15))),
        ],
        (2, 0): [
            ("curve", ((1.0, 0.48), (0.72, 0.34), (0.55, 0.38), (0.50, 0.55))),
            ("curve", ((0.50, 0.55), (0.45, 0.30), (0.68, 0.22), (1.0, 0.30))),
        ],
        (2, 1): [
            ("curve", ((0.0, 0.48), (0.06, 0.68), (0.11, 0.85), (0.15, 1.0))),
            ("curve", ((0.0, 0.30), (0.20, 0.55), (0.35, 0.80), (0.45, 1.0))),
            ("curve", ((1.0, 0.55), (0.82, 0.32), (0.82, 0.14), (1.0, 0.10))),
        ],
        (2, 2): [
            ("curve", ((0.05, 1.0), (0.08, 0.80), (0.05, 0.65), (0.0, 0.55))),
            ("line", ((0.0, 0.10), (1.0, 0.06))),
            ("poly", ((1.0, 0.95), (0.72, 0.62), (0.58, 0.62), (0.66, 0.78), (0.55, 0.82),
                      (0.35, 0.58), (0.24, 0.32), (0.42, 0.22), (1.0, 0.18))),
        ],
        (2, 3): [
            ("curve", ((0.0, 0.18), (0.32, 0.15), (0.38, 0.08), (0.0, 0.06))),
            ("curve", ((0.0, 0.95), (0.04, 0.97), (0.06, 0.98), (0.08, 1.0))),
        ],
    }
    tile0_B = [
        ("poly", ((0.0, 0.88), (0.20, 0.88), (0.22, 1.0))),
        ("curve", ((0.48, 1.0), (0.44, 0.62), (0.28, 0.32), (0.08, 0.0))),
    ]
    tile0_A = _rot90_ccw(tile0_B)
    tile0_D = _rot180(tile0_B)
    tile0_C = [
        ("poly", ((0.28, 1.0), (0.42, 0.65), (0.22, 0.30), (0.0, 0.30))),
        ("poly", ((0.65, 1.0), (1.0, 0.70), (0.60, 0.58), (0.42, 0.0))),
    ]
    tile0_E = _rot180(tile0_C)
    opt0_strokes = [tile0_A, tile0_B, tile0_C, tile0_D, tile0_E]
    check_missing_tile_geometry(3, 4, grid0, (1, 3), opt0_strokes, 1)

    if include_orig:
        fig0 = vstack([
            fig_tile_grid(3, 4, grid0, (1, 3), s=30),
            option_row([fig_tile(s, s=30) for s in opt0_strokes], gap=16),
        ], gap=12)
        d.problem(
            "Original 2002 #1.",
            "Which of the squares below was removed from the picture of the kangaroo?",
            fig0,
            "below",
        )
        key.append((
            "2002 #1",
            "B",
            "In the missing square, the kangaroo's back enters near the top of the left edge and connects to the "
            "back of the neck on the top edge, while the throat line from the top edge curves down to the chest "
            "at the bottom-left. Only square B matches all of these connections in the right orientation.",
        ))

    rng = random.Random(seed)
    themes = ["sailboat", "paths", "mosaic", "tracks", "paths", "tracks"]
    for idx in range(1, num_practice + 1):
        theme = themes[(idx - 1) % len(themes)]
        if theme == "sailboat":
            nr, nc, g_strokes, miss_rc, o_strokes, ans_idx, text, expl = _generate_dynamic_sailboat(rng)
        else:
            nr, nc, g_strokes, miss_rc, o_strokes, ans_idx, text, expl = _generate_dynamic_network_puzzle(rng, theme=theme)
        check_missing_tile_geometry(nr, nc, g_strokes, miss_rc, o_strokes, ans_idx)
        fig_p = vstack([
            fig_tile_grid(nr, nc, g_strokes, miss_rc, s=30),
            option_row([fig_tile(s, s=30) for s in o_strokes], gap=16),
        ], gap=12)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_p,
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_1

if __name__ == "__main__":
    for test_seed in range(25):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 25 random seeds!")
