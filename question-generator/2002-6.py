# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #6 - Question Generator."""
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
QUESTION_ID = (2002, 6)


def fig_square_rect(s1_val, am_val, label_s1, label_am=None, label_mb=None, size=92):
    w = size + 52
    h = size + 30
    cut_ratio = max(0.22, min(0.78, am_val / s1_val))

    def draw(c, x, y):
        ox = x + 32
        oy = y + 14
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
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(ox - 9, oy - 10, "A")
        c.drawString(ox + sw + 3, oy - 10, "B")
        c.drawString(ox + sw + 3, oy + sh + 3, "C")
        c.drawString(ox - 9, oy + sh + 3, "D")
        c.drawCentredString(mx, oy - 10, "M")
        c.drawCentredString(mx, oy + sh + 3, "T")

        # Dimension labels
        c.setFont("Helvetica", 8.5)
        c.drawRightString(ox - 4, oy + sh / 2 - 3, label_s1)
        if label_am:
            c.drawCentredString(ox + (cut_ratio * sw) / 2, oy + sh + 4, label_am)
        if label_mb:
            c.drawCentredString(mx + ((1 - cut_ratio) * sw) / 2, oy + sh + 4, label_mb)

        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_square_rect_diff(s1, am, opts, correct_idx, mode="sq_minus_amtd"):
    mb = s1 - am
    perim_sq = 4 * s1
    perim_amtd = 2 * (s1 + am)
    perim_mbct = 2 * (s1 + mb)
    if mode in ("sq_minus_amtd", "given_mb"):
        expected = perim_sq - perim_amtd
        assert expected == 2 * mb
    elif mode == "mbct_minus_amtd":
        expected = perim_mbct - perim_amtd
        assert expected == 2 * (mb - am)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    matches = [i for i, v in enumerate(opts) if v == expected]
    assert matches == [correct_idx], f"Expected {[correct_idx]} for diff={expected}, got {matches} in opts={opts}"


def _make_distractors(rng, ans, candidates):
    seen = {ans}
    dist = []
    for v in candidates:
        if v > 0 and v not in seen:
            seen.add(v)
            dist.append(v)
    delta = 2
    while len(dist) < 4:
        for cand in (ans + delta, ans - delta):
            if cand > 0 and cand not in seen:
                seen.add(cand)
                dist.append(cand)
                if len(dist) == 4:
                    break
        delta += 2
    opts = [ans] + dist[:4]
    rng.shuffle(opts)
    return opts, opts.index(ans)


def _generate_dynamic_sq_rect_problem(rng, mode="sq_minus_amtd"):
    s1 = rng.randint(11, 28)
    am = rng.randint(2, max(3, (s1 - 3) // 2))
    mb = s1 - am

    if mode == "sq_minus_amtd":
        ans = 2 * mb
        cands = [mb, 2 * am, s1, 2 * s1 - am, ans + 2, ans - 2]
        opts, ans_idx = _make_distractors(rng, ans, cands)
        fig = fig_square_rect(s1, am, f"{s1} cm", label_am=f"{am} cm")
        text = (
            f"The side of square <i>ABCD</i> is {s1} cm. The side <i>AM</i> of rectangle <i>AMTD</i> is {am} cm. "
            "How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?"
        )
        expl = (
            f"Perimeter of square ABCD = 4 × {s1} = {4 * s1} cm. "
            f"Perimeter of rectangle AMTD = 2 × ({s1} + {am}) = {2 * (s1 + am)} cm. "
            f"Difference = {4 * s1} - {2 * (s1 + am)} = {ans} cm (or simply 2 × MB = 2 × {mb} = {ans} cm)."
        )
    elif mode == "given_mb":
        ans = 2 * mb
        cands = [mb, 2 * am, am, s1 - mb, ans + 4, ans - 4]
        opts, ans_idx = _make_distractors(rng, ans, cands)
        fig = fig_square_rect(s1, am, f"{s1} cm", label_mb=f"{mb} cm")
        text = (
            f"The side of square <i>ABCD</i> is {s1} cm. A line segment <i>MT</i> divides the square into two rectangles, "
            f"and the top/bottom width <i>TC</i> = <i>MB</i> is {mb} cm. How much greater is the perimeter of square "
            "<i>ABCD</i> than the perimeter of the shaded rectangle <i>AMTD</i>?"
        )
        expl = (
            f"Since AB = {s1} cm and MB = {mb} cm, we have AM = {s1} - {mb} = {am} cm. "
            f"Perimeter of square ABCD = 4 × {s1} = {4 * s1} cm, and perimeter of rectangle AMTD = 2 × ({s1} + {am}) = {2 * (s1 + am)} cm. "
            f"The difference is {4 * s1} - {2 * (s1 + am)} = {ans} cm (which is simply 2 × MB = 2 × {mb} = {ans} cm)."
        )
    else:
        # mbct_minus_amtd
        ans = 2 * (mb - am)
        cands = [mb - am, 2 * mb, 2 * am, mb, ans + 2, ans - 2]
        opts, ans_idx = _make_distractors(rng, ans, cands)
        fig = fig_square_rect(s1, am, f"{s1} cm", label_am=f"{am} cm")
        text = (
            f"The side of square <i>ABCD</i> is {s1} cm. Line segment <i>MT</i> divides the square into the shaded "
            f"rectangle <i>AMTD</i> (with <i>AM</i> = {am} cm) and the white rectangle <i>MBCT</i>. "
            "How much greater is the perimeter of rectangle <i>MBCT</i> than the perimeter of rectangle <i>AMTD</i>?"
        )
        expl = (
            f"Since AB = {s1} cm and AM = {am} cm, the width of rectangle MBCT is MB = {s1} - {am} = {mb} cm. "
            f"Perimeter of MBCT = 2 × ({s1} + {mb}) = {2 * (s1 + mb)} cm, and perimeter of AMTD = 2 × ({s1} + {am}) = {2 * (s1 + am)} cm. "
            f"The difference is {2 * (s1 + mb)} - {2 * (s1 + am)} = {ans} cm."
        )

    check_square_rect_diff(s1, am, opts, ans_idx, mode=mode)
    return fig, opts, ans_idx, text, expl


def q_2002_6(d, key, set_num=2, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Square and rectangle perimeters", "Based on 2002, Problem 6")

    opts0 = [14, 10, 7, 6, 4]
    check_square_rect_diff(10, 3, opts0, 0, mode="sq_minus_amtd")
    if include_orig:
        fig0 = fig_square_rect(10, 3, "10 cm", label_am="3 cm")
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

    rng = random.Random(seed)
    modes = ["sq_minus_amtd", "given_mb", "mbct_minus_amtd", "sq_minus_amtd", "given_mb"]
    for idx in range(1, num_practice + 1):
        mode = modes[(idx - 1) % len(modes)]
        fig, opts, ans_idx, text, expl = _generate_dynamic_sq_rect_problem(rng, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig,
            "right",
            [f"{v} cm" for v in opts],
            choice_cols=5,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_6

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
