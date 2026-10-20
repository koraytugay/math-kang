# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #1 - Question Generator.

Procedural generator creating diverse, recognizable picture puzzles across a grid,
where one tile has been removed. Covers 11 distinct visual themes (Sailboat, Park Paths,
Mosaic, Train Tracks, Garden Archway, River Confluence, Village House, Radiant Sun,
Hot Air Balloon, Castle Fortress, Rocket Ship) plus the original Kangaroo puzzle.
"""
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
    """Verify directly from drawn stroke coordinates that:
    1. Every internal edge between two non-missing cells in cell_strokes has matching boundary crossings.
    2. Strictly one candidate tile in opt_strokes_list matches all boundary conditions of missing_rc.
    """
    sigs = {
        (r, c): tile_boundary_signature(strokes)
        for (r, c), strokes in cell_strokes.items()
        if (r, c) != missing_rc
    }

    # Verify internal grid continuity across all adjacent non-missing tiles
    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) == missing_rc:
                continue
            if r + 1 < n_rows and (r + 1, c) != missing_rc:
                assert sigs.get((r, c), {}).get("bot", []) == sigs.get((r + 1, c), {}).get("top", []), (
                    f"Mismatch between cell {(r, c)} bot={sigs.get((r, c), {}).get('bot', [])} "
                    f"and {(r + 1, c)} top={sigs.get((r + 1, c), {}).get('top', [])}"
                )
            if c + 1 < n_cols and (r, c + 1) != missing_rc:
                assert sigs.get((r, c), {}).get("right", []) == sigs.get((r, c + 1), {}).get("left", []), (
                    f"Mismatch between cell {(r, c)} right={sigs.get((r, c), {}).get('right', [])} "
                    f"and {(r, c + 1)} left={sigs.get((r, c + 1), {}).get('left', [])}"
                )

    # Compute required boundary signature for missing_rc from its neighbors
    mr, mc = missing_rc
    req = {}
    if mr > 0 and (mr - 1, mc) in sigs:
        req["top"] = sigs[(mr - 1, mc)]["bot"]
    else:
        req["top"] = []
    if mr + 1 < n_rows and (mr + 1, mc) in sigs:
        req["bot"] = sigs[(mr + 1, mc)]["top"]
    else:
        req["bot"] = []
    if mc > 0 and (mr, mc - 1) in sigs:
        req["left"] = sigs[(mr, mc - 1)]["right"]
    else:
        req["left"] = []
    if mc + 1 < n_cols and (mr, mc + 1) in sigs:
        req["right"] = sigs[(mr, mc + 1)]["left"]
    else:
        req["right"] = []

    correct_sig = tile_boundary_signature(opt_strokes_list[correct_idx])
    assert correct_sig == req, (
        f"Correct option {correct_idx} signature {correct_sig} does not match required boundary {req}"
    )

    for i, opt_strokes in enumerate(opt_strokes_list):
        if i == correct_idx:
            continue
        sig = tile_boundary_signature(opt_strokes)
        assert sig != req, (
            f"Ambiguity detected: option {i} also matches required boundary signature {req}!"
        )


def _rot90_cw(strokes):
    return [(k, tuple((round(y, 2), round(1.0 - x, 2)) for x, y in pts)) for k, pts in strokes]


def _rot90_ccw(strokes):
    return [(k, tuple((round(1.0 - y, 2), round(x, 2)) for x, y in pts)) for k, pts in strokes]


def _rot180(strokes):
    return [(k, tuple((round(1.0 - x, 2), round(1.0 - y, 2)) for x, y in pts)) for k, pts in strokes]


def _flip_h(strokes):
    return [(k, tuple((round(1.0 - x, 2), round(y, 2)) for x, y in pts)) for k, pts in strokes]


def _build_theme_sailboat():
    grid = {
        (0, 1): [
            ("line", ((0.50, 0.0), (0.50, 0.90))),
            ("poly", ((0.50, 0.90), (0.72, 0.82), (0.50, 0.74))),
            ("line", ((0.50, 0.70), (0.20, 0.0))),
            ("line", ((0.50, 0.85), (0.85, 0.0))),
        ],
        (1, 0): [
            ("poly", ((1.0, 0.35), (0.65, 0.35), (1.0, 0.82))),
        ],
        (1, 2): [
            ("poly", ((0.0, 0.25), (0.45, 0.25), (0.0, 0.75))),
        ],
        (2, 0): [
            ("poly", ((1.0, 0.75), (0.35, 0.75), (0.65, 0.30), (1.0, 0.30))),
            ("curve", ((0.10, 0.15), (0.40, 0.28), (0.70, 0.02), (1.0, 0.15))),
        ],
        (2, 1): [
            ("line", ((0.50, 1.0), (0.50, 0.75))),
            ("line", ((0.0, 0.75), (1.0, 0.75))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (1.0, 0.15))),
        ],
        (2, 2): [
            ("poly", ((0.0, 0.75), (0.65, 0.75), (0.40, 0.30), (0.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (0.90, 0.15))),
        ],
    }
    tile_correct = [
        ("line", ((0.50, 1.0), (0.50, 0.0))),
        ("line", ((0.20, 1.0), (0.0, 0.82))),
        ("line", ((0.0, 0.35), (0.50, 0.35))),
        ("line", ((0.85, 1.0), (1.0, 0.75))),
        ("line", ((0.50, 0.25), (1.0, 0.25))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _flip_h(tile_correct),
        tile_correct,
        _rot180(tile_correct),
        [
            ("line", ((0.50, 1.0), (0.50, 0.0))),
            ("line", ((0.20, 1.0), (0.0, 0.35))),
            ("line", ((0.85, 1.0), (1.0, 0.25))),
        ],
    ]
    text = "Which of the squares below is missing from the picture of the sailboat?"
    expl_fmt = (
        "In the center square, the vertical mast runs straight from the top center (0.50) to the bottom center (0.50), "
        "the left jib sail is higher than the right mainsail, and both horizontal booms meet the mast. "
        "Only square {ans} matches all four edges of the missing center square."
    )
    return 3, 3, grid, (1, 1), opts, 2, text, expl_fmt


def _build_theme_park_paths():
    grid = {
        (0, 1): [
            ("curve", ((1.0, 0.55), (0.45, 0.55), (0.35, 0.30), (0.35, 0.0))),
        ],
        (0, 2): [
            ("curve", ((0.0, 0.55), (0.25, 0.55), (0.35, 0.30), (0.35, 0.0))),
            ("curve", ((0.75, 0.0), (0.75, 0.45), (0.85, 0.65), (1.0, 0.65))),
        ],
        (0, 3): [
            ("curve", ((0.0, 0.65), (0.50, 0.65), (0.65, 0.40), (0.65, 0.0))),
        ],
        (1, 0): [
            ("curve", ((1.0, 0.70), (0.40, 0.70), (0.30, 0.45), (0.30, 0.0))),
            ("curve", ((1.0, 0.25), (0.65, 0.25), (0.60, 0.15), (0.60, 0.0))),
        ],
        (1, 1): [
            ("curve", ((0.35, 1.0), (0.35, 0.75), (0.60, 0.70), (1.0, 0.70))),
            ("line", ((0.0, 0.70), (0.35, 0.25))),
            ("line", ((0.35, 0.25), (1.0, 0.25))),
            ("curve", ((0.0, 0.25), (0.20, 0.25), (0.30, 0.12), (0.30, 0.0))),
        ],
        (1, 3): [
            ("curve", ((0.65, 1.0), (0.65, 0.50), (0.35, 0.30), (0.0, 0.30))),
        ],
        (2, 0): [
            ("curve", ((0.30, 1.0), (0.30, 0.40), (0.60, 0.30), (1.0, 0.30))),
            ("curve", ((0.60, 1.0), (0.60, 0.65), (0.80, 0.60), (1.0, 0.60))),
        ],
        (2, 1): [
            ("curve", ((0.30, 1.0), (0.30, 0.70), (0.15, 0.60), (0.0, 0.60))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
        ],
        (2, 2): [
            ("curve", ((0.0, 0.30), (0.35, 0.30), (0.45, 0.60), (0.45, 1.0))),
        ],
    }
    tile_correct = [
        ("curve", ((0.0, 0.70), (0.25, 0.70), (0.35, 0.85), (0.35, 1.0))),
        ("curve", ((0.75, 1.0), (0.75, 0.55), (0.85, 0.30), (1.0, 0.30))),
        ("curve", ((0.0, 0.25), (0.30, 0.25), (0.45, 0.15), (0.45, 0.0))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _rot180(tile_correct),
        _flip_h(tile_correct),
        tile_correct,
        _rot90_ccw(tile_correct),
    ]
    text = (
        "Park paths wind across the 3 × 4 map below, and one square tile has been removed. "
        "Which of the tiles (A through E) belongs in the square marked with a question mark (?)?"
    )
    expl_fmt = (
        "Checking the four edges of the missing square: two paths enter from the top (at 0.35 and 0.75), "
        "two enter from the left (at 0.25 and 0.70), one exits through the bottom (at 0.45), and one exits "
        "through the right (at 0.30). Only tile {ans} connects all six boundary points properly."
    )
    return 3, 4, grid, (1, 2), opts, 3, text, expl_fmt


def _build_theme_mosaic():
    grid = {
        (0, 1): [
            ("line", ((1.0, 0.35), (0.35, 0.0))),
            ("line", ((1.0, 0.75), (0.75, 0.0))),
        ],
        (0, 2): [
            ("line", ((0.0, 0.35), (0.35, 0.0))),
            ("poly", ((0.0, 0.75), (0.75, 0.75), (0.75, 0.0))),
        ],
        (1, 0): [
            ("poly", ((1.0, 0.75), (0.25, 0.50), (1.0, 0.25))),
        ],
        (1, 1): [
            ("line", ((0.35, 1.0), (0.35, 0.0))),
            ("line", ((0.75, 1.0), (0.75, 0.0))),
            ("line", ((0.0, 0.75), (1.0, 0.75))),
            ("line", ((0.0, 0.25), (1.0, 0.25))),
        ],
        (2, 1): [
            ("line", ((0.35, 1.0), (1.0, 0.65))),
            ("line", ((0.75, 1.0), (1.0, 0.25))),
        ],
        (2, 2): [
            ("poly", ((0.0, 0.65), (0.55, 0.65), (0.55, 1.0))),
            ("poly", ((0.0, 0.25), (0.55, 0.25), (0.55, 0.65))),
        ],
    }
    tile_correct = [
        ("line", ((0.0, 0.75), (0.35, 1.0))),
        ("poly", ((0.75, 1.0), (0.75, 0.25), (0.0, 0.25))),
        ("line", ((0.55, 0.0), (0.55, 0.25))),
    ]
    opts = [
        tile_correct,
        _rot90_cw(tile_correct),
        _flip_h(tile_correct),
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "One square tile is missing from the geometric pattern below. Which tile (A through E) fits in the "
        "empty square marked with a question mark (?)?"
    )
    expl_fmt = (
        "Looking at the neighbours of the missing square on the right: two vertical lines enter from the top "
        "(at 0.35 and 0.75), two horizontal lines enter from the left (at 0.25 and 0.75), one vertical line "
        "enters from the bottom (at 0.55), and nothing touches the outer right edge. Only tile {ans} matches."
    )
    return 3, 3, grid, (1, 2), opts, 0, text, expl_fmt


def _build_theme_train_tracks():
    grid = {
        (0, 1): [
            ("curve", ((0.30, 0.0), (0.30, 0.65), (0.55, 0.75), (1.0, 0.75))),
            ("curve", ((0.75, 0.0), (0.75, 0.30), (0.85, 0.35), (1.0, 0.35))),
        ],
        (0, 2): [
            ("curve", ((0.0, 0.75), (0.60, 0.75), (0.70, 0.50), (0.70, 0.0))),
            ("curve", ((0.0, 0.35), (0.25, 0.35), (0.30, 0.20), (0.30, 0.0))),
        ],
        (1, 0): [
            ("curve", ((1.0, 0.70), (0.35, 0.70), (0.35, 0.30), (1.0, 0.30))),
        ],
        (1, 2): [
            ("curve", ((0.30, 1.0), (0.30, 0.65), (0.15, 0.55), (0.0, 0.55))),
            ("line", ((0.70, 1.0), (0.70, 0.0))),
        ],
        (2, 1): [
            ("curve", ((0.40, 1.0), (0.40, 0.45), (0.65, 0.35), (1.0, 0.35))),
        ],
        (2, 2): [
            ("curve", ((0.0, 0.35), (0.50, 0.35), (0.70, 0.55), (0.70, 1.0))),
        ],
    }
    tile_correct = [
        ("curve", ((0.0, 0.70), (0.20, 0.70), (0.30, 0.85), (0.30, 1.0))),
        ("curve", ((0.0, 0.30), (0.30, 0.30), (0.40, 0.15), (0.40, 0.0))),
        ("curve", ((0.75, 1.0), (0.75, 0.65), (0.85, 0.55), (1.0, 0.55))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _flip_h(tile_correct),
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
        tile_correct,
    ]
    text = (
        "A model train track loops across the 3 × 4 board below. Which tile (A through E) belongs in the "
        "missing square marked with a question mark (?) to make the track continuous?"
    )
    expl_fmt = (
        "Tracing the tracks into the missing square: two tracks enter from the left (at 0.30 and 0.70), "
        "two enter from the top (at 0.30 and 0.75), one exits at the bottom (0.40), and one exits at the right (0.55). "
        "Only tile {ans} connects every track without breaks."
    )
    return 3, 4, grid, (1, 1), opts, 4, text, expl_fmt


def _build_theme_garden():
    grid = {
        (0, 1): [
            ("curve", ((0.25, 0.0), (0.25, 0.65), (0.75, 0.65), (0.75, 0.0))),
            ("line", ((0.50, 0.50), (0.50, 0.90))),
        ],
        (1, 0): [
            ("poly", ((1.0, 0.60), (0.30, 0.60), (0.30, 0.0))),
        ],
        (1, 2): [
            ("line", ((0.0, 0.80), (0.70, 0.80))),
            ("line", ((0.70, 0.80), (0.70, 0.0))),
            ("line", ((0.0, 0.20), (0.70, 0.20))),
        ],
        (2, 0): [
            ("poly", ((0.30, 1.0), (0.30, 0.35), (1.0, 0.35))),
        ],
        (2, 1): [
            ("poly", ((0.0, 0.35), (0.35, 0.35), (0.35, 1.0))),
            ("line", ((0.35, 0.35), (1.0, 0.35))),
        ],
        (2, 2): [
            ("poly", ((0.0, 0.35), (0.70, 0.35), (0.70, 1.0))),
        ],
    }
    tile_correct = [
        ("poly", ((0.0, 0.60), (0.25, 0.60), (0.25, 1.0))),
        ("poly", ((0.75, 1.0), (0.75, 0.80), (1.0, 0.80))),
        ("poly", ((0.35, 0.0), (0.35, 0.20), (1.0, 0.20))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "A garden path and archway are drawn across the 3 × 3 grid below, with the middle tile missing. "
        "Which tile (A through E) completes the picture?"
    )
    expl_fmt = (
        "In the center square, two arch lines enter from the top (at 0.25 and 0.75), one line enters from the "
        "left (at 0.60), one enters from the bottom (at 0.35), and two exit through the right (at 0.20 and 0.80). "
        "Only tile {ans} connects all of these endpoints cleanly."
    )
    return 3, 3, grid, (1, 1), opts, 1, text, expl_fmt


def _build_theme_river():
    grid = {
        (0, 2): [
            ("curve", ((0.15, 0.85), (0.35, 0.75), (0.45, 0.45), (0.45, 0.0))),
        ],
        (1, 0): [
            ("curve", ((0.15, 0.25), (0.45, 0.55), (0.75, 0.55), (1.0, 0.55))),
        ],
        (1, 1): [
            ("line", ((0.0, 0.55), (1.0, 0.55))),
            ("line", ((0.40, 0.80), (0.40, 0.30))),
            ("line", ((0.60, 0.80), (0.60, 0.30))),
        ],
        (1, 3): [
            ("curve", ((0.0, 0.70), (0.45, 0.70), (0.65, 0.40), (0.85, 0.40))),
            ("curve", ((0.0, 0.25), (0.35, 0.25), (0.55, 0.15), (0.55, 0.0))),
        ],
        (2, 2): [
            ("curve", ((0.30, 1.0), (0.30, 0.45), (0.50, 0.25), (0.85, 0.25))),
            ("curve", ((0.75, 1.0), (0.75, 0.65), (0.85, 0.55), (1.0, 0.55))),
        ],
        (2, 3): [
            ("curve", ((0.0, 0.55), (0.30, 0.55), (0.55, 0.75), (0.55, 1.0))),
        ],
    }
    tile_correct = [
        ("curve", ((0.0, 0.55), (0.20, 0.55), (0.30, 0.30), (0.30, 0.0))),
        ("curve", ((0.45, 1.0), (0.45, 0.75), (0.70, 0.70), (1.0, 0.70))),
        ("curve", ((0.75, 0.0), (0.75, 0.18), (0.85, 0.25), (1.0, 0.25))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _flip_h(tile_correct),
        tile_correct,
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "Streams flow across the 3 × 4 map below, and one square tile is missing. "
        "Which tile (A through E) fits in the square marked with a question mark (?)?"
    )
    expl_fmt = (
        "In the missing square, one stream enters from the left (at 0.55) and curves down to the bottom (at 0.30), "
        "one enters from the top (at 0.45) and curves to the upper-right (at 0.70), and a third connects the "
        "bottom-right (0.75) to the lower-right edge (0.25). Only tile {ans} matches all six boundary crossings."
    )
    return 3, 4, grid, (1, 2), opts, 2, text, expl_fmt


def _build_theme_house():
    grid = {
        (0, 0): [
            ("line", ((1.0, 0.40), (0.20, 0.15))),
            ("line", ((0.20, 0.15), (0.10, 0.15))),
            ("line", ((0.60, 0.15), (0.60, 0.0))),
        ],
        (0, 1): [
            ("line", ((0.50, 0.90), (0.0, 0.40))),
            ("line", ((0.50, 0.90), (1.0, 0.40))),
            ("poly", ((0.65, 0.55), (0.65, 0.95), (0.80, 0.95), (0.80, 0.45))),
            ("line", ((0.30, 0.70), (0.30, 0.0))),
            ("line", ((0.70, 0.70), (0.70, 0.0))),
        ],
        (0, 2): [
            ("line", ((0.0, 0.40), (0.80, 0.15))),
            ("line", ((0.80, 0.15), (0.90, 0.15))),
            ("line", ((0.40, 0.15), (0.40, 0.0))),
        ],
        (1, 0): [
            ("line", ((0.60, 1.0), (0.60, 0.0))),
            ("poly", ((0.15, 0.65), (0.45, 0.65), (0.45, 0.35), (0.15, 0.35), (0.15, 0.65))),
            ("line", ((0.60, 0.75), (1.0, 0.75))),
        ],
        (1, 2): [
            ("line", ((0.40, 1.0), (0.40, 0.0))),
            ("line", ((0.0, 0.75), (0.40, 0.75))),
            ("curve", ((0.0, 0.35), (0.20, 0.35), (0.30, 0.50), (0.20, 0.50))),
        ],
        (2, 0): [
            ("line", ((0.60, 1.0), (0.60, 0.0))),
        ],
        (2, 1): [
            ("line", ((0.25, 1.0), (0.15, 0.0))),
            ("line", ((0.60, 1.0), (0.75, 0.0))),
        ],
        (2, 2): [
            ("line", ((0.40, 1.0), (0.40, 0.0))),
        ],
    }
    tile_correct = [
        ("line", ((0.30, 1.0), (0.25, 0.0))),
        ("line", ((0.70, 1.0), (0.60, 0.0))),
        ("line", ((0.0, 0.75), (0.30, 0.75))),
        ("line", ((0.70, 0.75), (1.0, 0.75))),
        ("curve", ((1.0, 0.35), (0.80, 0.35), (0.65, 0.50), (0.65, 0.50))),
        ("curve", ((0.28, 0.55), (0.40, 0.70), (0.55, 0.70), (0.63, 0.55))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "A cozy village house is drawn on the 3 × 3 grid below, but the central front-door square is missing. "
        "Which tile (A through E) completes the house?"
    )
    expl_fmt = (
        "In the missing center square, the two doorframe pillars run from top (0.30, 0.70) down to the walkway "
        "(0.25, 0.60), the decorative frieze crosses horizontally at height 0.75, and a vine enters from the right edge "
        "at height 0.35. Only tile {ans} matches all connections."
    )
    return 3, 3, grid, (1, 1), opts, 1, text, expl_fmt


def _build_theme_sun():
    grid = {
        (0, 0): [
            ("curve", ((0.20, 0.80), (0.60, 0.90), (0.80, 0.70), (0.90, 0.50))),
            ("curve", ((0.90, 0.50), (0.80, 0.30), (0.50, 0.20), (0.30, 0.40))),
        ],
        (0, 1): [
            ("line", ((0.25, 0.0), (0.25, 0.75))),
            ("line", ((0.75, 0.0), (0.75, 0.75))),
            ("line", ((0.50, 0.15), (0.50, 0.90))),
            ("curve", ((0.25, 0.75), (0.35, 0.85), (0.65, 0.85), (0.75, 0.75))),
        ],
        (0, 2): [
            ("curve", ((0.10, 0.60), (0.40, 0.85), (0.80, 0.80), (0.90, 0.55))),
        ],
        (1, 0): [
            ("line", ((1.0, 0.60), (0.40, 0.60))),
            ("curve", ((0.15, 0.30), (0.35, 0.70), (0.70, 0.70), (0.60, 0.30))),
        ],
        (1, 2): [
            ("line", ((0.0, 0.75), (0.65, 0.75))),
            ("curve", ((0.0, 0.30), (0.35, 0.40), (0.70, 0.35), (0.85, 0.20))),
        ],
        (2, 0): [
            ("curve", ((0.10, 0.15), (0.40, 0.25), (0.70, 0.30), (1.0, 0.35))),
        ],
        (2, 1): [
            ("line", ((0.40, 1.0), (0.40, 0.35))),
            ("curve", ((0.0, 0.35), (0.40, 0.40), (0.70, 0.38), (1.0, 0.30))),
        ],
        (2, 2): [
            ("curve", ((0.0, 0.30), (0.30, 0.25), (0.65, 0.20), (0.90, 0.10))),
        ],
    }
    tile_correct = [
        ("line", ((0.25, 1.0), (0.25, 0.40))),
        ("line", ((0.75, 1.0), (0.75, 0.40))),
        ("line", ((0.0, 0.60), (0.30, 0.60))),
        ("line", ((0.70, 0.75), (1.0, 0.75))),
        ("curve", ((1.0, 0.30), (0.75, 0.25), (0.55, 0.25), (0.40, 0.0))),
        ("curve", ((0.25, 0.40), (0.35, 0.20), (0.65, 0.20), (0.75, 0.40))),
        ("curve", ((0.40, 0.55), (0.50, 0.42), (0.60, 0.55), (0.60, 0.55))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _rot180(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "A radiant sun shines over rolling hills in the 3 × 3 picture below, but the center tile is missing. "
        "Which tile (A through E) fits in the square marked with a question mark (?)?"
    )
    expl_fmt = (
        "In the center tile, two upper sun rays enter from the top edge (at 0.25 and 0.75), a ray enters from the left "
        "(at 0.60), a ray exits through the bottom into the hills (at 0.40), and two exit through the right edge (at 0.30 and 0.75). "
        "Only tile {ans} satisfies all four borders."
    )
    return 3, 3, grid, (1, 1), opts, 2, text, expl_fmt


def _build_theme_hot_air_balloon():
    grid = {
        (0, 0): [
            ("curve", ((0.20, 0.60), (0.40, 0.80), (0.70, 0.75), (0.80, 0.55))),
        ],
        (0, 1): [
            ("curve", ((0.20, 0.0), (0.20, 0.65), (0.40, 0.90), (0.50, 0.90))),
            ("curve", ((0.50, 0.90), (0.60, 0.90), (0.80, 0.65), (0.80, 0.0))),
            ("line", ((0.45, 0.0), (0.45, 0.88))),
        ],
        (0, 2): [
            ("curve", ((0.15, 0.65), (0.45, 0.80), (0.75, 0.70), (0.80, 0.45))),
        ],
        (1, 0): [
            ("curve", ((0.30, 0.40), (0.50, 0.60), (0.80, 0.55), (1.0, 0.40))),
        ],
        (1, 2): [
            ("line", ((0.0, 0.70), (0.45, 0.78))),
            ("line", ((0.0, 0.30), (0.35, 0.38))),
        ],
        (2, 0): [
            ("curve", ((0.10, 0.10), (0.40, 0.25), (0.70, 0.20), (0.90, 0.10))),
        ],
        (2, 1): [
            ("line", ((0.35, 1.0), (0.35, 0.50))),
            ("line", ((0.65, 1.0), (0.65, 0.50))),
            ("poly", ((0.30, 0.50), (0.70, 0.50), (0.65, 0.20), (0.35, 0.20), (0.30, 0.50))),
        ],
        (2, 2): [
            ("curve", ((0.10, 0.15), (0.50, 0.30), (0.80, 0.25), (0.95, 0.10))),
        ],
    }
    tile_correct = [
        ("curve", ((0.20, 1.0), (0.22, 0.60), (0.30, 0.25), (0.35, 0.0))),
        ("curve", ((0.80, 1.0), (0.78, 0.60), (0.70, 0.25), (0.65, 0.0))),
        ("line", ((0.45, 1.0), (0.50, 0.15))),
        ("curve", ((0.0, 0.40), (0.12, 0.45), (0.18, 0.35), (0.10, 0.30))),
        ("line", ((0.75, 0.70), (1.0, 0.70))),
        ("line", ((0.80, 0.30), (1.0, 0.30))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _rot180(tile_correct),
        _rot90_ccw(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
    ]
    text = (
        "A hot air balloon soars across the 3 × 3 sky below. Which tile (A through E) belongs in the "
        "missing square marked with a question mark (?)?"
    )
    expl_fmt = (
        "In the middle square, three contour lines enter from the balloon envelope above (at 0.20, 0.45, and 0.80), "
        "two cords exit through the bottom to the basket (at 0.35 and 0.65), a cloud touches the left edge at 0.40, "
        "and two flight lines exit right (at 0.30 and 0.70). Only tile {ans} matches."
    )
    return 3, 3, grid, (1, 1), opts, 3, text, expl_fmt


def _build_theme_castle():
    grid = {
        (0, 0): [
            ("poly", ((0.20, 0.50), (0.20, 0.90), (0.70, 0.90), (0.70, 0.50))),
            ("line", ((0.70, 0.50), (0.70, 0.0))),
        ],
        (0, 1): [
            ("line", ((0.30, 0.60), (0.30, 0.0))),
            ("line", ((0.75, 0.60), (0.75, 0.0))),
            ("line", ((0.50, 0.60), (0.50, 0.95))),
            ("poly", ((0.50, 0.95), (0.70, 0.88), (0.50, 0.80))),
        ],
        (0, 2): [
            ("poly", ((0.05, 0.60), (0.20, 0.60), (0.20, 0.85), (0.45, 0.85), (0.45, 0.60), (0.60, 0.60), (0.60, 0.85), (0.85, 0.85), (0.85, 0.60), (0.95, 0.60))),
        ],
        (0, 3): [
            ("poly", ((0.10, 0.50), (0.50, 0.95), (0.90, 0.50), (0.10, 0.50))),
            ("line", ((0.30, 0.50), (0.30, 0.0))),
        ],
        (1, 0): [
            ("line", ((0.70, 1.0), (0.70, 0.0))),
            ("line", ((0.70, 0.65), (1.0, 0.65))),
            ("line", ((0.70, 0.30), (1.0, 0.30))),
        ],
        (1, 2): [
            ("curve", ((0.0, 0.50), (0.30, 0.85), (0.70, 0.85), (1.0, 0.50))),
        ],
        (1, 3): [
            ("line", ((0.30, 1.0), (0.30, 0.0))),
            ("line", ((0.0, 0.50), (0.30, 0.50))),
        ],
        (2, 0): [
            ("line", ((0.70, 1.0), (0.70, 0.0))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
        ],
        (2, 1): [
            ("line", ((0.45, 1.0), (0.45, 0.50))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
        ],
        (2, 2): [
            ("line", ((0.0, 0.30), (1.0, 0.30))),
        ],
        (2, 3): [
            ("line", ((0.30, 1.0), (0.30, 0.0))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
        ],
    }
    tile_correct = [
        ("line", ((0.30, 1.0), (0.30, 0.65))),
        ("line", ((0.75, 1.0), (0.75, 0.50))),
        ("line", ((0.0, 0.65), (0.30, 0.65))),
        ("curve", ((0.0, 0.30), (0.25, 0.30), (0.45, 0.20), (0.45, 0.0))),
        ("line", ((0.75, 0.50), (1.0, 0.50))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _rot180(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "A medieval fortress with towers and battlements stands across the 3 × 4 grid below. "
        "Which tile (A through E) belongs in the missing square marked with a question mark (?)?"
    )
    expl_fmt = (
        "Examining the missing square: two wall seams enter from the battlements above (at 0.30 and 0.75), "
        "the west curtain wall enters from the left (at 0.30 and 0.65), the ramp exits down at 0.45, and the gateway "
        "arch connects to the right at 0.50. Only tile {ans} completes the fortress."
    )
    return 3, 4, grid, (1, 1), opts, 2, text, expl_fmt


def _build_theme_rocket():
    grid = {
        (0, 0): [
            ("poly", ((0.30, 0.50), (0.45, 0.70), (0.60, 0.50), (0.30, 0.50))),
        ],
        (0, 1): [
            ("line", ((0.35, 0.0), (0.50, 0.85))),
            ("line", ((0.50, 0.85), (0.65, 0.0))),
            ("poly", ((0.15, 0.70), (0.22, 0.80), (0.28, 0.70), (0.15, 0.70))),
        ],
        (0, 2): [
            ("poly", ((0.50, 0.40), (0.65, 0.60), (0.80, 0.40), (0.50, 0.40))),
        ],
        (1, 0): [
            ("poly", ((1.0, 0.60), (0.55, 0.20), (1.0, 0.20))),
        ],
        (1, 2): [
            ("poly", ((0.0, 0.35), (0.40, 0.35), (0.20, 0.60), (0.0, 0.35))),
        ],
        (2, 0): [
            ("poly", ((0.40, 0.60), (0.55, 0.75), (0.70, 0.60), (0.40, 0.60))),
        ],
        (2, 1): [
            ("poly", ((0.25, 1.0), (0.35, 0.40), (0.50, 1.0))),
            ("poly", ((0.50, 1.0), (0.65, 0.40), (0.75, 1.0))),
            ("curve", ((0.35, 0.40), (0.45, 0.20), (0.55, 0.20), (0.65, 0.40))),
        ],
        (2, 2): [
            ("poly", ((0.30, 0.30), (0.45, 0.50), (0.60, 0.30), (0.30, 0.30))),
        ],
    }
    tile_correct = [
        ("line", ((0.35, 1.0), (0.35, 0.10))),
        ("line", ((0.65, 1.0), (0.65, 0.10))),
        ("line", ((0.0, 0.60), (0.35, 0.60))),
        ("line", ((0.0, 0.20), (0.35, 0.20))),
        ("line", ((0.65, 0.35), (1.0, 0.35))),
        ("line", ((0.35, 0.10), (0.65, 0.10))),
        ("line", ((0.35, 0.10), (0.25, 0.0))),
        ("line", ((0.50, 0.10), (0.50, 0.0))),
        ("line", ((0.65, 0.10), (0.75, 0.0))),
    ]
    opts = [
        _rot90_cw(tile_correct),
        _rot180(tile_correct),
        tile_correct,
        _flip_h(tile_correct),
        _rot90_ccw(tile_correct),
    ]
    text = (
        "A rocket ship launches into outer space on the 3 × 3 grid below. Which tile (A through E) "
        "belongs in the missing square marked with a question mark (?)?"
    )
    expl_fmt = (
        "In the rocket's fuselage square, two hull lines enter from the nosecone above (at 0.35 and 0.65), "
        "three flame nozzles exit through the bottom (at 0.25, 0.50, and 0.75), two fin lines enter from the left "
        "(at 0.20 and 0.60), and one fin enters from the right (at 0.35). Only tile {ans} matches."
    )
    return 3, 3, grid, (1, 1), opts, 2, text, expl_fmt


THEME_BUILDERS = [
    _build_theme_sailboat,
    _build_theme_park_paths,
    _build_theme_mosaic,
    _build_theme_train_tracks,
    _build_theme_garden,
    _build_theme_river,
    _build_theme_house,
    _build_theme_sun,
    _build_theme_hot_air_balloon,
    _build_theme_castle,
    _build_theme_rocket,
]


def _shuffle_options_and_update(opts, correct_idx, rng):
    """Randomly reorder the options so the correct answer is dynamically placed at any of A..E."""
    correct_opt = opts[correct_idx]
    distractors = [opt for i, opt in enumerate(opts) if i != correct_idx]
    rng.shuffle(distractors)
    new_idx = rng.randrange(len(opts))
    new_opts = distractors[:new_idx] + [correct_opt] + distractors[new_idx:]
    return new_opts, new_idx


def q_2002_1(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    """Generate Math Kangaroo 2002 #1 practice set with fully verified, distinct visual picture puzzles."""
    rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Original Kangaroo problem (3x4 grid, missing tile (1, 3))
    grid0 = {
        (0, 3): [
            ("poly", ((0.22, 0.0), (0.26, 0.22), (0.14, 0.42), (0.08, 0.90), (0.16, 0.78),
                      (0.24, 0.92), (0.42, 0.56), (0.76, 0.32), (0.62, 0.10), (0.48, 0.0))),
        ],
        (1, 1): [
            ("curve", ((0.15, 0.0), (0.42, 0.28), (0.72, 0.54), (1.0, 0.72))),
            ("curve", ((0.45, 0.0), (0.65, 0.15), (0.85, 0.20), (1.0, 0.15))),
        ],
        (1, 2): [
            ("curve", ((0.0, 0.72), (0.35, 0.95), (0.70, 0.95), (1.0, 0.88))),
            ("curve", ((0.0, 0.15), (0.04, 0.12), (0.05, 0.06), (0.05, 0.0))),
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

    # ------------------------------------------------------------------
    # Select practice problems from the 11 rich, distinct picture themes
    builder_indices = list(range(len(THEME_BUILDERS)))
    if seed is not None:
        rng.shuffle(builder_indices)

    # Repeat pool if num_practice > len(THEME_BUILDERS)
    selected_indices = []
    while len(selected_indices) < num_practice:
        for b_idx in builder_indices:
            selected_indices.append(b_idx)
            if len(selected_indices) == num_practice:
                break

    for p_idx, b_idx in enumerate(selected_indices, start=1):
        nr, nc, g_strokes, miss_rc, raw_opts, base_ans_idx, text, expl_fmt = THEME_BUILDERS[b_idx]()
        opts, ans_idx = _shuffle_options_and_update(raw_opts, base_ans_idx, rng)
        check_missing_tile_geometry(nr, nc, g_strokes, miss_rc, opts, ans_idx)

        fig_p = vstack([
            fig_tile_grid(nr, nc, g_strokes, miss_rc, s=30),
            option_row([fig_tile(s, s=30) for s in opts], gap=16),
        ], gap=12)

        ans_letter = LETTERS[ans_idx]
        expl = expl_fmt.format(ans=ans_letter)

        d.problem(
            f"Practice {set_num}.{p_idx}",
            text,
            fig_p,
            "below",
        )
        key.append((f"{set_num}.{p_idx}", ans_letter, expl))


GENERATE = q_2002_1

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=10, seed=test_seed)
        assert len(collector.problems) == len(key) == 11
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds with 10 practice problems each!")
