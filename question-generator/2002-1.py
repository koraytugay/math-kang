# Model: argon
# Reviewed by argon on high effort
"""Math Kangaroo 2002, Problem #1 - Question Generator."""
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
REVIEWED_BY = "argon (high effort)"
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

    # 1. Verify internal grid continuity across all adjacent non-missing tiles
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

    # 2. Compute required boundary signature for missing_rc from its neighbors
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
    """Rotate tile strokes 90 degrees clockwise: (x, y) -> (y, 1 - x)."""
    out = []
    for kind, pts in strokes:
        out.append((kind, tuple((round(y, 2), round(1.0 - x, 2)) for x, y in pts)))
    return out


def _rot90_ccw(strokes):
    """Rotate tile strokes 90 degrees counter-clockwise: (x, y) -> (1 - y, x)."""
    out = []
    for kind, pts in strokes:
        out.append((kind, tuple((round(1.0 - y, 2), round(x, 2)) for x, y in pts)))
    return out


def _rot180(strokes):
    """Rotate tile strokes 180 degrees: (x, y) -> (1 - x, 1 - y)."""
    out = []
    for kind, pts in strokes:
        out.append((kind, tuple((round(1.0 - x, 2), round(1.0 - y, 2)) for x, y in pts)))
    return out


def _flip_h(strokes):
    """Flip tile strokes horizontally: (x, y) -> (1 - x, y)."""
    out = []
    for kind, pts in strokes:
        out.append((kind, tuple((round(1.0 - x, 2), round(y, 2)) for x, y in pts)))
    return out


def q_2002_1(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Missing puzzle tile", "Based on 2002, Problem 1")

    # ------------------------------------------------------------------
    # Original 2002 #1: 3x4 grid drawing of a Kangaroo, missing tile (1, 3).
    # In 2002.pdf:
    # - Cell (0, 3) has the kangaroo's head & ears; two neck lines touch bot at x=0.22 and x=0.48.
    # - Cell (1, 2) has the kangaroo's arched back touching right at y=0.88, and lower back touching left at y=0.72.
    # - Cell (1, 1) has the kangaroo's lower back from (0.40, 0.0) to (1.0, 0.72), and tail base from (0.15, 0.0) to (1.0, 0.15).
    # - Cell (2, 0) and (2, 1) have the kangaroo's long curved tail.
    # - Cell (2, 2) has the kangaroo's tucked front paw, chest (meeting top-right at (1.0, 0.08) of (1,3)), and hind leg.
    # - Cell (2, 3) has the front tip of the kangaroo's long hind foot (entering from left at y=0.06 and y=0.20, no lines on top).
    # Missing tile (1, 3) has:
    #   1) Short upper-neck bridge from left (0.0, 0.88) -> (0.22, 0.88) -> top (0.22, 1.0)
    #   2) Throat/chest curve from top (0.48, 1.0) -> down-left to (0.0, 0.08)
    # Answer in 2002.pdf is B!
    grid0 = {
        (0, 3): [
            # Kangaroo head, two ears at top-left, snout pointing right, neck meeting bottom at x=0.22 and x=0.48
            ("poly", ((0.22, 0.0), (0.26, 0.22), (0.14, 0.42), (0.08, 0.90), (0.16, 0.78),
                      (0.24, 0.92), (0.42, 0.56), (0.76, 0.32), (0.62, 0.10), (0.48, 0.0))),
        ],
        (1, 2): [
            # Kangaroo upper back from (0.0, 0.72) arching to (1.0, 0.88)
            ("curve", ((0.0, 0.72), (0.35, 0.95), (0.70, 0.95), (1.0, 0.88))),
            # Belly/hip line at bottom-left from (0.0, 0.15) to (0.05, 0.0)
            ("curve", ((0.0, 0.15), (0.04, 0.12), (0.05, 0.06), (0.05, 0.0))),
        ],
        (1, 1): [
            # Back from (0.15, 0.0) up-right to (1.0, 0.72)
            ("curve", ((0.15, 0.0), (0.42, 0.28), (0.72, 0.54), (1.0, 0.72))),
            # Tail underside / hip curve from (0.45, 0.0) to (1.0, 0.15)
            ("curve", ((0.45, 0.0), (0.65, 0.15), (0.85, 0.20), (1.0, 0.15))),
        ],
        (2, 0): [
            # Tip of tail curving up and back to right edge (1.0, 0.48) and (1.0, 0.30)
            ("curve", ((1.0, 0.48), (0.72, 0.34), (0.55, 0.38), (0.50, 0.55))),
            ("curve", ((0.50, 0.55), (0.45, 0.30), (0.68, 0.22), (1.0, 0.30))),
        ],
        (2, 1): [
            # Middle of tail connecting (2, 0) to (1, 1) and (2, 2)
            ("curve", ((0.0, 0.48), (0.06, 0.68), (0.11, 0.85), (0.15, 1.0))),
            ("curve", ((0.0, 0.30), (0.20, 0.55), (0.35, 0.80), (0.45, 1.0))),
            # Hind leg loop sticking slightly into right side of (2, 1)
            ("curve", ((1.0, 0.55), (0.82, 0.32), (0.82, 0.14), (1.0, 0.10))),
        ],
        (2, 2): [
            # Hip entering from top (0.05, 1.0) down to (0.0, 0.55)
            ("curve", ((0.05, 1.0), (0.08, 0.80), (0.05, 0.65), (0.0, 0.55))),
            # Bottom of foot from (0.0, 0.10) across to (1.0, 0.06)
            ("line", ((0.0, 0.10), (1.0, 0.06))),
            # Chest + tucked front paw + top of hind foot: starts at (1.0, 0.92)? Wait: chest meets (1, 3) at (0.0, 0.08) of (1, 3)!
            # Instead of crossing inside (1, 3), in (2, 2) the chest line starts at top-right (1.0, 1.0) or in (1, 2) right at (1.0, 0.08):
            ("poly", ((1.0, 0.95), (0.72, 0.62), (0.58, 0.62), (0.66, 0.78), (0.55, 0.82),
                      (0.35, 0.58), (0.24, 0.32), (0.42, 0.22), (1.0, 0.18))),
        ],
        (2, 3): [
            # Tip of kangaroo's long foot
            ("curve", ((0.0, 0.18), (0.32, 0.15), (0.38, 0.08), (0.0, 0.06))),
            # Notice: (2, 2) has (1.0, 0.95), which connects to (2, 3) at (0.0, 0.95) curving up to (0.08, 1.0)!
            ("curve", ((0.0, 0.95), (0.04, 0.97), (0.06, 0.98), (0.08, 1.0))),
        ],
    }
    # Correct tile B for (1, 3):
    # - top: [0.22, 0.48] (matches (0, 3) bot)
    # - left: [0.88] (matches (1, 2) right)
    # - bot: [0.08] (matches (2, 3) top)
    # - right: []
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
    # Practice variations (4 rich multi-stroke grid drawings, all verified by check_missing_tile_geometry)
    practices = []

    # Practice .1: Sailboat on the waves (3x3 grid, missing center tile (1, 1) -> Answer: C)
    # Center tile (1, 1) has:
    # - Mast going straight from top (0.50, 1.0) to bot (0.50, 0.0)
    # - Left jib sail edge from top (0.20, 1.0) to left (0.0, 0.35), and boom from (0.0, 0.35) to (0.50, 0.35)
    # - Right mainsail edge from top (0.85, 1.0) to right (1.0, 0.25), and boom from (0.50, 0.25) to (1.0, 0.25)
    grid1 = {
        (0, 1): [
            # Top of mast + flag + top of left and right sails
            ("line", ((0.50, 0.0), (0.50, 0.90))),
            ("poly", ((0.50, 0.90), (0.72, 0.82), (0.50, 0.74))),
            ("line", ((0.50, 0.70), (0.20, 0.0))),
            ("line", ((0.50, 0.85), (0.85, 0.0))),
        ],
        (1, 0): [
            # Left tip of jib sail inside (1, 0)
            ("poly", ((1.0, 0.35), (0.65, 0.35), (1.0, 0.82))),
        ],
        (0, 0): [
            ("line", ((1.0, 0.0), (1.0, 0.0))),  # empty sky; wait: (1, 0) has (1.0, 0.82) on right edge, not top!
        ],
        (1, 2): [
            # Right tip of mainsail inside (1, 2)
            ("poly", ((0.0, 0.25), (0.45, 0.25), (0.0, 0.75))),
        ],
        (2, 0): [
            # Left bow of boat hull + wave
            ("poly", ((1.0, 0.75), (0.35, 0.75), (0.65, 0.30), (1.0, 0.30))),
            ("curve", ((0.10, 0.15), (0.40, 0.28), (0.70, 0.02), (1.0, 0.15))),
        ],
        (2, 1): [
            # Middle of hull + mast base at (0.50, 1.0)
            ("line", ((0.50, 1.0), (0.50, 0.75))),
            ("line", ((0.0, 0.75), (1.0, 0.75))),
            ("line", ((0.0, 0.30), (1.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (1.0, 0.15))),
        ],
        (2, 2): [
            # Right stern of hull + wave
            ("poly", ((0.0, 0.75), (0.65, 0.75), (0.40, 0.30), (0.0, 0.30))),
            ("curve", ((0.0, 0.15), (0.35, 0.28), (0.65, 0.02), (0.90, 0.15))),
        ],
    }
    # Clean up (0, 0) and reconcile (1, 0)/(1, 2) with (1, 1):
    del grid1[(0, 0)]
    tile1_C = [
        ("line", ((0.50, 1.0), (0.50, 0.0))),
        ("line", ((0.20, 1.0), (0.0, 0.82))),
        ("line", ((0.0, 0.35), (0.50, 0.35))),
        ("line", ((0.85, 1.0), (1.0, 0.75))),
        ("line", ((0.50, 0.25), (1.0, 0.25))),
    ]
    opt1_strokes = [
        _rot90_cw(tile1_C),
        _flip_h(tile1_C),
        tile1_C,
        _rot180(tile1_C),
        [
            ("line", ((0.50, 1.0), (0.50, 0.0))),
            ("line", ((0.20, 1.0), (0.0, 0.35))),
            ("line", ((0.85, 1.0), (1.0, 0.25))),
        ],
    ]
    practices.append((
        3, 3, grid1, (1, 1), opt1_strokes, 2,
        "Which of the squares below is missing from the picture of the sailboat?",
        "In the center square, the vertical mast runs straight from the top center (0.50) to the bottom center (0.50), "
        "the left jib sail is higher than the right mainsail, and both horizontal booms meet the mast. Only square C "
        "matches all four edges of the missing center square.",
    ))

    # Practice .2: Winding double park trail (3x4 grid, missing tile (1, 2) -> Answer: D)
    # In (1, 2):
    # - top: [0.35, 0.75]
    # - left: [0.25, 0.70]
    # - bot: [0.45]
    # - right: [0.30]
    grid2 = {
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
    tile2_D = [
        ("curve", ((0.0, 0.70), (0.25, 0.70), (0.35, 0.85), (0.35, 1.0))),
        ("curve", ((0.75, 1.0), (0.75, 0.55), (0.85, 0.30), (1.0, 0.30))),
        ("curve", ((0.0, 0.25), (0.30, 0.25), (0.45, 0.15), (0.45, 0.0))),
    ]
    opt2_strokes = [
        _rot90_cw(tile2_D),
        _rot180(tile2_D),
        _flip_h(tile2_D),
        tile2_D,
        _rot90_ccw(tile2_D),
    ]
    practices.append((
        3, 4, grid2, (1, 2), opt2_strokes, 3,
        "Park paths wind across the 3 × 4 map below, and one square tile has been removed. "
        "Which of the tiles (A through E) belongs in the square marked with a question mark (?)?",
        "Checking the four edges of the missing square: two paths enter from the top (at 0.35 and 0.75), "
        "two enter from the left (at 0.25 and 0.70), one exits through the bottom (at 0.45), and one exits "
        "through the right (at 0.30). Only tile D connects all six boundary points properly.",
    ))

    # Practice .3: Geometric Kite & Star Mosaic (3x3 grid, missing right-middle tile (1, 2) -> Answer: A)
    # In (1, 2):
    # - top: [0.35, 0.75]
    # - left: [0.25, 0.75]
    # - bot: [0.55]
    # - right: []
    grid3 = {
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
    tile3_A = [
        ("line", ((0.0, 0.75), (0.35, 1.0))),
        ("poly", ((0.75, 1.0), (0.75, 0.25), (0.0, 0.25))),
        ("line", ((0.55, 0.0), (0.55, 0.25))),
    ]
    opt3_strokes = [
        tile3_A,
        _rot90_cw(tile3_A),
        _flip_h(tile3_A),
        _rot180(tile3_A),
        _rot90_ccw(tile3_A),
    ]
    practices.append((
        3, 3, grid3, (1, 2), opt3_strokes, 0,
        "One square tile is missing from the geometric pattern below. Which tile (A through E) fits in the "
        "empty square marked with a question mark (?)?",
        "Looking at the neighbours of the missing square on the right: two vertical lines enter from the top "
        "(at 0.35 and 0.75), two horizontal lines enter from the left (at 0.25 and 0.75), one vertical line "
        "enters from the bottom (at 0.55), and nothing touches the outer right edge. Only tile A matches.",
    ))

    # Practice .4: Dual-loop railway switchyard (3x4 grid, missing tile (1, 1) -> Answer: E)
    # In (1, 1):
    # - top: [0.30, 0.75]
    # - bot: [0.40]
    # - left: [0.30, 0.70]
    # - right: [0.55]
    grid4 = {
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
    tile4_E = [
        ("curve", ((0.0, 0.70), (0.20, 0.70), (0.30, 0.85), (0.30, 1.0))),
        ("curve", ((0.0, 0.30), (0.30, 0.30), (0.40, 0.15), (0.40, 0.0))),
        ("curve", ((0.75, 1.0), (0.75, 0.65), (0.85, 0.55), (1.0, 0.55))),
    ]
    opt4_strokes = [
        _rot90_cw(tile4_E),
        _flip_h(tile4_E),
        _rot180(tile4_E),
        _rot90_ccw(tile4_E),
        tile4_E,
    ]
    practices.append((
        3, 4, grid4, (1, 1), opt4_strokes, 4,
        "A model train track loops across the 3 × 4 board below. Which tile (A through E) belongs in the "
        "missing square marked with a question mark (?) to make the track continuous?",
        "Tracing the tracks into the missing square: two tracks enter from the left (at 0.30 and 0.70), "
        "two enter from the top (at 0.30 and 0.75), one exits at the bottom (0.40), and one exits at the right (0.55). "
        "Only tile E connects every track without breaks.",
    ))

    # Practice .5: Garden Stone Wall & Archway (3x3 grid, missing center tile (1, 1) -> Answer: B)
    # In (1, 1):
    # - top: [0.25, 0.75]
    # - bot: [0.35]
    # - left: [0.60]
    # - right: [0.20, 0.80]
    grid5 = {
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
    tile5_B = [
        ("poly", ((0.0, 0.60), (0.25, 0.60), (0.25, 1.0))),
        ("poly", ((0.75, 1.0), (0.75, 0.80), (1.0, 0.80))),
        ("poly", ((0.35, 0.0), (0.35, 0.20), (1.0, 0.20))),
    ]
    opt5_strokes = [
        _rot90_cw(tile5_B),
        tile5_B,
        _flip_h(tile5_B),
        _rot180(tile5_B),
        _rot90_ccw(tile5_B),
    ]
    practices.append((
        3, 3, grid5, (1, 1), opt5_strokes, 1,
        "A garden path and archway are drawn across the 3 × 3 grid below, with the middle tile missing. "
        "Which tile (A through E) completes the picture?",
        "In the center square, two arch lines enter from the top (at 0.25 and 0.75), one line enters from the "
        "left (at 0.60), one enters from the bottom (at 0.35), and two exit through the right (at 0.20 and 0.80). "
        "Only tile B connects all of these endpoints cleanly.",
    ))

    # Practice .6: River Confluence & Bridges (3x4 grid, missing tile (1, 2) -> Answer: C)
    # In (1, 2):
    # - top: [0.45]
    # - bot: [0.30, 0.75]
    # - left: [0.55]
    # - right: [0.25, 0.70]
    grid6 = {
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
    tile6_C = [
        ("curve", ((0.0, 0.55), (0.20, 0.55), (0.30, 0.30), (0.30, 0.0))),
        ("curve", ((0.45, 1.0), (0.45, 0.75), (0.70, 0.70), (1.0, 0.70))),
        ("curve", ((0.75, 0.0), (0.75, 0.18), (0.85, 0.25), (1.0, 0.25))),
    ]
    opt6_strokes = [
        _rot90_cw(tile6_C),
        _flip_h(tile6_C),
        tile6_C,
        _rot180(tile6_C),
        _rot90_ccw(tile6_C),
    ]
    practices.append((
        3, 4, grid6, (1, 2), opt6_strokes, 2,
        "Streams flow across the 3 × 4 map below, and one square tile is missing. Which tile (A through E) "
        "fits in the square marked with a question mark (?)?",
        "In the missing square, one stream enters from the left (at 0.55) and curves down to the bottom (at 0.30), "
        "one enters from the top (at 0.45) and curves to the upper-right (at 0.70), and a third connects the "
        "bottom-right (0.75) to the lower-right edge (0.25). Only tile C matches all six boundary crossings.",
    ))

    if isinstance(num_practice, int) and num_practice < 0:
        import random
        selected_practices = random.sample(practices, min(abs(num_practice), len(practices)))
    else:
        selected_practices = practices[:num_practice]

    for idx, (nr, nc, g_strokes, miss_rc, o_strokes, ans_idx, text, expl) in enumerate(selected_practices, start=1):
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
    import inspect
    collector = _ProblemCollector()
    key = []
    sig = inspect.signature(GENERATE)
    if "num_practice" in sig.parameters:
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5)
    else:
        GENERATE(collector, key, set_num=1, include_orig=True)
    assert len(collector.problems) == len(key)
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}): {len(collector.problems)} problems generated.")
