# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #11 - Question Generator."""
import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    option_row,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 11)


def _clock_pt(cx, cy, R, r_frac, clock_pos):
    ang = math.radians(90.0 - clock_pos * 30.0)
    return cx + r_frac * R * math.cos(ang), cy + r_frac * R * math.sin(ang)


def _bezier_ctrl(cx, cy, R, crack):
    (r1, p1), (rm, pm), (r2, p2) = crack
    x1, y1 = _clock_pt(cx, cy, R, r1, p1)
    xm, ym = _clock_pt(cx, cy, R, rm, pm)
    x2, y2 = _clock_pt(cx, cy, R, r2, p2)
    ix1, iy1 = _clock_pt(cx, cy, R, 0.46 if r1 >= 0.95 else r1, p1)
    ix2, iy2 = _clock_pt(cx, cy, R, 0.46 if r2 >= 0.95 else r2, p2)
    cx1 = 0.62 * ix1 + 0.38 * xm
    cy1 = 0.62 * iy1 + 0.38 * ym
    cx2 = 0.62 * ix2 + 0.38 * xm
    cy2 = 0.62 * iy2 + 0.38 * ym
    return (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)


def _eval_bezier(bpts, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = bpts
    u = 1.0 - t
    bx = (u ** 3) * x0 + 3 * (u ** 2) * t * x1 + 3 * u * (t ** 2) * x2 + (t ** 3) * x3
    by = (u ** 3) * y0 + 3 * (u ** 2) * t * y1 + 3 * u * (t ** 2) * y2 + (t ** 3) * y3
    return bx, by


def _cracks_to_polylines(cracks, R=33.0):
    """Convert crack specifications into 2D polylines for exact geometric intersection testing."""
    cx, cy = 0.0, 0.0
    drawn_beziers = []
    polylines = []
    for crack in cracks:
        if isinstance(crack[0], str) and crack[0] == "branch":
            _, parent_idx, t_val, (r2, p2) = crack
            bx, by = _eval_bezier(drawn_beziers[parent_idx], t_val)
            x2, y2 = _clock_pt(cx, cy, R, r2, p2)
            polylines.append([(bx, by), (x2, y2)])
        elif len(crack) == 2:
            (r1, p1), (r2, p2) = crack
            polylines.append([_clock_pt(cx, cy, R, r1, p1), _clock_pt(cx, cy, R, r2, p2)])
            drawn_beziers.append(None)
        elif len(crack) == 3:
            bpts = _bezier_ctrl(cx, cy, R, crack)
            drawn_beziers.append(bpts)
            pts = [_eval_bezier(bpts, i / 24.0) for i in range(25)]
            polylines.append(pts)
        else:
            polylines.append([_clock_pt(cx, cy, R, rf, cp) for rf, cp in crack])
            drawn_beziers.append(None)
    return polylines


def _segments_intersect(p1, p2, q1, q2):
    if (
        max(p1[0], p2[0]) < min(q1[0], q2[0]) - 1e-7
        or max(q1[0], q2[0]) < min(p1[0], p2[0]) - 1e-7
        or max(p1[1], p2[1]) < min(q1[1], q2[1]) - 1e-7
        or max(q1[1], q2[1]) < min(p1[1], p2[1]) - 1e-7
    ):
        return False

    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])

    d1 = ccw(q1, q2, p1)
    d2 = ccw(q1, q2, p2)
    d3 = ccw(p1, p2, q1)
    d4 = ccw(p1, p2, q2)
    return (d1 * d2 <= 1e-7) and (d3 * d4 <= 1e-7)


def extract_parts_from_cracks(cracks, R=33.0):
    """Geometrically extract the connected components of clock numbers {1..12} from the 2D crack polylines."""
    polylines = _cracks_to_polylines(cracks, R=R)
    segments = []
    for poly in polylines:
        for i in range(len(poly) - 1):
            segments.append((poly[i], poly[i + 1]))

    hr_pts = {hr: _clock_pt(0.0, 0.0, R, 0.78, hr) for hr in range(1, 13)}

    def blocked(pA, pB):
        return any(_segments_intersect(pA, pB, s0, s1) for s0, s1 in segments)

    adj = {hr: set() for hr in range(1, 13)}
    for u in range(1, 13):
        for v in range(u + 1, 13):
            if not blocked(hr_pts[u], hr_pts[v]):
                adj[u].add(v)
                adj[v].add(u)

    visited = set()
    components = []
    for hr in range(1, 13):
        if hr not in visited:
            comp = []
            stack = [hr]
            visited.add(hr)
            while stack:
                curr = stack.pop()
                comp.append(curr)
                for nxt in adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        stack.append(nxt)
            components.append(sorted(comp))
    return sorted(components)


def fig_cracked_clock(cracks, R=33):
    """Draw a clock face (1..12) with cracks specified as lists of (r_frac, clock_pos) points."""
    pad = 4
    w = 2 * R + 2 * pad
    h = 2 * R + 2 * pad

    def draw(c, x, y):
        cx = x + pad + R
        cy = y + pad + R

        def pt(r_frac, clock_pos):
            return _clock_pt(cx, cy, R, r_frac, clock_pos)

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

        drawn_beziers = []
        for crack in cracks:
            if isinstance(crack[0], str) and crack[0] == "branch":
                _, parent_idx, t_val, (r2, p2) = crack
                bx, by = _eval_bezier(drawn_beziers[parent_idx], t_val)
                x2, y2 = pt(r2, p2)
                c.line(bx, by, x2, y2)
            elif len(crack) == 2:
                (r1, p1), (r2, p2) = crack
                c.line(*pt(r1, p1), *pt(r2, p2))
                drawn_beziers.append(None)
            elif len(crack) == 3:
                bpts = _bezier_ctrl(cx, cy, R, crack)
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
        c.setLineWidth(1)

    return w, h, draw


def check_cracked_clock(options_parts, options_cracks, expected_sums, answer_idx):
    """Verify both geometrically (from options_cracks) and arithmetically (from options_parts)
    that each option partitions 1..12 into the stated pieces and only answer_idx has expected_sums.
    """
    full_clock = list(range(1, 13))
    target_sorted = sorted(expected_sums)
    assert sum(target_sorted) == 78, f"Target sums {target_sorted} do not add to 78"
    matching = []
    for idx, (parts, cracks) in enumerate(zip(options_parts, options_cracks)):
        flat = sorted(x for p in parts for x in p)
        assert flat == full_clock, f"Option {idx} does not partition 1..12: {parts}"
        geom_parts = extract_parts_from_cracks(cracks)
        expected_parts = sorted(sorted(p) for p in parts)
        assert geom_parts == expected_parts, (
            f"Geometric mismatch on option {idx}: cracks give {geom_parts}, expected {expected_parts}"
        )
        sums = sorted(sum(p) for p in parts)
        if sums == target_sorted:
            matching.append(idx)
    assert matching == [answer_idx], f"Expected unique match at {answer_idx} for sums {target_sorted}, got {matching}"


def _wedges_from_cuts(cuts):
    """Given sorted half-integer boundary cuts c_0 < c_1 < ... < c_{k-1} in {0.5, 1.5, ..., 11.5},
    return both the partition of 1..12 into k contiguous arcs and the radial crack list.
    """
    cuts_sorted = sorted(cuts)
    k = len(cuts_sorted)
    parts = []
    for i in range(k):
        start_hr = int(cuts_sorted[i] + 0.5)
        end_hr = int(cuts_sorted[(i + 1) % k] - 0.5)
        piece = []
        hr = start_hr
        while True:
            hr_norm = ((hr - 1) % 12) + 1
            piece.append(hr_norm)
            if hr_norm == (((end_hr - 1) % 12) + 1):
                break
            hr += 1
        parts.append(piece)
    cracks = [[(1.0, c), (0.0, 0.0)] for c in cuts_sorted]
    return parts, cracks


def _generate_dynamic_clock_problem(rng, variant_type=0):
    """Procedurally generate a cracked-clock problem with randomized distractors and shuffled A-E choices."""
    vtype = variant_type % 5

    if vtype == 0:
        # 3 pieces with equal sums (26, 26, 26) using two horizontal/band cracks
        good_parts = [[11, 12, 1, 2], [9, 10, 3, 4], [5, 6, 7, 8]]
        good_cracks = [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 4.5)]]
        distractor_pool = [
            (
                [[12, 1, 2, 3], [10, 11, 4, 5], [6, 7, 8, 9]],
                [[(1.0, 11.5), (0.25, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.25, 7.5), (1.0, 5.5)]],
            ),
            (
                [[10, 11, 12, 1], [8, 9, 2, 3], [4, 5, 6, 7]],
                [[(1.0, 9.5), (0.25, 11.5), (1.0, 1.5)], [(1.0, 7.5), (0.25, 5.5), (1.0, 3.5)]],
            ),
            (
                [[11, 12, 1], [9, 10, 2, 3], [4, 5, 6, 7, 8]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 1.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 3.5)]],
            ),
            (
                [[11, 12, 1, 2], [10, 3, 4], [5, 6, 7, 8, 9]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 9.5), (0.25, 7.0), (1.0, 4.5)]],
            ),
            (
                [[12, 1, 2], [10, 11, 3, 4], [5, 6, 7, 8, 9]],
                [[(1.0, 11.5), (0.25, 1.0), (1.0, 2.5)], [(1.0, 9.5), (0.25, 7.0), (1.0, 4.5)]],
            ),
        ]
        rng.shuffle(distractor_pool)
        chosen_distractors = distractor_pool[:4]
        exp_sums = [26, 26, 26]
        text = (
            "The face of a clock is cracked into 3 pieces so that the sums of the numbers on all 3 pieces are equal. "
            "Which clock face shows how it was cracked?"
        )
        reason = (
            "Since the numbers 1 through 12 add up to 78, each of the 3 equal pieces must have a sum of 78 ÷ 3 = 26. "
            "In clock %s, the top piece has 11 + 12 + 1 + 2 = 26, the middle piece has 9 + 10 + 3 + 4 = 26, "
            "and the bottom piece has 5 + 6 + 7 + 8 = 26."
        )

    elif vtype == 1:
        # 3 wedge pieces meeting at center with consecutive sums (25, 26, 27)
        good_cuts = (2.5, 7.5, 10.5)
        good_parts, good_cracks = _wedges_from_cuts(good_cuts)
        distractor_cuts = [
            (2.5, 6.5, 10.5),
            (3.5, 8.5, 11.5),
            (0.5, 6.5, 9.5),
            (1.5, 7.5, 10.5),
            (2.5, 7.5, 9.5),
            (3.5, 7.5, 10.5),
        ]
        rng.shuffle(distractor_cuts)
        chosen_distractors = [_wedges_from_cuts(c) for c in distractor_cuts[:4]]
        exp_sums = [25, 26, 27]
        text = (
            "The face of a clock is cracked into 3 pieces meeting at the center. The sums of the numbers within the 3 parts "
            "are consecutive numbers. Which clock face shows how it was cracked?"
        )
        reason = (
            "Three consecutive numbers that add up to 78 are 25, 26, and 27 (25 + 26 + 27 = 78). "
            "In clock %s, the three pieces are {3, 4, 5, 6, 7} = 25, {11, 12, 1, 2} = 26, and {8, 9, 10} = 27."
        )

    elif vtype == 2:
        # 2 pieces by a single crack with a target ratio/equality: either equal sums (39, 39) or 1:2 ratio (26, 52)
        submode = rng.choice(["equal_39", "double_26_52", "consecutive_even_38_40"])
        if submode == "equal_39":
            good_cuts = (3.5, 9.5)
            exp_sums = [39, 39]
            text = (
                "A clock face is cracked into 2 pieces by a single crack so that the sum of the numbers on one piece "
                "equals the sum of the numbers on the other piece. Which clock face shows this crack?"
            )
            reason = (
                "Half of the total clock sum is 78 ÷ 2 = 39. In clock %s, the crack goes between 9 and 10 on the left "
                "and between 3 and 4 on the right, giving {10, 11, 12, 1, 2, 3} = 39 and {4, 5, 6, 7, 8, 9} = 39."
            )
        elif submode == "double_26_52":
            # Either {11,12,1,2}=26 or {5,6,7,8}=26; pick one and don't put the other in distractors!
            if rng.random() < 0.5:
                good_cuts = (2.5, 10.5)
                arc_desc = "{11, 12, 1, 2} = 26 and {3, 4, 5, 6, 7, 8, 9, 10} = 52"
            else:
                good_cuts = (4.5, 8.5)
                arc_desc = "{5, 6, 7, 8} = 26 and {9, 10, 11, 12, 1, 2, 3, 4} = 52"
            exp_sums = [26, 52]
            text = (
                "A clock face is cracked into 2 pieces by a single straight crack so that the sum of the numbers on "
                "the larger piece is exactly <b>twice</b> the sum of the numbers on the smaller piece. Which clock face shows this?"
            )
            reason = (
                f"Since the total sum is 78 and one piece has twice the sum of the other, the two sums must be "
                f"78 ÷ 3 = 26 and 2 × 26 = 52. In clock %s, the pieces are {arc_desc}."
            )
        else:
            good_cuts = (7.5, 11.5)
            exp_sums = [38, 40]
            text = (
                "A clock face is cracked into 2 pieces by a single crack so that the sums of the numbers on the two pieces "
                "are two consecutive even numbers (38 and 40). Which clock face shows this crack?"
            )
            reason = (
                "Two consecutive even numbers that add up to 78 are 38 and 40. In clock %s, one piece has "
                "{8, 9, 10, 11} = 38 and the other piece has {12, 1, 2, 3, 4, 5, 6, 7} = 40."
            )

        def make_single_crack(c1, c2):
            return _wedges_from_cuts((c1, c2))

        good_parts, good_cracks = make_single_crack(*good_cuts)
        cand_pairs = [
            (5.5, 11.5),
            (4.5, 10.5),
            (0.5, 6.5),
            (2.5, 8.5),
            (1.5, 7.5),
            (3.5, 8.5),
            (1.5, 9.5),
        ]
        rng.shuffle(cand_pairs)
        chosen_distractors = []
        for c1, c2 in cand_pairs:
            p, cr = make_single_crack(c1, c2)
            if sorted(sum(x) for x in p) != sorted(exp_sums):
                chosen_distractors.append((p, cr))
            if len(chosen_distractors) == 4:
                break

    elif vtype == 3:
        # 4 pieces where two pieces sum to 18 and two pieces sum to 21
        good_parts = [[12, 1, 2, 3], [10, 11], [8, 9, 4], [5, 6, 7]]
        good_cracks = [
            [(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)],
            [(1.0, 7.5), (0.28, 6.0), (1.0, 4.5)],
            ("branch", 0, 0.45, (1.0, 9.5)),
        ]
        distractor_pool = [
            (
                [[12, 1, 2, 3], [11, 4, 5], [9, 10], [6, 7, 8]],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
            ),
            (
                [[12, 1, 2], [11, 3, 4, 5], [6, 7, 8], [9, 10]],
                [[(1.0, 11.5), (0.22, 1.0), (1.0, 2.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
            ),
            (
                [[11, 12, 1, 2], [10, 3, 4], [8, 9], [5, 6, 7]],
                [[(1.0, 10.5), (0.22, 12.5), (1.0, 2.5)], [(1.0, 9.5), (0.28, 7.0), (1.0, 4.5)], ("branch", 1, 0.50, (1.0, 7.5))],
            ),
            (
                [[12, 1, 2, 3], [10, 11], [7, 8, 9], [4, 5, 6]],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.28, 8.0), (1.0, 6.5)], ("branch", 0, 0.45, (1.0, 9.5))],
            ),
        ]
        rng.shuffle(distractor_pool)
        chosen_distractors = distractor_pool[:4]
        exp_sums = [18, 18, 21, 21]
        text = (
            "The face of a clock is cracked into 4 pieces so that two of the pieces each have a sum of 18, "
            "and the other two pieces each have a sum of 21. Which clock face shows this?"
        )
        reason = (
            "In clock %s, the top-right piece has {12, 1, 2, 3} = 18, the bottom piece has {5, 6, 7} = 18, "
            "the top-left piece has {10, 11} = 21, and the middle piece has {8, 9, 4} = 21."
        )

    else:
        # 4 wedge pieces meeting at center with arithmetic progression sums (15, 18, 21, 24)
        good_cuts = (3.5, 6.5, 9.5, 11.5)
        good_parts, good_cracks = _wedges_from_cuts(good_cuts)
        distractor_cuts = [
            (2.5, 5.5, 8.5, 11.5),
            (1.5, 4.5, 7.5, 10.5),
            (3.5, 7.5, 9.5, 11.5),
            (2.5, 5.5, 8.5, 10.5),
            (3.5, 6.5, 8.5, 11.5),
        ]
        rng.shuffle(distractor_cuts)
        chosen_distractors = [_wedges_from_cuts(c) for c in distractor_cuts[:4]]
        exp_sums = [15, 18, 21, 24]
        text = (
            "The face of a clock is cracked into 4 wedge-shaped pieces meeting at the center. "
            "When ordered from smallest to largest, the sums of the pieces increase by 3 each time (15, 18, 21, and 24). "
            "Which clock face shows how it was cracked?"
        )
        reason = (
            "In clock %s, the four wedges are {4, 5, 6} = 15, {12, 1, 2, 3} = 18, {10, 11} = 21, and {7, 8, 9} = 24. "
            "Sorted in order, the sums are 15, 18, 21, and 24."
        )

    all_opts = chosen_distractors + [(good_parts, good_cracks)]
    order = list(range(5))
    rng.shuffle(order)
    p_list = [all_opts[i][0] for i in order]
    cr_list = [all_opts[i][1] for i in order]
    ans_idx = order.index(4)
    expl = reason % LETTERS[ans_idx]
    check_cracked_clock(p_list, cr_list, exp_sums, ans_idx)
    return p_list, cr_list, exp_sums, ans_idx, text, expl


def q_2002_11(d, key, set_num=2, include_orig=True, num_practice=5, seed=None):
    d.heading(
        f"Problem {set_num}: 2002 #11 - Cracked Clock Face",
        "Partitioning the clock face (sum 1 + 2 + ... + 12 = 78) into pieces with given sum properties",
    )

    if include_orig:
        parts0 = [
            [[9, 10], [7, 8], [11, 5, 6], [12, 1, 2, 3, 4]],        # A: sums 19, 15, 22, 22
            [[11, 12], [7, 8, 9], [6], [10, 1, 2, 3, 4, 5]],        # B: sums 23, 24, 6, 25
            [[12, 1, 2, 3], [9, 10], [11, 4, 5], [6, 7, 8]],        # C: sums 18, 19, 20, 21
            [[10, 11], [9, 12, 1], [7, 8, 2, 3], [4, 5, 6]],        # D: sums 21, 22, 20, 15
            [[8, 9, 10, 11], [12, 1, 2, 3], [4, 5, 6, 7]],          # E: only 3 pieces (38, 18, 22)
        ]
        cracks0 = [
            [[(1.0, 10.55), (0.35, 8.5), (1.0, 6.45)], [(1.0, 11.45), (0.15, 8.0), (1.0, 4.55)], ("branch", 0, 0.52, (1.0, 8.5))],
            [[(1.0, 10.5), (0.28, 11.5), (1.0, 0.5)], [(1.0, 9.5), (0.35, 7.2), (1.0, 5.5)], ("branch", 1, 0.62, (1.0, 6.5))],
            [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
            [[(1.0, 11.5), (0.28, 10.5), (1.0, 9.5)], [(1.0, 1.5), (0.05, 5.0), (1.0, 8.5)], [(1.0, 3.5), (0.32, 5.0), (1.0, 6.5)]],
            [[(1.0, 11.5), (0.2, 9.5), (1.0, 7.5)], ("branch", 0, 0.5, (1.0, 3.5))],
        ]
        check_cracked_clock(parts0, cracks0, [18, 19, 20, 21], 2)
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

    rng = random.Random(seed)
    vtypes = [0, 1, 2, 3, 4]
    rng.shuffle(vtypes)
    for idx in range(1, num_practice + 1):
        vt = vtypes[(idx - 1) % len(vtypes)]
        p_list, cr_list, exp_sums, ans_idx, text, expl = _generate_dynamic_clock_problem(rng, variant_type=vt)
        fig = option_row([fig_cracked_clock(cr) for cr in cr_list], gap=12)
        d.problem(f"Practice {set_num}.{idx}", text, fig, "below")
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_11

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
