# Model: argon
"""Math Kangaroo 2002, Problem #12 - Question Generator."""
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

    return w, h, draw


def path_length_and_cells(path, grid_cols=13, grid_rows=10):
    assert path[0][1] == 0, f"Path must start at y=0, got {path[0]}"
    assert path[-1][1] == grid_rows + 1, f"Path must end at y={grid_rows + 1}, got {path[-1]}"
    total = 0
    used_vertices = {path[0]}
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert 0 <= x1 <= grid_cols and 0 <= x2 <= grid_cols, f"x out of bounds: {(x1, x2)}"
        assert 0 <= y1 <= grid_rows + 1 and 0 <= y2 <= grid_rows + 1, f"y out of bounds: {(y1, y2)}"
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        assert (dx == 0) ^ (dy == 0), f"Non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}"
        step_x = 0 if x2 == x1 else (1 if x2 > x1 else -1)
        step_y = 0 if y2 == y1 else (1 if y2 > y1 else -1)
        steps = dx + dy
        for k in range(1, steps + 1):
            v = (x1 + k * step_x, y1 + k * step_y)
            assert v not in used_vertices, f"Self-intersecting path at {v}"
            used_vertices.add(v)
        total += steps
    return total, used_vertices


def check_zigzag_race(paths, expected_lengths, answer_idx):
    all_vertices = set()
    lengths = []
    for p in paths:
        L, verts = path_length_and_cells(p)
        assert not (all_vertices & verts), f"Paths overlap at {all_vertices & verts}"
        all_vertices |= verts
        lengths.append(L)
    assert lengths == list(expected_lengths), f"Expected path lengths {expected_lengths}, got {lengths}"
    assert 0 <= answer_idx < 5


def q_2002_12(d, key, set_num=3, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #12 - Kangaroo Zigzag Run",
        "Comparing total grid-segment lengths of zigzag paths",
    )

    # Original 2002 #12: Mary = 21, Norbert = 21, Oscar = 19 -> Answer: E
    if include_orig:
        paths0 = [
            # Mary: 11 vertical + (2+3+1+1+1+2)=10 horizontal = 21
            [(2, 0), (2, 3), (4, 3), (4, 5), (1, 5), (1, 6), (0, 6), (0, 7), (1, 7), (1, 8), (0, 8), (0, 10), (2, 10), (2, 11)],
            # Norbert: 11 vertical + (1+2+1+1+1+2+1+1)=10 horizontal = 21
            [(6, 0), (6, 1), (7, 1), (7, 2), (5, 2), (5, 3), (6, 3), (6, 4), (5, 4), (5, 5), (6, 5), (6, 6), (8, 6), (8, 8), (7, 8), (7, 9), (6, 9), (6, 11)],
            # Oscar: 11 vertical + (1+1+1+1+1+1+1+1)=8 horizontal = 19
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

    practices = [
        # Practice .1: Anna = 19, Ben = 21, Clara = 21 -> Answer: A (Anna is first)
        (
            ["Anna", "Ben", "Clara"],
            [
                # Anna: 11 vertical + (2+2+1+1+1+1)=8 horizontal = 19
                [(2, 0), (2, 2), (0, 2), (0, 5), (2, 5), (2, 7), (3, 7), (3, 8), (2, 8), (2, 9), (1, 9), (1, 10), (2, 10), (2, 11)],
                # Ben: 11 vertical + (2+3+2+1+2)=10 horizontal = 21
                [(6, 0), (6, 2), (8, 2), (8, 4), (5, 4), (5, 6), (7, 6), (7, 8), (8, 8), (8, 10), (6, 10), (6, 11)],
                # Clara: 11 vertical + (2+2+2+1+1+2)=10 horizontal = 21
                [(11, 0), (11, 2), (13, 2), (13, 4), (11, 4), (11, 6), (9, 6), (9, 8), (10, 8), (10, 9), (9, 9), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 21, 21],
            [
                "Anna is first",
                "Ben is first",
                "Clara is first",
                "Anna is last",
                "They all arrive at the same time",
            ],
            0,
            1,
            "During a zigzag run the kangaroos Anna, Ben, and Clara jump along the paths drawn in the picture "
            "at the same speed. Which statement is true?",
            "Each kangaroo travels 11 units upward. Counting horizontal steps: Anna takes 2 + 2 + 1 + 1 + 1 + 1 = 8 "
            "horizontal steps (total 19), Ben takes 2 + 3 + 2 + 1 + 2 = 10 horizontal steps (total 21), and Clara takes "
            "2 + 2 + 2 + 1 + 1 + 2 = 10 horizontal steps (total 21). Since 19 is the shortest path, Anna finishes first.",
        ),
        # Practice .2: Dan = 19, Eva = 23, Finn = 19 -> Answer: B (Dan and Finn arrive at the same time)
        (
            ["Dan", "Eva", "Finn"],
            [
                # Dan: 11 vertical + (2+3+2+1)=8 horizontal = 19
                [(2, 0), (2, 3), (0, 3), (0, 6), (3, 6), (3, 9), (1, 9), (1, 10), (2, 10), (2, 11)],
                # Eva: 11 vertical + (2+3+3+2+2)=12 horizontal = 23
                [(6, 0), (6, 2), (8, 2), (8, 4), (5, 4), (5, 7), (8, 7), (8, 9), (6, 9), (6, 10), (8, 10), (8, 11)],
                # Finn: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(11, 0), (11, 2), (13, 2), (13, 5), (11, 5), (11, 8), (9, 8), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 23, 19],
            [
                "Eva is first",
                "Dan and Finn arrive at the same time",
                "Finn is last",
                "Dan and Eva arrive at the same time",
                "They all arrive at the same time",
            ],
            1,
            1,
            "The kangaroos Dan, Eva, and Finn jump along the zigzag paths shown at the same speed. "
            "Which statement is true?",
            "All three paths go 11 units upward. Counting horizontal steps: Dan takes 2 + 3 + 2 + 1 = 8 horizontal steps "
            "(total 19), Eva takes 2 + 3 + 3 + 2 + 2 = 12 horizontal steps (total 23), and Finn takes 2 + 2 + 2 + 2 = 8 "
            "horizontal steps (total 19). Therefore, Dan and Finn arrive at the same time.",
        ),
        # Practice .3: Leo = 19, Mia = 19, Noah = 19 -> Answer: C (They all arrive at the same time)
        (
            ["Leo", "Mia", "Noah"],
            [
                # Leo: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(2, 0), (2, 2), (0, 2), (0, 5), (2, 5), (2, 7), (0, 7), (0, 9), (2, 9), (2, 11)],
                # Mia: 11 vertical + (1+2+2+2+1)=8 horizontal = 19
                [(6, 0), (6, 2), (5, 2), (5, 4), (7, 4), (7, 6), (5, 6), (5, 9), (7, 9), (7, 10), (6, 10), (6, 11)],
                # Noah: 11 vertical + (2+3+1+2)=8 horizontal = 19
                [(11, 0), (11, 3), (13, 3), (13, 6), (10, 6), (10, 8), (9, 8), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 19, 19],
            [
                "Leo is first",
                "Mia is last",
                "They all arrive at the same time",
                "Only Leo and Mia arrive at the same time",
                "Noah is first",
            ],
            2,
            1,
            "Leo, Mia, and Noah jump from the bottom to the top of the grid along the drawn paths at the same speed. "
            "Which statement is true?",
            "Every kangaroo moves 11 units upward. Counting horizontal steps: Leo takes 2 + 2 + 2 + 2 = 8 horizontal steps "
            "(total 19), Mia takes 1 + 2 + 2 + 2 + 1 = 8 horizontal steps (total 19), and Noah takes 2 + 3 + 1 + 2 = 8 "
            "horizontal steps (total 19). Since all three travel 19 grid segments, they all arrive at the same time.",
        ),
        # Practice .4: Max = 17, Nina = 19, Otto = 21 -> Answer: D (Otto is last)
        (
            ["Max", "Nina", "Otto"],
            [
                # Max: 11 vertical + (2+2+1+1)=6 horizontal = 17
                [(2, 0), (2, 3), (0, 3), (0, 6), (2, 6), (2, 8), (1, 8), (1, 10), (2, 10), (2, 11)],
                # Nina: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(6, 0), (6, 2), (8, 2), (8, 5), (6, 5), (6, 7), (4, 7), (4, 9), (6, 9), (6, 11)],
                # Otto: 11 vertical + (2+3+3+2)=10 horizontal = 21
                [(11, 0), (11, 2), (13, 2), (13, 5), (10, 5), (10, 8), (13, 8), (13, 10), (11, 10), (11, 11)],
            ],
            [17, 19, 21],
            [
                "Max is last",
                "Nina is first",
                "Max and Nina arrive at the same time",
                "Otto is last",
                "Otto is first",
            ],
            3,
            1,
            "Max, Nina, and Otto jump along the paths drawn in the picture at the same speed. "
            "Which statement is true?",
            "All three paths have 11 vertical steps upward. Counting horizontal steps: Max takes 2 + 2 + 1 + 1 = 6 "
            "horizontal steps (total 17), Nina takes 2 + 2 + 2 + 2 = 8 horizontal steps (total 19), and Otto takes "
            "2 + 3 + 3 + 2 = 10 horizontal steps (total 21). Otto has the longest path (21 steps), so Otto is last.",
        ),
        # Practice .5: Ruby = 21, Sam = 17, Toby = 19 -> Shortest path length = 17 m (Answer: C)
        (
            ["Ruby", "Sam", "Toby"],
            [
                # Ruby: 11 vertical + (2+3+3+2)=10 horizontal = 21
                [(2, 0), (2, 2), (0, 2), (0, 5), (3, 5), (3, 8), (0, 8), (0, 10), (2, 10), (2, 11)],
                # Sam: 11 vertical + (1+2+2+1)=6 horizontal = 17
                [(6, 0), (6, 3), (7, 3), (7, 6), (5, 6), (5, 9), (7, 9), (7, 10), (6, 10), (6, 11)],
                # Toby: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(11, 0), (11, 2), (13, 2), (13, 5), (11, 5), (11, 7), (9, 7), (9, 9), (11, 9), (11, 11)],
            ],
            [21, 17, 19],
            ["15 m", "16 m", "17 m", "19 m", "21 m"],
            2,
            5,
            "Three kangaroos — Ruby, Sam, and Toby — jump from the bottom to the top along the paths shown on the grid, "
            "where each small grid square has a side of 1 m. What is the total length of the <b>shortest</b> path?",
            "Every kangaroo travels 11 m upward. Counting horizontal steps: Ruby travels 2 + 3 + 3 + 2 = 10 m horizontally "
            "(total 11 + 10 = 21 m), Sam travels 1 + 2 + 2 + 1 = 6 m horizontally (total 11 + 6 = 17 m), and Toby travels "
            "2 + 2 + 2 + 2 = 8 m horizontally (total 11 + 8 = 19 m). The shortest path is Sam's path at 17 m.",
        ),
    ]

    for idx, (names, paths, exp_lens, opts, ans_idx, cols, text, expl) in enumerate(practices[:num_practice], start=1):
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
