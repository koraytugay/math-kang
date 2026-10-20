# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #10 - Question Generator."""
import os
import sys
import random
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2007, 10)


def fig_mini_sudoku(grid, s=26):
    w = 3 * s + 8
    h = 3 * s + 8

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4

        for r in range(3):
            for col in range(3):
                cy = oy + (2 - r) * s
                cx = ox + col * s

                val = grid[r][col]
                if val in ("A", "B"):
                    c.setFillColor(colors.Color(0.9, 0.9, 0.9))
                    c.rect(cx, cy, s, s, fill=1, stroke=0)

                c.setStrokeColor(colors.black)
                c.setLineWidth(1.0)
                c.rect(cx, cy, s, s, fill=0, stroke=1)

                if val is not None:
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 5, str(val))

        c.setLineWidth(2.0)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, 3 * s, 3 * s, fill=0, stroke=1)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


LATIN_3X3 = []
for _r0 in itertools.permutations([1, 2, 3]):
    for _r1 in itertools.permutations([1, 2, 3]):
        for _r2 in itertools.permutations([1, 2, 3]):
            _b = [_r0, _r1, _r2]
            if all(len(set(_b[r][c] for r in range(3))) == 3 for c in range(3)):
                LATIN_3X3.append(_b)


def _format_val_set(vals):
    if vals == [1]:
        return "only 1"
    elif vals == [2]:
        return "only 2"
    elif vals == [3]:
        return "only 3"
    elif vals == [1, 2]:
        return "1 or 2"
    elif vals == [2, 3]:
        return "2 or 3"
    elif vals == [1, 3]:
        return "1 or 3"
    elif vals == [1, 2, 3]:
        return "1, 2 or 3"
    raise ValueError(f"Unexpected values: {vals}")


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
        expected = _format_val_set(vals)
        assert choices[answer_idx] == expected, f"Expected {expected}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if ch == expected]
        assert matches == [answer_idx], f"Multiple or no choices match {expected}: {matches}"

    elif question_type == "sum_cells":
        ar, ac = positions["A"]
        br, bc = positions["B"]
        sums = set(b[ar][ac] + b[br][bc] for b in matching)
        assert len(sums) == 1, f"Multiple possible sums: {sums}"
        val = sums.pop()
        assert int(choices[answer_idx]) == val, f"Expected {val}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if int(ch) == val]
        assert matches == [answer_idx], f"Multiple or no choices match {val}: {matches}"


NAMES = ["Leo", "Maya", "Lucas", "Clara", "Noah", "Elena", "Sam", "Zoe"]
ALL_CELLS = [(r, c) for r in range(3) for c in range(3)]


def _generate_dynamic_sudoku_problem(rng, mode_idx=0):
    """Procedurally generate a 3x3 mini-sudoku problem across 3 logical deduction modes."""
    actor = rng.choice(NAMES)
    m = mode_idx % 3

    if m == 0:
        # Mode 0: 3 clues, 1 "?" cell whose value is uniquely forced (and not trivially in a row/col with 2 clues)
        for _ in range(500):
            board = rng.choice(LATIN_3X3)
            clues = rng.sample(ALL_CELLS, 3)
            rem = [p for p in ALL_CELLS if p not in clues]
            q_cell = rng.choice(rem)
            qr, qc = q_cell
            # Avoid trivial case where qr or qc already has 2 given clues
            if sum(1 for r, _ in clues if r == qr) >= 2 or sum(1 for _, c in clues if c == qc) >= 2:
                continue
            matching = [b for b in LATIN_3X3 if all(b[r][c] == board[r][c] for r, c in clues)]
            vals = sorted(list(set(b[qr][qc] for b in matching)))
            if len(vals) == 1:
                grid = [[None] * 3 for _ in range(3)]
                for r, c in clues:
                    grid[r][c] = str(board[r][c])
                grid[qr][qc] = "?"
                if grid == [["1", "?", None], ["2", "1", None], [None, None, None]]:
                    continue
                expected = _format_val_set(vals)
                two_opt = rng.choice(["1 or 2", "2 or 3", "1 or 3"])
                opts = ["only 1", "only 2", "only 3", two_opt, "1, 2 or 3"]
                ans_idx = opts.index(expected)
                check_mini_sudoku(grid, opts, ans_idx, question_type="single_cell")
                sol_b = matching[0]
                text = (
                    f"The square in the figure is a <i>mini-sudoku</i>: each row and each column must contain "
                    f"the numbers 1, 2, and 3 exactly once. {actor} started to fill in the square as shown. "
                    f"Which number should {actor} write in the cell marked by a question mark (?) ?"
                )
                expl = (
                    f"Completing the rows and columns so each contains 1, 2, and 3 once forces the completed board "
                    f"to have rows {list(sol_b[0])}, {list(sol_b[1])}, and {list(sol_b[2])}. "
                    f"Therefore, the cell marked '?' at row {qr + 1}, column {qc + 1} must be {vals[0]} ({expected})."
                )
                return grid, opts, ans_idx, "single_cell", text, expl

    elif m == 1:
        # Mode 1: 2 clues, 1 "?" cell that can take two possible values ("1 or 2", "2 or 3", or "1 or 3")
        for _ in range(500):
            board = rng.choice(LATIN_3X3)
            clues = rng.sample(ALL_CELLS, 2)
            rem = [p for p in ALL_CELLS if p not in clues]
            q_cell = rng.choice(rem)
            qr, qc = q_cell
            matching = [b for b in LATIN_3X3 if all(b[r][c] == board[r][c] for r, c in clues)]
            vals = sorted(list(set(b[qr][qc] for b in matching)))
            if len(vals) == 2:
                grid = [[None] * 3 for _ in range(3)]
                for r, c in clues:
                    grid[r][c] = str(board[r][c])
                grid[qr][qc] = "?"
                expected = _format_val_set(vals)
                opts = ["only 1", "only 2", "only 3", expected, "1, 2 or 3"]
                ans_idx = 3
                check_mini_sudoku(grid, opts, ans_idx, question_type="single_cell")
                text = (
                    f"{actor} started filling in the 3 × 3 mini-sudoku square using the numbers 1, 2, and 3 "
                    f"so that each number appears once in every row and once in every column. "
                    f"Which number(s) could {actor} write in the cell marked by a question mark (?) ?"
                )
                expl = (
                    f"From the given clues, the cell marked '?' at row {qr + 1}, column {qc + 1} cannot be "
                    f"{({1, 2, 3} - set(vals)).pop()}, but there are valid completions of the Latin square where '?' "
                    f"is {vals[0]} and where '?' is {vals[1]}. Thus {actor} can write {expected}."
                )
                return grid, opts, ans_idx, "single_cell", text, expl

    else:
        # Mode 2: 3 clues, two marked cells A and B -> ask for the sum A + B
        for _ in range(500):
            board = rng.choice(LATIN_3X3)
            clues = rng.sample(ALL_CELLS, 3)
            matching = [b for b in LATIN_3X3 if all(b[r][c] == board[r][c] for r, c in clues)]
            if len(matching) != 1:
                continue
            rem = [p for p in ALL_CELLS if p not in clues]
            cell_a, cell_b = rng.sample(rem, 2)
            ar, ac = cell_a
            br, bc = cell_b
            grid = [[None] * 3 for _ in range(3)]
            for r, c in clues:
                grid[r][c] = str(board[r][c])
            grid[ar][ac] = "A"
            grid[br][bc] = "B"
            va, vb = board[ar][ac], board[br][bc]
            s_ab = va + vb
            opts = [2, 3, 4, 5, 6]
            rng.shuffle(opts)
            ans_idx = opts.index(s_ab)
            check_mini_sudoku(grid, opts, ans_idx, question_type="sum_cells")
            text = (
                f"{actor} filled in the mini-sudoku square with numbers 1, 2, and 3 so that each number appears "
                f"in each row and in each column. Two cells are marked with letters A and B (see picture). "
                f"What is the sum of the numbers in cells A and B?"
            )
            expl = (
                f"The clues uniquely determine the 3 × 3 Latin square with rows {list(board[0])}, {list(board[1])}, "
                f"and {list(board[2])}. Thus cell A is {va} and cell B is {vb}, giving A + B = {va} + {vb} = {s_ab}."
            )
            return grid, opts, ans_idx, "sum_cells", text, expl

    raise RuntimeError("Failed to generate mini-sudoku problem")


def q_2007_10(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(
        f"Problem {set_num}: 2007 #10 - Mini-Sudoku",
        "Arranging numbers 1, 2, and 3 in a 3×3 square (Latin square logic)",
    )

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

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        grid, opts, ans_idx, qtype, text, expl = _generate_dynamic_sudoku_problem(rng, mode_idx=m)
        check_mini_sudoku(grid, opts, ans_idx, question_type=qtype)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_mini_sudoku(grid),
            "right",
            opts,
            choice_cols=5,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_10

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
