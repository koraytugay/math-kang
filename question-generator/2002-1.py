# Model: argon
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
QUESTION_ID = (2002, 1)


def fig_tile(strokes, s=26):
    """Draw a single square tile of size s with strokes."""
    w = h = s

    def draw(c, x, y):
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.rect(x, y, s, s, stroke=1, fill=0)
        c.setLineWidth(1.5)
        for kind, pts in strokes:
            if kind == "line":
                (x1, y1), (x2, y2) = pts
                c.line(x + x1 * s, y + y1 * s, x + x2 * s, y + y2 * s)
            elif kind == "curve":
                (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pts
                p = c.beginPath()
                p.moveTo(x + x1 * s, y + y1 * s)
                p.curveTo(x + cx1 * s, y + cy1 * s, x + cx2 * s, y + cy2 * s, x + x2 * s, y + y2 * s)
                c.drawPath(p, stroke=1, fill=0)
    return w, h, draw


def fig_tile_grid(n_rows, n_cols, cell_strokes, missing_rc, s=26):
    """Draw a grid of tiles where missing_rc is dashed with a question mark."""
    w = n_cols * s
    h = n_rows * s

    def draw(c, x, y):
        top = y + h
        for r in range(n_rows):
            for col in range(n_cols):
                cx = x + col * s
                cy = top - (r + 1) * s
                if (r, col) == missing_rc:
                    c.setLineWidth(1.0)
                    c.setStrokeColor(colors.black)
                    c.setDash(2, 2)
                    c.rect(cx, cy, s, s, stroke=1, fill=0)
                    c.setDash([])
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 5, "?")
                else:
                    c.setLineWidth(0.8)
                    c.setStrokeColor(colors.black)
                    c.rect(cx, cy, s, s, stroke=1, fill=0)
                    strokes = cell_strokes.get((r, col), [])
                    c.setLineWidth(1.5)
                    for kind, pts in strokes:
                        if kind == "line":
                            (x1, y1), (x2, y2) = pts
                            c.line(cx + x1 * s, cy + y1 * s, cx + x2 * s, cy + y2 * s)
                        elif kind == "curve":
                            (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pts
                            p = c.beginPath()
                            p.moveTo(cx + x1 * s, cy + y1 * s)
                            p.curveTo(cx + cx1 * s, cy + cy1 * s, cx + cx2 * s, cy + cy2 * s, cx + x2 * s, cy + y2 * s)
                            c.drawPath(p, stroke=1, fill=0)
    return w, h, draw


def check_missing_tile(tile_opts, correct_idx, top_conn, bot_conn, left_conn, right_conn):
    results = []
    for opt in tile_opts:
        ok = (
            opt.get("top", []) == top_conn
            and opt.get("bot", []) == bot_conn
            and opt.get("left", []) == left_conn
            and opt.get("right", []) == right_conn
        )
        results.append(ok)
    assert results[correct_idx] is True
    matches = [i for i, r in enumerate(results) if r]
    assert matches == [correct_idx], f"Expected unique match {correct_idx}, got {matches}"


def q_2002_1(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Missing puzzle tile", "Based on 2002, Problem 1")

    # Original 2002 #1
    t0_meta = [
        {"left": [0.5], "right": [0.8]},
        {"top": [0.2], "left": [0.5]},
        {"top": [0.2, 0.8], "right": [0.5]},
        {"top": [0.2, 0.5], "bot": [0.5]},
        {"left": [0.3], "bot": [0.7]},
    ]
    check_missing_tile(t0_meta, 3, [0.2, 0.5], [0.5], [], [])

    if include_orig:
        grid0 = {
            (0, 3): [("curve", ((0.1, 0.9), (0.1, 0.4), (0.2, 0.2), (0.2, 0.0))),
                     ("curve", ((0.7, 0.8), (0.6, 0.4), (0.5, 0.2), (0.5, 0.0)))],
            (2, 3): [("line", ((0.5, 1.0), (0.5, 0.0)))],
            (1, 2): [("curve", ((0.2, 0.7), (0.5, 0.7), (0.8, 0.5), (1.0, 0.5)))],
            (2, 2): [("curve", ((0.3, 0.9), (0.4, 0.5), (0.5, 0.3), (0.7, 0.0)))],
            (2, 1): [("line", ((0.0, 0.2), (1.0, 0.2)))],
            (2, 0): [("curve", ((1.0, 0.2), (0.6, 0.2), (0.3, 0.4), (0.1, 0.7)))],
        }
        opt0_strokes = [
            [("line", ((0.0, 0.5), (1.0, 0.8)))],
            [("curve", ((0.2, 1.0), (0.2, 0.6), (0.1, 0.5), (0.0, 0.5)))],
            [("line", ((0.2, 1.0), (1.0, 0.5))), ("line", ((0.8, 1.0), (1.0, 0.5)))],
            [("curve", ((0.2, 1.0), (0.2, 0.5), (0.5, 0.5), (0.5, 0.0))),
             ("line", ((0.5, 1.0), (0.5, 0.5)))],
            [("curve", ((0.0, 0.3), (0.4, 0.3), (0.7, 0.3), (0.7, 0.0)))],
        ]
        fig0 = vstack([
            fig_tile_grid(3, 4, grid0, (1, 3), s=28),
            option_row([fig_tile(s, s=28) for s in opt0_strokes], gap=16),
        ], gap=12)
        d.problem(
            "Original 2002 #1.",
            "Which of the squares below is missing from the picture of the kangaroo?",
            fig0,
            "below",
        )
        key.append((
            "2002 #1",
            "D",
            "Looking at the grid, the neck lines enter the missing square from the top at two points, "
            "and the leg continues down through the bottom edge. Tile D is the only square with two lines at the top "
            "and one line at the bottom connecting to the kangaroo's body.",
        ))

    # Practice 1.1: 3x3 grid track, missing center tile (1, 1). Enters top at 0.5, exits right at 0.5.
    t1_meta = [
        {"top": [0.5], "bot": [0.5]},
        {"top": [0.5], "right": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"left": [0.5], "bot": [0.5]},
        {"top": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t1_meta, 1, [0.5], [], [], [0.5])
    grid1 = {
        (0, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (1, 2): [("curve", ((0.0, 0.5), (0.4, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        (2, 2): [("curve", ((0.5, 1.0), (0.5, 0.5), (0.3, 0.2), (0.0, 0.2)))],
        (2, 1): [("line", ((1.0, 0.2), (0.0, 0.2)))],
        (2, 0): [("curve", ((1.0, 0.2), (0.5, 0.2), (0.2, 0.4), (0.2, 1.0)))],
        (1, 0): [("line", ((0.2, 0.0), (0.2, 1.0)))],
    }
    opt1_strokes = [
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("curve", ((0.0, 0.5), (0.3, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.6), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig1 = vstack([
        fig_tile_grid(3, 3, grid1, (1, 1), s=28),
        option_row([fig_tile(s, s=28) for s in opt1_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.1",
        "A train track runs across the grid below. Which tile belongs in the empty square marked with a question mark (?) "
        "to complete the continuous track?",
        fig1,
        "below",
    )
    key.append((
        f"{set_num}.1",
        "B",
        "The track enters the empty square from the top at the center and continues out to the right. "
        "Tile B contains the curved track connecting the top edge to the right edge.",
    ))

    # Practice 1.2: 4x3 grid, missing tile (1, 2). Enters left at 0.5, exits bottom at 0.5.
    t2_meta = [
        {"top": [0.5], "right": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"top": [0.5], "bot": [0.5]},
        {"left": [0.5], "bot": [0.5]},
        {"top": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t2_meta, 3, [], [0.5], [0.5], [])
    grid2 = {
        (1, 0): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (1, 1): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (2, 2): [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        (2, 3): [("line", ((0.0, 0.5), (1.0, 0.5)))],
    }
    opt2_strokes = [
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("curve", ((0.0, 0.5), (0.4, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.6), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig2 = vstack([
        fig_tile_grid(3, 4, grid2, (1, 2), s=28),
        option_row([fig_tile(s, s=28) for s in opt2_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.2",
        "A pipe connects across the grid. Which tile is missing at the question mark (?) "
        "to connect the left pipe to the bottom pipe?",
        fig2,
        "below",
    )
    key.append((
        f"{set_num}.2",
        "D",
        "The incoming pipe comes from the left at the middle, and exits through the bottom edge at the middle. "
        "Tile D correctly turns the pipe from left to bottom.",
    ))

    # Practice 1.3: 3x3 grid crossing tracks, missing center tile (1, 1). Crossing (top-bot and left-right).
    t3_meta = [
        {"top": [0.5], "bot": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"top": [0.5], "bot": [0.5], "left": [0.5], "right": [0.5]},
        {"top": [0.5], "right": [0.5]},
        {"bot": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t3_meta, 2, [0.5], [0.5], [0.5], [0.5])
    grid3 = {
        (0, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (2, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (1, 0): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (1, 2): [("line", ((0.0, 0.5), (1.0, 0.5)))],
    }
    opt3_strokes = [
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("line", ((0.5, 1.0), (0.5, 0.0))), ("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("curve", ((0.5, 0.0), (0.5, 0.4), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig3 = vstack([
        fig_tile_grid(3, 3, grid3, (1, 1), s=28),
        option_row([fig_tile(s, s=28) for s in opt3_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.3",
        "Two roads cross each other on the map below: one road runs vertically and the other runs horizontally. "
        "Which tile belongs in the empty square marked with a question mark (?) so both roads can continue across the square?",
        fig3,
        "below",
    )
    key.append((
        f"{set_num}.3",
        "C",
        "Both the vertical road (top to bottom) and the horizontal road (left to right) pass through the missing square. "
        "Tile C shows the intersection of both roads.",
    ))

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
    print(f"Verified {QUESTION_ID} (model={MODEL}): {len(collector.problems)} problems generated.")
