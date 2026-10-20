# Model: argon
"""Math Kangaroo 2007, Problem #21 - Question Generator."""
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
QUESTION_ID = (2007, 21)


def fig_bw_grid_pattern(grid_specs, s=8.5):
    """grid_specs: list of (N, is_black_fn, caption_str)."""
    gap = 14
    widths = [max(N * s, 54) for N, _, _ in grid_specs]
    w = sum(widths) + gap * (len(grid_specs) - 1)
    h = max(N * s for N, _, _ in grid_specs) + 16

    def draw(c, x, y):
        cx = x
        for (N, is_black_fn, cap), box_w in zip(grid_specs, widths):
            gw = N * s
            gx = cx + (box_w - gw) / 2
            gy = y + 14
            for r in range(N):
                for col in range(N):
                    if is_black_fn(r, col, N):
                        c.setFillColor(colors.Color(0.35, 0.35, 0.35))
                    else:
                        c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.setLineWidth(0.75)
                    c.rect(gx + col * s, gy + (N - 1 - r) * s, s, s, stroke=1, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawCentredString(cx + box_w / 2, gy - 10, cap)
            cx += box_w + gap
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_bw_pattern(step_fn, step_idx, choices, ans_idx):
    val = step_fn(step_idx)
    matches = [i for i, ch in enumerate(choices) if int(ch) == val]
    assert matches == [ans_idx], f"BW pattern step {step_idx} -> {val}, choices={choices}, ans_idx={ans_idx}"


def q_2007_21(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Growing Pattern of Black and White Grid Cells", "Based on 2007, Problem 21")

    # Original 2007 #21: step k (k=1,2,3...) has grid size (2k+1)x(2k+1) and k^2 black cells (at odd 0-indexed r,c)
    orig_black_fn = lambda r, c, N: (r % 2 == 1 and c % 2 == 1)
    orig_white_step = lambda k: (2 * k + 1) ** 2 - k ** 2
    assert [orig_white_step(1), orig_white_step(2), orig_white_step(3)] == [8, 21, 40]
    opts0 = ["50", "60", "65", "70", "75"]
    check_bw_pattern(orig_white_step, 4, opts0, 2)

    orig_specs = [
        (3, orig_black_fn, "8 white cells"),
        (5, orig_black_fn, "21 white cells"),
        (7, orig_black_fn, "40 white cells"),
    ]
    if include_orig:
        d.problem(
            "Original 2007 #21.",
            "The following three diagrams represent a pattern in the arrangement of the black and white cells. "
            "If the pattern continues, how many white cells will the next diagram have?",
            fig_bw_grid_pattern(orig_specs),
            "right",
            opts0,
        )
        key.append((
            "2007 #21",
            "C",
            "The grids are 3×3 (with 1×1 = 1 black cell), 5×5 (with 2×2 = 4 black cells), and 7×7 (with 3×3 = 9 black cells). "
            "The 4th diagram is a 9×9 grid (81 cells) with 4×4 = 16 black cells, leaving 81 - 16 = 65 white cells.",
        ))

    practices = [
        # Practice .1: Same diagram, ask for the 5th diagram (11x11 = 121 total - 5^2=25 black = 96 white cells) (Answer: D)
        (
            orig_specs,
            orig_white_step,
            5,
            ["75", "84", "90", "96", "105"],
            3,
            "The three diagrams show the first 3 steps of a pattern of black and white cells (with 8, 21, and 40 white cells). "
            "If the pattern continues, how many white cells will the <b>5th diagram</b> have?",
            "In step k, the grid is (2k + 1) × (2k + 1) and has k × k black cells. For the 5th diagram (k = 5), "
            "the grid is 11 × 11 = 121 cells with 5 × 5 = 25 black cells, leaving 121 - 25 = 96 white cells.",
        ),
        # Practice .2: Diagonal black cells on k+2 grid (k=1: 3x3 with 3 black on diagonal -> 6 white; k=2: 4x4 with 4 black -> 12 white; k=3: 5x5 with 5 black -> 20 white; next k=4: 6x6 - 6 = 30 white) (Answer: B)
        (
            [
                (3, lambda r, c, N: r == c, "6 white cells"),
                (4, lambda r, c, N: r == c, "12 white cells"),
                (5, lambda r, c, N: r == c, "20 white cells"),
            ],
            lambda k: (k + 2) ** 2 - (k + 2),
            4,
            ["24", "30", "32", "36", "42"],
            1,
            "The three diagrams show a pattern where the main diagonal is shaded grey (with 6, 12, and 20 white cells). "
            "How many white cells will the <b>next</b> diagram in the pattern have?",
            "The grids are 3×3 (9 - 3 = 6 white), 4×4 (16 - 4 = 12 white), and 5×5 (25 - 5 = 20 white). "
            "The next grid is 6×6 = 36 cells with 6 diagonal grey cells, giving 36 - 6 = 30 white cells.",
        ),
        # Practice .3: Border white, inner (k)x(k) black! Wait: let's do checkerboard corners or plus-cross!
        # Let's do: step k has (2k+1)x(2k+1) grid where the center row and center column are grey (a cross of 4k+1 grey cells),
        # leaving 4 * k^2 white cells!
        # k=1 (3x3): 4 white cells; k=2 (5x5): 16 white cells; k=3 (7x7): 36 white cells; k=4 (9x9): 64 white cells (Answer: E)
        (
            [
                (3, lambda r, c, N: r == N // 2 or c == N // 2, "4 white cells"),
                (5, lambda r, c, N: r == N // 2 or c == N // 2, "16 white cells"),
                (7, lambda r, c, N: r == N // 2 or c == N // 2, "36 white cells"),
            ],
            lambda k: 4 * (k ** 2),
            4,
            ["48", "52", "56", "60", "64"],
            4,
            "In the pattern shown, the middle row and middle column of each odd-sized square grid are shaded grey "
            "(leaving 4, 16, and 36 white cells in the first three diagrams). How many white cells will the <b>next</b> diagram have?",
            "In each diagram, the grey cross splits the white cells into 4 identical k × k corners: "
            "4 × 1² = 4, 4 × 2² = 16, and 4 × 3² = 36. In the 4th diagram (a 9 × 9 grid), there are 4 × 4² = 64 white cells.",
        ),
        # Practice .4: Original pattern, how many MORE white cells does the 4th diagram have than the 3rd diagram? 65 - 40 = 25 (Answer: A)
        (
            orig_specs,
            lambda k: orig_white_step(k) - orig_white_step(k - 1),
            4,
            ["25", "23", "21", "19", "16"],
            0,
            "Look at the three diagrams of black and white cells (with 8, 21, and 40 white cells). "
            "How many <b>more</b> white cells will the 4th diagram have than the 3rd diagram?",
            "The number of white cells increases by 21 - 8 = 13 from the 1st to the 2nd diagram, and by 40 - 21 = 19 "
            "from the 2nd to the 3rd diagram (6 more each step). The next increase is 19 + 6 = 25 more white cells "
            "(since the 4th diagram has 65 white cells and 65 - 40 = 25).",
        ),
    ]

    for idx, (specs, s_fn, s_idx, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_bw_pattern(s_fn, s_idx, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_bw_grid_pattern(specs),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_21

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
