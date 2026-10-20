# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #14 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2003, 14)


def shoelace(pts):
    return abs(
        sum(
            pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
            for i in range(len(pts))
        )
    ) / 2


def letter_area(polys):
    total = sum(shoelace(p) for p in polys)
    assert abs(total - round(total)) < 1e-9, f"Non-integer letter area: {total}"
    return int(round(total))


def check_letter_area(polys, choices, ans_idx):
    area = letter_area(polys)
    matches = [i for i, ch in enumerate(choices) if int(ch) == area]
    assert matches == [ans_idx], f"Letter area={area}, choices={choices}, ans_idx={ans_idx}"
    return area


def fig_letter(gw, gh, polys, s=14):
    pad = 2
    w = gw * s + 2 * pad
    h = gh * s + 2 * pad

    def draw(c, x, y):
        ox = x + pad
        oy = y + pad
        # 1. Shaded polygon fills first so grid lines remain visible on top
        c.setFillColor(colors.Color(0.76, 0.76, 0.76))
        for pts in polys:
            pa = c.beginPath()
            pa.moveTo(ox + pts[0][0] * s, oy + pts[0][1] * s)
            for q in pts[1:]:
                pa.lineTo(ox + q[0] * s, oy + q[1] * s)
            pa.close()
            c.drawPath(pa, stroke=0, fill=1)

        # 2. Grid lines
        c.setStrokeColor(colors.Color(0.35, 0.35, 0.35))
        c.setLineWidth(0.55)
        for i in range(gw + 1):
            c.line(ox + i * s, oy, ox + i * s, oy + gh * s)
        for j in range(gh + 1):
            c.line(ox, oy + j * s, ox + gw * s, oy + j * s)

        # 3. Bold polygon outlines
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.9)
        for pts in polys:
            pa = c.beginPath()
            pa.moveTo(ox + pts[0][0] * s, oy + pts[0][1] * s)
            for q in pts[1:]:
                pa.lineTo(ox + q[0] * s, oy + q[1] * s)
            pa.close()
            c.drawPath(pa, stroke=1, fill=0)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def _make_area_choices(rng, area):
    offset = rng.randint(0, 4)
    step = rng.choice([1, 2])
    vals = [area + (i - offset) * step for i in range(5)]
    if vals[0] < 4:
        vals = [area + i * step for i in range(5)]
    ans_idx = vals.index(area)
    return vals, ans_idx


def _generate_dynamic_letter_problem(rng, family_idx=0):
    """Procedurally generate a block letter on a 1 cm grid with randomized dimensions."""
    fam = family_idx % 4

    if fam == 0:
        # Family 0: Letter Z with top/bottom horizontal bars and slanted diagonal parallelogram
        letter_name = "Z"
        W_bar = rng.choice([4, 5, 6])
        H_mid = rng.choice([4, 5, 6])
        diag_w = rng.choice([1, 2]) if W_bar >= 5 else 1
        H_tot = H_mid + 2
        gw = W_bar + 2
        gh = H_tot
        polys = [
            [(1, H_tot - 1), (1 + W_bar, H_tot - 1), (1 + W_bar, H_tot), (1, H_tot)],
            [(1, 0), (1 + W_bar, 0), (1 + W_bar, 1), (1, 1)],
            [(1 + W_bar - diag_w, H_tot - 1), (1 + W_bar, H_tot - 1), (1 + diag_w, 1), (1, 1)],
        ]
        area = letter_area(polys)
        diag_area = diag_w * H_mid
        assert area == 2 * W_bar + diag_area
        expl = (
            f"The top bar has area {W_bar} cm² and the bottom bar has area {W_bar} cm². "
            f"The slanted middle part is a parallelogram with base {diag_w} cm and height {H_mid} cm, "
            f"so its area is {diag_w} × {H_mid} = {diag_area} cm². "
            f"In total, the area is {W_bar} + {W_bar} + {diag_area} = {area} cm²."
        )

    elif fam == 1:
        # Family 1: Letter N with two vertical bars and a slanted diagonal parallelogram
        letter_name = "N"
        while True:
            H = rng.choice([4, 5, 6])
            bar_w = rng.choice([1, 2])
            diag_w = rng.choice([1, 2])
            span = rng.choice([2, 3])
            if (H, bar_w, diag_w, span) != (6, 1, 1, 3):
                break
        xL0, xL1 = 1, 1 + bar_w
        xR0, xR1 = xL1 + span, xL1 + span + bar_w
        gw = xR1 + 1
        gh = H
        polys = [
            [(xL0, 0), (xL1, 0), (xL1, H), (xL0, H)],
            [(xR0, 0), (xR1, 0), (xR1, H), (xR0, H)],
            [(xL1, H), (xL1 + diag_w, H), (xR0, 0), (xR0 - diag_w, 0)],
        ]
        area = letter_area(polys)
        bar_area = bar_w * H
        diag_area = diag_w * H
        assert area == 2 * bar_area + diag_area
        expl = (
            f"Each vertical side bar is {bar_w} cm wide and {H} cm tall (area {bar_area} cm² each). "
            f"The slanted bar is a parallelogram with horizontal base {diag_w} cm and height {H} cm "
            f"(area {diag_w} × {H} = {diag_area} cm²). Total area = {bar_area} + {bar_area} + {diag_area} = {area} cm²."
        )

    elif fam == 2:
        # Family 2: Letter M with two vertical side bars and a V-shaped middle
        letter_name = "M"
        H = rng.choice([4, 5, 6])
        bar_w = 1
        half_span = rng.choice([2, 3])
        v_thick = rng.choice([1, 2]) if H >= 5 else 2
        # Ensure v_thick is even or half_span*v_thick is integer: parallelogram of vertical thickness v_thick and horizontal width half_span has area half_span * v_thick!
        y_drop = rng.randint(2, H - v_thick)
        xL0, xL1 = 1, 1 + bar_w
        xM = xL1 + half_span
        xR0, xR1 = xM + half_span, xM + half_span + bar_w
        gw = xR1 + 1
        gh = H
        polys = [
            [(xL0, 0), (xL1, 0), (xL1, H), (xL0, H)],
            [(xR0, 0), (xR1, 0), (xR1, H), (xR0, H)],
            [
                (xL1, H),
                (xM, H - y_drop),
                (xR0, H),
                (xR0, H - v_thick),
                (xM, H - y_drop - v_thick),
                (xL1, H - v_thick),
            ],
        ]
        area = letter_area(polys)
        v_part_area = half_span * v_thick
        assert area == 2 * H + 2 * v_part_area
        expl = (
            f"The two vertical side bars each have area 1 × {H} = {H} cm² (together {2 * H} cm²). "
            f"The middle V consists of two slanted parallelograms, each {half_span} cm wide horizontally "
            f"with vertical thickness {v_thick} cm (area {half_span} × {v_thick} = {v_part_area} cm² each). "
            f"Total area = {2 * H} + {v_part_area} + {v_part_area} = {area} cm²."
        )

    else:
        # Family 3: Letter V formed by two slanted legs meeting at the bottom
        letter_name = "V"
        H = rng.choice([4, 5, 6])
        leg_w = rng.choice([1, 2])
        s_span = rng.choice([1, 2])
        # Make V out of two meeting parallelograms or a notched trapezoid with integer shoelace area:
        # Left leg: top [(1, H), (1 + leg_w, H)], bottom [(1 + s_span, 0), (1 + s_span + leg_w, 0)]
        # Right leg: top [(1 + 2*s_span + leg_w, H), (1 + 2*s_span + 2*leg_w, H)], bottom [(1 + s_span + leg_w, 0), (1 + s_span + 2*leg_w, 0)]
        x0 = 1
        bL0 = x0 + s_span
        bM = bL0 + leg_w
        bR1 = bM + leg_w
        tR0 = bM + s_span
        tR1 = tR0 + leg_w
        gw = tR1 + 1
        gh = H
        polys = [
            [(x0, H), (x0 + leg_w, H), (bM, 0), (bL0, 0)],
            [(tR0, H), (tR1, H), (bR1, 0), (bM, 0)],
        ]
        area = letter_area(polys)
        leg_area = leg_w * H
        assert area == 2 * leg_area
        expl = (
            f"The letter V is made of two slanted parallelogram legs, each with horizontal base {leg_w} cm "
            f"and height {H} cm (area {leg_w} × {H} = {leg_area} cm² each). "
            f"Together, the total area is {leg_area} + {leg_area} = {area} cm²."
        )

    opts, ans_idx = _make_area_choices(rng, area)
    check_letter_area(polys, opts, ans_idx)
    s_scale = 12 if max(gw, gh) >= 9 else 14
    return letter_name, gw, gh, polys, s_scale, opts, ans_idx, expl


def q_2003_14(d, key, set_num=6, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Area of a letter on squared paper", "Based on 2003, Problem 14")
    q = "If the side of each little square is 1 cm, what is the area of the letter %s (in square cm)?"
    if include_orig:
        N = [[(1, 0), (2, 0), (2, 6), (1, 6)], [(5, 0), (6, 0), (6, 6), (5, 6)], [(2, 6), (3, 6), (5, 0), (4, 0)]]
        opts0 = [14, 15, 16, 17, 18]
        check_letter_area(N, opts0, 4)
        d.problem("Original 2003 #14.", q % "N", fig_letter(7, 6, N, s=15), "right", opts0)
        key.append((
            "2003 #14",
            "E",
            "Each side bar is 6. The slanted part is a parallelogram 1 wide and 6 tall = 6 (cut-off triangles fit together). 6+6+6 = 18.",
        ))

    rng = random.Random(seed)
    fams = [0, 1, 2, 3]
    rng.shuffle(fams)
    for idx in range(1, num_practice + 1):
        fam = fams[(idx - 1) % len(fams)]
        lname, gw, gh, polys, s_sc, opts, ans_idx, expl = _generate_dynamic_letter_problem(rng, family_idx=fam)
        check_letter_area(polys, opts, ans_idx)
        d.problem(f"Practice {set_num}.{idx}", q % lname, fig_letter(gw, gh, polys, s=s_sc), "right", opts)
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_14

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
