# Model: argon
"""Math Kangaroo 2007, Problem #10 - Question Generator."""
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
QUESTION_ID = (2007, 10)


def fig_mini_sudoku(grid, s=26):
    w = 3 * s + 8
    h = 3 * s + 8

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4

        # Draw cells
        for r in range(3):
            for col in range(3):
                cy = oy + (2 - r) * s
                cx = ox + col * s

                val = grid[r][col]
                if val in ("A", "B"):
                    c.setFillColor(colors.Color(0.9, 0.9, 0.9))
                    c.rect(cx, cy, s, s, fill=1, stroke=0)

                # Draw cell borders
                c.setStrokeColor(colors.black)
                c.setLineWidth(1.0)
                c.rect(cx, cy, s, s, fill=0, stroke=1)

                # Draw text
                if val is not None:
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 5, str(val))

        # Outer thick border
        c.setLineWidth(2.0)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, 3 * s, 3 * s, fill=0, stroke=1)

        # Always reset canvas colors
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


LATIN_3X3 = []
for _r0 in itertools.permutations([1, 2, 3]):
    for _r1 in itertools.permutations([1, 2, 3]):
        for _r2 in itertools.permutations([1, 2, 3]):
            _b = [_r0, _r1, _r2]
            if all(len(set(_b[r][c] for r in range(3))) == 3 for c in range(3)):
                LATIN_3X3.append(_b)


def check_mini_sudoku(grid, choices, answer_idx, question_type="single_cell"):
    fixed = {}
    positions = {}
    for r in range(3):
        for c in range(3):
            v = grid[r][c]
            if v in ("1", "2", "3"):
                fixed[(r, c)] = int(v)
            elif v is not None:
                positions[v] = (r, c)

    matching = [b for b in LATIN_3X3 if all(b[r][c] == val for (r, c), val in fixed.items())]
    assert len(matching) > 0, "No valid mini-sudoku solution for this board!"

    if question_type == "single_cell":
        qr, qc = positions["?"]
        vals = sorted(list(set(b[qr][qc] for b in matching)))
        if vals == [1]:
            expected = "only 1"
        elif vals == [2]:
            expected = "only 2"
        elif vals == [3]:
            expected = "only 3"
        elif vals == [1, 2]:
            expected = "1 or 2"
        elif vals == [2, 3]:
            expected = "2 or 3"
        elif vals == [1, 3]:
            expected = "1 or 3"
        elif vals == [1, 2, 3]:
            expected = "1, 2 or 3"
        else:
            raise ValueError(f"Unexpected values: {vals}")

        assert choices[answer_idx] == expected, f"Expected {expected}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if ch == expected]
        assert matches == [answer_idx], f"Multiple or no choices match {expected}: {matches}"

    elif question_type == "sum_cells":
        ar, ac = positions["A"]
        br, bc = positions["B"]
        sums = set(b[ar][ac] + b[br][bc] for b in matching)
        assert len(sums) == 1, f"Multiple possible sums: {sums}"
        val = sums.pop()
        assert choices[answer_idx] == val, f"Expected {val}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if ch == val]
        assert matches == [answer_idx], f"Multiple or no choices match {val}: {matches}"


def q_2007_10(d, key, set_num=1, include_orig=True):
    d.heading(
        f"Problem {set_num}: 2007 #10 - Mini-Sudoku",
        "Arranging numbers 1, 2, and 3 in a 3×3 square (Latin square logic)",
    )

    # Original 2007 #10
    if include_orig:
        G0 = [
            ["1", "?", None],
            ["2", "1", None],
            [None, None, None],
        ]
        opts0 = ["only 1", "only 2", "only 3", "2 or 3", "1, 2 or 3"]
        check_mini_sudoku(G0, opts0, 2)
        d.problem(
            "2007 #10",
            "The square in the figure is a <i>mini-sudoku</i>: the numbers 1, 2, and 3 must be "
            "written in the cells so that each of them appears in each row and in each column. "
            "Harry started to fill in the square. Which number should he write in the cell "
            "that is marked by a question mark (?) ?",
            fig_mini_sudoku(G0),
            "right",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2007 #10",
            "C",
            "In a 3 × 3 mini-sudoku, each row and column must contain the numbers 1, 2, and 3 exactly once. "
            "The middle row already has 2 and 1, so its third cell must be 3. The first column has 1 and 2, "
            "so its bottom cell must be 3. Now look at the top row: the first cell is 1, so the question mark "
            "and top-right cell must be 2 and 3. But column 3 already has 3 in the middle row, so the top-right "
            "cell cannot be 3 (it must be 2). Therefore, the question mark cell must be 3 (only 3).",
        ))

    # Practice .1 (Answer: A) only 1)
    G1 = [
        ["?", "2", None],
        ["2", "3", None],
        [None, None, None],
    ]
    opts1 = ["only 1", "only 2", "only 3", "1 or 2", "1, 2 or 3"]
    check_mini_sudoku(G1, opts1, 0)
    d.problem(
        f"Practice {set_num}.1",
        "The square in the figure is a <i>mini-sudoku</i>: each row and each column must contain "
        "the numbers 1, 2, and 3 exactly once. Leo started to fill in the square as shown. "
        "Which number should he write in the cell marked by a question mark (?) ?",
        fig_mini_sudoku(G1),
        "right",
        opts1,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The middle row has 2 and 3, so its third cell must be 1. The middle column has 2 and 3, "
        "so its bottom cell must be 1. In the top row, the middle cell is 2, so the remaining two cells "
        "(the question mark and the top-right cell) must be 1 and 3. If the question mark were 3, "
        "the top-right cell would be 1, but column 3 already has 1 in the middle row! "
        "Thus, the question mark cannot be 3. It must be 1 (only 1).",
    ))

    # Practice .2 (Answer: D) 2 or 3)
    G2 = [
        ["1", "?", None],
        ["2", None, None],
        [None, None, None],
    ]
    opts2 = ["only 1", "only 2", "only 3", "2 or 3", "1, 2 or 3"]
    check_mini_sudoku(G2, opts2, 3)
    d.problem(
        f"Practice {set_num}.2",
        "Maya started filling in the 3×3 mini-sudoku square using the numbers 1, 2, and 3. "
        "Each number must appear once in every row and once in every column. "
        "Which number(s) could Maya write in the cell marked by a question mark (?) ?",
        fig_mini_sudoku(G2),
        "right",
        opts2,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "D",
        "Column 1 already has 1 and 2, so its bottom cell must be 3. Row 1 has 1 in the first cell, "
        "so the remaining cells in the top row must be 2 and 3 in some order. Both completions are valid: "
        "if ? is 2, the board can be completed with rows [1, 2, 3], [2, 3, 1], [3, 1, 2]; "
        "if ? is 3, the board can be completed with rows [1, 3, 2], [2, 1, 3], [3, 2, 1]. "
        "Therefore, Maya can write 2 or 3.",
    ))

    # Practice .3 (Twist: Sum of two marked cells A and B; Answer: B) 6)
    G3 = [
        ["1", "A", None],
        ["3", "2", None],
        [None, None, "B"],
    ]
    opts3 = [3, 6, 4, 5, 7]
    check_mini_sudoku(G3, opts3, 1, question_type="sum_cells")
    d.problem(
        f"Practice {set_num}.3",
        "Lucas filled in the mini-sudoku square with numbers 1, 2, and 3 so that each number appears "
        "in each row and in each column. Two cells are marked with letters A and B (see picture). "
        "What is the sum of the numbers in cells A and B?",
        fig_mini_sudoku(G3),
        "right",
        opts3,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "B",
        "The middle row has 3 and 2, so its third cell must be 1. The first column has 1 and 3, "
        "so its bottom cell must be 2. In the third column, the middle cell is 1, so the other two cells "
        "(top-right and bottom-right B) must be 2 and 3. Since the bottom row already has 2 in the first column, "
        "cell B cannot be 2; B must be 3 (making the top-right cell 2). Now in the top row, the numbers are "
        "1, A, and 2, so cell A must be 3. Therefore, the sum of the numbers in cells A and B is 3 + 3 = 6.",
    ))

GENERATE = q_2007_10

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
