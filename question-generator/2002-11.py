# Model: argon
"""Math Kangaroo 2002, Problem #11 - Question Generator."""
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
QUESTION_ID = (2002, 11)


def fig_cracked_clock(cracks, R=33):
    """Draw a clock face (1..12) with cracks specified as lists of (r_frac, clock_pos) points."""
    pad = 4
    w = 2 * R + 2 * pad
    h = 2 * R + 2 * pad

    def draw(c, x, y):
        cx = x + pad + R
        cy = y + pad + R

        def pt(r_frac, clock_pos):
            ang = math.radians(90.0 - clock_pos * 30.0)
            return cx + r_frac * R * math.cos(ang), cy + r_frac * R * math.sin(ang)

        # Outer clock circle
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.2)
        c.circle(cx, cy, R, stroke=1, fill=1)

        # Clock numbers 1..12
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 7.8)
        r_num = 0.78
        for hr in range(1, 13):
            px, py = pt(r_num, hr)
            c.drawCentredString(px, py - 2.8, str(hr))

        # Crack lines
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.95)

        def bezier_ctrl(crack):
            (r1, p1), (rm, pm), (r2, p2) = crack
            x1, y1 = pt(r1, p1)
            xm, ym = pt(rm, pm)
            x2, y2 = pt(r2, p2)
            ix1, iy1 = pt(0.46 if r1 >= 0.95 else r1, p1)
            ix2, iy2 = pt(0.46 if r2 >= 0.95 else r2, p2)
            cx1 = 0.62 * ix1 + 0.38 * xm
            cy1 = 0.62 * iy1 + 0.38 * ym
            cx2 = 0.62 * ix2 + 0.38 * xm
            cy2 = 0.62 * iy2 + 0.38 * ym
            return (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)

        def eval_bezier(bpts, t):
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = bpts
            u = 1.0 - t
            bx = (u ** 3) * x0 + 3 * (u ** 2) * t * x1 + 3 * u * (t ** 2) * x2 + (t ** 3) * x3
            by = (u ** 3) * y0 + 3 * (u ** 2) * t * y1 + 3 * u * (t ** 2) * y2 + (t ** 3) * y3
            return bx, by

        drawn_beziers = []
        for crack in cracks:
            if isinstance(crack[0], str) and crack[0] == "branch":
                _, parent_idx, t_val, (r2, p2) = crack
                bx, by = eval_bezier(drawn_beziers[parent_idx], t_val)
                x2, y2 = pt(r2, p2)
                c.line(bx, by, x2, y2)
            elif len(crack) == 2:
                (r1, p1), (r2, p2) = crack
                c.line(*pt(r1, p1), *pt(r2, p2))
                drawn_beziers.append(None)
            elif len(crack) == 3:
                bpts = bezier_ctrl(crack)
                drawn_beziers.append(bpts)
                (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = bpts
                path = c.beginPath()
                path.moveTo(x1, y1)
                path.curveTo(cx1, cy1, cx2, cy2, x2, y2)
                c.drawPath(path, stroke=1, fill=0)
            else:
                pts = [pt(rf, cp) for rf, cp in crack]
                path = c.beginPath()
                path.moveTo(*pts[0])
                for qx, qy in pts[1:]:
                    path.lineTo(qx, qy)
                c.drawPath(path, stroke=1, fill=0)
                drawn_beziers.append(None)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_cracked_clock(options_parts, expected_sums, answer_idx):
    """Verify each option partitions 1..12 and only answer_idx has piece sums matching expected_sums."""
    full_clock = list(range(1, 13))
    target_sorted = sorted(expected_sums)
    assert sum(target_sorted) == 78, f"Target sums {target_sorted} do not add to 78"
    matching = []
    for idx, parts in enumerate(options_parts):
        flat = sorted(x for p in parts for x in p)
        assert flat == full_clock, f"Option {idx} does not partition 1..12: {parts}"
        sums = sorted(sum(p) for p in parts)
        if sums == target_sorted:
            matching.append(idx)
    assert matching == [answer_idx], f"Expected unique match at {answer_idx} for sums {target_sorted}, got {matching}"


def q_2002_11(d, key, set_num=2, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #11 - Cracked Clock Face",
        "Partitioning the clock face (sum 1 + 2 + ... + 12 = 78) into pieces with given sum properties",
    )

    # Original 2002 #11: 4 pieces with consecutive sums (18, 19, 20, 21) -> Answer: C
    if include_orig:
        parts0 = [
            [[9, 10], [7, 8], [11, 5, 6], [12, 1, 2, 3, 4]],        # A: sums 19, 15, 22, 22
            [[11, 12], [7, 8, 9], [6], [10, 1, 2, 3, 4, 5]],        # B: sums 23, 24, 6, 25
            [[12, 1, 2, 3], [9, 10], [11, 4, 5], [6, 7, 8]],        # C: sums 18, 19, 20, 21
            [[10, 11], [9, 12, 1], [7, 8, 2, 3], [4, 5, 6]],        # D: sums 21, 22, 20, 15
            [[8, 9, 10, 11], [12, 1, 2, 3], [4, 5, 6, 7]],          # E: only 3 pieces (38, 18, 22)
        ]
        cracks0 = [
            # A: two cracks from top-left to bottom, short crack on left between 8 and 9
            [[(1.0, 10.55), (0.35, 8.5), (1.0, 6.45)], [(1.0, 11.45), (0.15, 8.0), (1.0, 4.55)], ("branch", 0, 0.52, (1.0, 8.5))],
            # B: top loop around 11,12; diagonal from 9.5 to 5.5; branch to 6.5
            [[(1.0, 10.5), (0.28, 11.5), (1.0, 0.5)], [(1.0, 9.5), (0.35, 7.2), (1.0, 5.5)], ("branch", 1, 0.62, (1.0, 6.5))],
            # C: 11.5 to 3.5; 10.5 to 5.5; branch from 8.5 to middle crack
            [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
            # D: loop around 10,11; diagonal 1.5 to 8.5; curve 3.5 to 6.5
            [[(1.0, 11.5), (0.28, 10.5), (1.0, 9.5)], [(1.0, 1.5), (0.05, 5.0), (1.0, 8.5)], [(1.0, 3.5), (0.32, 5.0), (1.0, 6.5)]],
            # E: 11.5 to 7.5; branch to 3.5
            [[(1.0, 11.5), (0.2, 9.5), (1.0, 7.5)], ("branch", 0, 0.5, (1.0, 3.5))],
        ]
        check_cracked_clock(parts0, [18, 19, 20, 21], 2)
        fig0 = option_row([fig_cracked_clock(cr) for cr in cracks0], gap=12)
        d.problem(
            "2002 #11",
            "The face of a clock is cracked into 4 pieces. The sums of the numbers within the parts are consecutive "
            "numbers. Provided there is only one possible way to crack it, the face would look like:",
            fig0,
            "below",
        )
        key.append((
            "2002 #11",
            "C",
            "The sum of all numbers on a clock face is 1 + 2 + ... + 12 = 78. Four consecutive numbers that add up "
            "to 78 must be 18, 19, 20, and 21 (since 18 + 19 + 20 + 21 = 78). In clock C, the four pieces contain "
            "{12, 1, 2, 3} = 18, {9, 10} = 19, {11, 4, 5} = 20, and {6, 7, 8} = 21.",
        ))

    practices = [
        # Practice .1: 3 pieces with equal sums (26, 26, 26) -> Answer: A
        (
            [
                [[11, 12, 1, 2], [9, 10, 3, 4], [5, 6, 7, 8]],          # A: 26, 26, 26
                [[12, 1, 2, 3], [10, 11, 4, 5], [6, 7, 8, 9]],          # B: 18, 30, 30
                [[10, 11, 12, 1], [8, 9, 2, 3], [4, 5, 6, 7]],          # C: 34, 22, 22
                [[11, 12, 1], [9, 10, 2, 3], [4, 5, 6, 7, 8]],          # D: 24, 24, 30
                [[11, 12, 1, 2], [10, 3, 4], [5, 6, 7, 8, 9]],          # E: 26, 17, 35
            ],
            [
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 4.5)]],
                [[(1.0, 11.5), (0.25, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.25, 7.5), (1.0, 5.5)]],
                [[(1.0, 9.5), (0.25, 11.5), (1.0, 1.5)], [(1.0, 7.5), (0.25, 5.5), (1.0, 3.5)]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 1.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 3.5)]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 9.5), (0.25, 7.0), (1.0, 4.5)]],
            ],
            [26, 26, 26],
            0,
            "The face of a clock is cracked into 3 pieces so that the sums of the numbers on all 3 pieces are equal. "
            "Which clock face shows how it was cracked?",
            "Since the numbers 1 through 12 add up to 78, each of the 3 equal pieces must have a sum of 78 ÷ 3 = 26. "
            "In clock A, the top piece has 11 + 12 + 1 + 2 = 26, the middle piece has 9 + 10 + 3 + 4 = 26, "
            "and the bottom piece has 5 + 6 + 7 + 8 = 26.",
        ),
        # Practice .2: 3 pieces with consecutive sums (25, 26, 27) -> Answer: B
        (
            [
                [[11, 12, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10]],          # A: 26, 18, 34
                [[11, 12, 1, 2], [3, 4, 5, 6, 7], [8, 9, 10]],          # B: 26, 25, 27
                [[12, 1, 2, 3], [4, 5, 6, 7, 8], [9, 10, 11]],          # C: 18, 30, 30
                [[10, 11, 12], [1, 2, 3, 4, 5, 6], [7, 8, 9]],          # D: 33, 21, 24
                [[11, 12, 1], [2, 3, 4, 5, 6, 7], [8, 9, 10]],          # E: 24, 27, 27
            ],
            [
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
                [[(1.0, 9.5), (0.0, 0.0)], [(1.0, 0.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 1.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
            ],
            [25, 26, 27],
            1,
            "The face of a clock is cracked into 3 pieces meeting at the center. The sums of the numbers within the 3 parts "
            "are consecutive numbers. Which clock face shows how it was cracked?",
            "Three consecutive numbers that add up to 78 are 25, 26, and 27 (25 + 26 + 27 = 78). "
            "In clock B, the three pieces are {3, 4, 5, 6, 7} = 25, {11, 12, 1, 2} = 26, and {8, 9, 10} = 27.",
        ),
        # Practice .3: 2 pieces with equal sums (39, 39) -> Answer: D
        (
            [
                [[12, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11]],            # A: 27, 51
                [[11, 12, 1, 2, 3, 4], [5, 6, 7, 8, 9, 10]],            # B: 33, 45
                [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],            # C: 21, 57
                [[10, 11, 12, 1, 2, 3], [4, 5, 6, 7, 8, 9]],            # D: 39, 39
                [[9, 10, 11, 12, 1, 2], [3, 4, 5, 6, 7, 8]],            # E: 45, 33
            ],
            [
                [[(1.0, 11.5), (0.1, 2.5), (1.0, 5.5)]],
                [[(1.0, 10.5), (0.1, 1.5), (1.0, 4.5)]],
                [[(1.0, 0.5), (0.1, 3.5), (1.0, 6.5)]],
                [[(1.0, 9.5), (0.1, 12.5), (1.0, 3.5)]],
                [[(1.0, 8.5), (0.1, 11.5), (1.0, 2.5)]],
            ],
            [39, 39],
            3,
            "A clock face is cracked into 2 pieces by a single crack so that the sum of the numbers on one piece "
            "equals the sum of the numbers on the other piece. Which clock face shows this crack?",
            "Half of the total clock sum is 78 ÷ 2 = 39. In clock D, the crack goes between 9 and 10 on the left "
            "and between 3 and 4 on the right, giving {10, 11, 12, 1, 2, 3} = 39 and {4, 5, 6, 7, 8, 9} = 39.",
        ),
        # Practice .4: 4 pieces where two pieces sum to 18 and two pieces sum to 21 -> Answer: E
        (
            [
                [[12, 1, 2, 3], [11, 4, 5], [9, 10], [6, 7, 8]],        # A: 18, 20, 19, 21
                [[12, 1, 2], [11, 3, 4], [9, 10, 5], [6, 7, 8]],        # B: 15, 18, 24, 21
                [[11, 12, 1, 2], [10, 3, 4], [8, 9], [5, 6, 7]],        # C: 26, 17, 17, 18
                [[12, 1, 2, 3], [10, 11], [7, 8, 9], [4, 5, 6]],        # D: 18, 21, 24, 15
                [[12, 1, 2, 3], [10, 11], [8, 9, 4], [5, 6, 7]],        # E: 18, 21, 21, 18
            ],
            [
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
                [[(1.0, 11.5), (0.22, 1.0), (1.0, 2.5)], [(1.0, 10.5), (0.28, 7.5), (1.0, 4.5)], ("branch", 1, 0.50, (1.0, 8.5))],
                [[(1.0, 10.5), (0.22, 12.5), (1.0, 2.5)], [(1.0, 9.5), (0.28, 7.0), (1.0, 4.5)], ("branch", 1, 0.50, (1.0, 7.5))],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.28, 6.5), (1.0, 3.5)], ("branch", 1, 0.52, (1.0, 6.5))],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 7.5), (0.28, 6.0), (1.0, 4.5)], ("branch", 0, 0.45, (1.0, 9.5))],
            ],
            [18, 18, 21, 21],
            4,
            "The face of a clock is cracked into 4 pieces so that two of the pieces each have a sum of 18, "
            "and the other two pieces each have a sum of 21. Which clock face shows this?",
            "In clock E, the top-right piece has {12, 1, 2, 3} = 18, the bottom piece has {5, 6, 7} = 18, "
            "the top-left piece has {10, 11} = 21, and the middle piece has {8, 9, 4} = 21.",
        ),
        # Practice .5: 4 pieces meeting at center with sums 15, 18, 21, 24 (increasing by 3) -> Answer: C
        (
            [
                [[12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],        # A: 15, 12, 21, 30
                [[11, 12, 1], [2, 3, 4], [5, 6, 7], [8, 9, 10]],        # B: 24, 9, 18, 27
                [[12, 1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]],        # C: 18, 15, 24, 21
                [[12, 1, 2, 3], [4, 5, 6, 7], [8, 9], [10, 11]],        # D: 18, 22, 17, 21
                [[11, 12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10]],        # E: 26, 12, 21, 19
            ],
            [
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 5.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 1.5), (0.0, 0.0)], [(1.0, 4.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)], [(1.0, 9.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)], [(1.0, 9.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 5.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
            ],
            [15, 18, 21, 24],
            2,
            "The face of a clock is cracked into 4 wedge-shaped pieces meeting at the center. "
            "When ordered from smallest to largest, the sums of the pieces increase by 3 each time (15, 18, 21, and 24). "
            "Which clock face shows how it was cracked?",
            "In clock C, the four wedges are {4, 5, 6} = 15, {12, 1, 2, 3} = 18, {10, 11} = 21, and {7, 8, 9} = 24. "
            "Sorted in order, the sums are 15, 18, 21, and 24.",
        ),
    ]

    for idx, (p_list, cr_list, exp_sums, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_cracked_clock(p_list, exp_sums, ans_idx)
        fig = option_row([fig_cracked_clock(cr) for cr in cr_list], gap=12)
        d.problem(f"Practice {set_num}.{idx}", text, fig, "below")
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_11

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
