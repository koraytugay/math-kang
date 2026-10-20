# Model: argon
"""Math Kangaroo 2002, Problem #6 - Question Generator."""
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
QUESTION_ID = (2002, 6)


def fig_square_rect(s1_val, s2_val, label_s1, label_s2=None, label_mb=None, size=95):
    w = size + 45
    h = size + 25
    cut_ratio = s2_val / s1_val

    def draw(c, x, y):
        ox = x + 25
        oy = y + 12
        sw = size
        sh = size
        mx = ox + cut_ratio * sw

        # Light gray fill for AMTD rectangle
        c.setFillColor(colors.Color(0.88, 0.88, 0.88))
        c.rect(ox, oy, cut_ratio * sw, sh, stroke=0, fill=1)

        # Draw square border and dividing line MT
        c.setLineWidth(1.4)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, sw, sh, stroke=1, fill=0)
        c.setLineWidth(1.2)
        c.line(mx, oy, mx, oy + sh)

        # Labels for vertices A, B, C, D, M, T
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(ox - 10, oy - 9, "A")
        c.drawString(ox + sw + 3, oy - 9, "B")
        c.drawString(ox + sw + 3, oy + sh + 3, "C")
        c.drawString(ox - 10, oy + sh + 3, "D")
        c.drawString(mx - 4, oy - 10, "M")
        c.drawString(mx - 3, oy + sh + 3, "T")

        # Dimension labels
        c.setFont("Helvetica", 9)
        c.drawCentredString(ox - 16, oy + sh / 2 - 3, label_s1)
        if label_s2:
            c.drawCentredString(ox + (cut_ratio * sw) / 2, oy + sh + 4, label_s2)
        if label_mb:
            c.drawCentredString(mx + ((1 - cut_ratio) * sw) / 2, oy - 10, label_mb)

    return w, h, draw


def check_square_rect_diff(s1, s2, opts, correct_idx, twist_mb=None):
    if twist_mb is not None:
        am = s1 - twist_mb
        diff = 2 * (s1 - am)
    else:
        diff = 2 * (s1 - s2)
    assert opts[correct_idx] == diff, f"Expected {diff}, got {opts[correct_idx]}"
    matches = [i for i, v in enumerate(opts) if v == diff]
    assert matches == [correct_idx], f"Multiple matches: {matches}"


def q_2002_6(d, key, set_num=2, include_orig=True):
    d.heading(f"Set {set_num} - Square and rectangle perimeters", "Based on 2002, Problem 6")

    # Original 2002 #6: s1=10, s2=3. Perimeter diff = 4(10) - 2(10+3) = 40 - 26 = 14 cm.
    opts0 = [14, 10, 7, 6, 4]
    check_square_rect_diff(10, 3, opts0, 0)
    if include_orig:
        fig0 = fig_square_rect(10, 3, "10 cm", label_s2="3 cm")
        d.problem(
            "Original 2002 #6.",
            "The side of the square <i>ABCD</i> is 10 cm. The side <i>AM</i> of the rectangle <i>AMTD</i> is 3 cm. "
            "How much greater is the perimeter of the square than the perimeter of the rectangle <i>AMTD</i>?",
            fig0,
            "right",
            [f"{v} cm" for v in opts0],
            choice_cols=5,
        )
        key.append((
            "2002 #6",
            "A",
            "Perimeter of square ABCD = 4 × 10 = 40 cm. Perimeter of rectangle AMTD = 2 × (10 + 3) = 26 cm. "
            "Difference = 40 - 26 = 14 cm (or simply 2 × MB = 2 × 7 = 14 cm).",
        ))

    # Practice 2.1: s1=12, s2=4. Diff = 2*(12-4) = 16 cm. Answer: B (16 cm)
    opts1 = [10, 16, 18, 20, 24]
    check_square_rect_diff(12, 4, opts1, 1)
    fig1 = fig_square_rect(12, 4, "12 cm", label_s2="4 cm")
    d.problem(
        f"Practice {set_num}.1",
        "The side of square <i>ABCD</i> is 12 cm. The side <i>AM</i> of rectangle <i>AMTD</i> is 4 cm. "
        "How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig1,
        "right",
        [f"{v} cm" for v in opts1],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "B",
        "Perimeter of square ABCD = 4 × 12 = 48 cm. Perimeter of rectangle AMTD = 2 × (12 + 4) = 32 cm. "
        "Difference = 48 - 32 = 16 cm.",
    ))

    # Practice 2.2: s1=15, s2=6. Diff = 2*(15-6) = 18 cm. Answer: C (18 cm)
    opts2 = [14, 16, 18, 22, 24]
    check_square_rect_diff(15, 6, opts2, 2)
    fig2 = fig_square_rect(15, 6, "15 cm", label_s2="6 cm")
    d.problem(
        f"Practice {set_num}.2",
        "The side of square <i>ABCD</i> is 15 cm. The side <i>AM</i> of rectangle <i>AMTD</i> is 6 cm. "
        "How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig2,
        "right",
        [f"{v} cm" for v in opts2],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "C",
        "Perimeter of square ABCD = 4 × 15 = 60 cm. Perimeter of rectangle AMTD = 2 × (15 + 6) = 42 cm. "
        "Difference = 60 - 42 = 18 cm.",
    ))

    # Practice 2.3: twist - gives MB = 7 cm, s1 = 18 cm. Diff = 2 * MB = 14 cm. Answer: B (14 cm)
    opts3 = [12, 14, 16, 18, 22]
    check_square_rect_diff(18, None, opts3, 1, twist_mb=7)
    fig3 = fig_square_rect(18, 11, "18 cm", label_mb="MB = 7 cm")
    d.problem(
        f"Practice {set_num}.3",
        "The side of square <i>ABCD</i> is 18 cm. A line segment <i>MT</i> divides the square into two rectangles. "
        "The length of segment <i>MB</i> is 7 cm. How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig3,
        "right",
        [f"{v} cm" for v in opts3],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "B",
        "Since AB = 18 cm and MB = 7 cm, AM = 18 - 7 = 11 cm. "
        "Perimeter of square = 4 × 18 = 72 cm. Perimeter of rectangle AMTD = 2 × (18 + 11) = 58 cm. "
        "Difference = 72 - 58 = 14 cm (which is simply 2 × MB = 2 × 7 = 14 cm).",
    ))

GENERATE = q_2002_6

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
