# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #7 - Question Generator."""
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
QUESTION_ID = (2002, 7)


def tok_path(tokens):
    """Yield drawing segments and bbox for a skyline token list."""
    x = y = 0
    pts = [(0, 0)]
    segs = []
    for t in tokens:
        k = t[0]
        if k == "H":
            segs.append(("L", x, y, x + t[1], y))
            x += t[1]
        elif k == "V":
            segs.append(("L", x, y, x, y + t[1]))
            y += t[1]
        elif k == "D":
            segs.append(("L", x, y, x + t[1], y + t[2]))
            x += t[1]
            y += t[2]
        elif k == "A":
            w = t[1]
            hh = w * 0.42
            segs.append(("C", x, y, w, hh))
            pts.append((x, y + hh))
            x += w
        pts.append((x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return segs, (min(xs), min(ys), max(xs), max(ys))


def fig_tokens(tokens, sc, lw=1.3):
    segs, (x0, y0, x1, y1) = tok_path(tokens)

    def draw(c, x, y):
        c.setLineWidth(lw)
        c.setStrokeColor(colors.black)
        for s in segs:
            if s[0] == "L":
                c.line(
                    x + (s[1] - x0) * sc,
                    y + (s[2] - y0) * sc,
                    x + (s[3] - x0) * sc,
                    y + (s[4] - y0) * sc,
                )
            else:
                _, ax, ay, w, hh = s
                X, Y = x + (ax - x0) * sc, y + (ay - y0) * sc
                p = c.beginPath()
                p.moveTo(X, Y)
                p.curveTo(
                    X,
                    Y + hh * sc * 4 / 3,
                    X + w * sc,
                    Y + hh * sc * 4 / 3,
                    X + w * sc,
                    Y,
                )
                c.drawPath(p, stroke=1, fill=0)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return (x1 - x0) * sc, (y1 - y0) * sc, draw


def _tok_match(t_sky, t_pc, is_end):
    if t_sky[0] != t_pc[0]:
        return False
    kind = t_sky[0]
    if kind == "A":
        return t_sky[1] == t_pc[1]
    if kind in ("H", "V"):
        if not is_end:
            return t_sky[1] == t_pc[1]
        return (t_sky[1] > 0 and t_pc[1] > 0 and abs(t_pc[1]) <= abs(t_sky[1])) or (
            t_sky[1] < 0 and t_pc[1] < 0 and abs(t_pc[1]) <= abs(t_sky[1])
        )
    if kind == "D":
        if not is_end:
            return t_sky[1] == t_pc[1] and t_sky[2] == t_pc[2]
        return (
            t_sky[1] * t_pc[2] == t_sky[2] * t_pc[1]
            and (t_sky[1] > 0) == (t_pc[1] > 0)
            and (t_sky[2] > 0) == (t_pc[2] > 0)
            and abs(t_pc[1]) <= abs(t_sky[1])
        )
    return False


def is_subpath_of_skyline(sky, pc):
    m = len(pc)
    for i in range(len(sky) - m + 1):
        if all(_tok_match(sky[i + j], pc[j], j == 0 or j == m - 1) for j in range(m)):
            return True
    return False


def skyline_problem(sky, pieces, sc, ans_idx=None):
    if ans_idx is not None:
        cannot_belong = [i for i, p in enumerate(pieces) if not is_subpath_of_skyline(sky, p)]
        assert cannot_belong == [ans_idx], f"Skyline check failed: expected {[ans_idx]}, got {cannot_belong}"
    return vstack([fig_tokens(sky, sc), option_row([fig_tokens(p, sc) for p in pieces], gap=24)], gap=16)


def _trim_end_token(tok):
    if tok[0] in ("H", "V") and abs(tok[1]) >= 35:
        sign = 1 if tok[1] > 0 else -1
        return (tok[0], sign * max(20, int(abs(tok[1]) * 0.6)))
    return tok


def _generate_dynamic_skyline_problem(rng, variant_type=0):
    """Procedurally generate a skyline contour with randomized dimensions and shuffled A-E pieces."""
    h_gap = rng.choice([34, 38, 42])
    arch_w = rng.choice([32, 36, 40])
    dome_w = rng.choice([52, 56, 60])
    wall_h = rng.choice([65, 72, 80])
    spire_h = rng.choice([95, 105, 115])
    roof_w = rng.choice([24, 28])
    roof_h = rng.choice([34, 40])
    ledge_w = rng.choice([26, 30])

    vtype = variant_type % 4
    if vtype == 0:
        # Variant 0: Double arch + flat-shouldered pointed roof + tall tower.
        # Bad piece: pointed roof sitting directly on the vertical wall without the flat shoulder!
        sky = [
            ("H", 50),
            ("A", arch_w),
            ("A", arch_w),
            ("H", h_gap),
            ("V", wall_h),
            ("H", ledge_w),
            ("D", roof_w, roof_h),
            ("D", roof_w, -roof_h),
            ("H", ledge_w),
            ("V", -wall_h),
            ("H", h_gap),
            ("V", spire_h),
            ("H", 20),
            ("V", -spire_h),
            ("H", 50),
        ]
        valid_pcs = [
            [_trim_end_token(sky[1]), sky[2], sky[3], _trim_end_token(sky[4])],
            [_trim_end_token(sky[4]), sky[5], sky[6]],
            [sky[7], sky[8], sky[9], _trim_end_token(sky[10])],
            [_trim_end_token(sky[10]), sky[11], sky[12], sky[13], _trim_end_token(sky[14])],
        ]
        bad_pc = [("V", 45), ("D", roof_w, roof_h), ("D", roof_w, -roof_h), ("H", ledge_w)]
        reason = (
            "In the skyline there is a flat horizontal ledge between the vertical wall and the pointed roof, "
            "whereas piece %s has the pointed roof sitting directly on the vertical wall."
        )
        sc = 0.45
    elif vtype == 1:
        # Variant 1: Two-notch battlement castle wall + dome + trapezoid roof.
        # Bad piece: battlement tower top with only ONE notch instead of TWO!
        bw = rng.choice([22, 25])
        nw = rng.choice([18, 22])
        nd = rng.choice([14, 18])
        bh = rng.choice([48, 55])
        sky = [
            ("H", 45),
            ("V", bh),
            ("H", bw),
            ("V", -nd),
            ("H", nw),
            ("V", nd),
            ("H", bw),
            ("V", -nd),
            ("H", nw),
            ("V", nd),
            ("H", bw),
            ("V", -bh),
            ("H", h_gap),
            ("A", dome_w),
            ("H", h_gap),
            ("D", 32, 46),
            ("H", 36),
            ("D", 32, -46),
            ("H", 45),
        ]
        valid_pcs = [
            [_trim_end_token(sky[11]), sky[12], sky[13], _trim_end_token(sky[14])],
            [sky[13], sky[14], sky[15], _trim_end_token(sky[16])],
            [_trim_end_token(sky[16]), sky[17], _trim_end_token(sky[18])],
            [sky[6], sky[7], sky[8], sky[9], sky[10], sky[11], _trim_end_token(sky[12])],
        ]
        bad_pc = [("V", bh), ("H", bw), ("V", -nd), ("H", nw), ("V", nd), ("H", bw), ("V", -bh)]
        reason = (
            "The castle battlement wall has TWO notches along the top, whereas piece %s shows a complete tower top "
            "with only ONE notch."
        )
        sc = 0.42
    elif vtype == 2:
        # Variant 2: Small arch + pointed tower + dome + stepped tower.
        # Bad piece: goes DOWN after an arch (in the skyline, the line always goes flat and then UP after an arch).
        h1 = rng.choice([32, 38])
        h2 = wall_h - h1 + 15
        sky = [
            ("H", 45),
            ("A", arch_w),
            ("H", ledge_w),
            ("V", wall_h),
            ("D", roof_w, roof_h),
            ("D", roof_w, -roof_h),
            ("V", -wall_h),
            ("H", h_gap),
            ("A", dome_w),
            ("H", ledge_w),
            ("V", h1 + h2),
            ("H", 24),
            ("V", -h1),
            ("H", 24),
            ("V", -h2),
            ("H", 45),
        ]
        valid_pcs = [
            [sky[8], sky[9], _trim_end_token(sky[10])],
            [sky[2], sky[3], sky[4], sky[5]],
            [_trim_end_token(sky[10]), sky[11], sky[12], sky[13], sky[14], _trim_end_token(sky[15])],
            [_trim_end_token(sky[6]), sky[7], sky[8]],
        ]
        bad_pc = [("A", arch_w), ("H", ledge_w), ("V", -40)]
        reason = (
            "After every arch in the skyline, the contour goes flat and then straight UP into a tower, "
            "whereas piece %s goes DOWN after the arch."
        )
        sc = 0.44
    else:
        # Variant 3: Twin arches touching directly + stepped tower + twin arches on a tower.
        # Bad piece: two arches separated by a flat horizontal gap ("A", "H", "A") when twin arches always touch directly!
        sky = [
            ("H", 40),
            ("A", arch_w),
            ("A", arch_w),
            ("H", h_gap),
            ("V", wall_h),
            ("D", roof_w, roof_h),
            ("D", roof_w, -roof_h),
            ("V", -wall_h),
            ("H", h_gap),
            ("V", wall_h),
            ("A", arch_w),
            ("A", arch_w),
            ("V", -wall_h),
            ("H", 40),
        ]
        valid_pcs = [
            [sky[1], sky[2], sky[3], _trim_end_token(sky[4])],
            [_trim_end_token(sky[4]), sky[5], sky[6], _trim_end_token(sky[7])],
            [_trim_end_token(sky[8]), sky[9], sky[10]],
            [sky[10], sky[11], sky[12], _trim_end_token(sky[13])],
        ]
        bad_pc = [("A", arch_w), ("H", 28), ("A", arch_w)]
        reason = (
            "Wherever two arches appear in the skyline, they sit right next to each other with no flat gap between them, "
            "whereas piece %s has a flat segment between the two arches."
        )
        sc = 0.44

    all_pcs = valid_pcs + [bad_pc]
    order = list(range(5))
    rng.shuffle(order)
    shuffled_pcs = [all_pcs[i] for i in order]
    ans_idx = order.index(4)
    expl = reason % LETTERS[ans_idx]
    return sky, shuffled_pcs, sc, ans_idx, expl


def q_2002_7(d, key, set_num=2, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Pieces of a skyline", "Based on 2002, Problem 7")
    if include_orig:
        sky = [
            ("A", 40), ("A", 40), ("H", 42), ("V", 40), ("H", 83), ("V", 42), ("D", 42, 43), ("D", 43, -43),
            ("V", -42), ("H", 83), ("V", -40), ("H", 42), ("D", 40, 40), ("D", 40, -40), ("V", 80), ("A", 40),
            ("A", 40), ("V", -80), ("H", 40), ("V", 40), ("H", 45), ("V", 85), ("H", 15), ("V", -85), ("H", 40),
            ("V", -40), ("H", 40),
        ]
        pcs = [
            [("V", -30), ("H", 40), ("V", -40), ("H", 30)],
            [("D", 40, -40), ("V", 80), ("A", 40)],
            [("A", 40), ("V", -50), ("H", 25), ("V", 50), ("A", 40)],
            [("H", 40), ("V", -40), ("H", 42), ("D", 40, 40)],
            [("A", 40), ("A", 40), ("V", -50)],
        ]
        d.problem(
            "Original 2002 #7.",
            "Far away we see the skyline of a castle. Which of the pieces <b>cannot</b> belong to the skyline?",
            skyline_problem(sky, pcs, 0.36, ans_idx=2),
            "below",
        )
        key.append((
            "2002 #7",
            "C",
            "Wherever there are two arches, they sit right next to each other. There is never a U-shaped dip between two arches.",
        ))

    rng = random.Random(seed)
    vtypes = [0, 1, 2, 3]
    rng.shuffle(vtypes)
    for idx in range(1, num_practice + 1):
        vt = vtypes[(idx - 1) % len(vtypes)]
        sky, pcs, sc, ans_idx, expl = _generate_dynamic_skyline_problem(rng, variant_type=vt)
        d.problem(
            f"Practice {set_num}.{idx}",
            "Here is the skyline of a castle. Which piece (A through E) <b>cannot</b> belong to it?",
            skyline_problem(sky, pcs, sc, ans_idx=ans_idx),
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_7

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
