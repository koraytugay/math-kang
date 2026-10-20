# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #9 - Question Generator."""
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
QUESTION_ID = (2003, 9)


def solve_brick_cubes(Wn, Hn, Dn, mode="inside"):
    """Exact 3D voxel enumeration solver for an Wn x Hn x Dn brick."""
    inside_count = 0
    outside_count = 0
    for ix in range(Wn):
        for iy in range(Hn):
            for iz in range(Dn):
                if 0 < ix < Wn - 1 and 0 < iy < Hn - 1 and 0 < iz < Dn - 1:
                    inside_count += 1
                else:
                    outside_count += 1
    assert inside_count == max(0, Wn - 2) * max(0, Hn - 2) * max(0, Dn - 2)
    assert inside_count + outside_count == Wn * Hn * Dn
    if mode == "inside":
        return inside_count
    elif mode == "outside":
        return outside_count
    elif mode == "diff":
        return outside_count - inside_count
    raise ValueError(f"Unknown mode: {mode}")


def check_brick_cubes(Wn, Hn, Dn, choices, ans_idx, mode="inside"):
    val = solve_brick_cubes(Wn, Hn, Dn, mode=mode)
    matches = [i for i, ch in enumerate(choices) if int(ch) == val]
    assert matches == [ans_idx], f"Brick ({Wn},{Hn},{Dn}) mode={mode}: expected {val} at {ans_idx}, got {choices}"


def fig_brick(Wn, Hn, Dn, s=12):
    k = 0.45 * s  # oblique offset per depth unit
    pad = 4
    w = Wn * s + Dn * k + 2 * pad
    h = Hn * s + Dn * k + 2 * pad

    def draw(c, x, y):
        ox = x + pad
        oy = y + pad
        rx = ox + Wn * s
        top = oy + Hn * s

        # Shaded faces (front, top, right)
        c.setFillColor(colors.white)
        c.rect(ox, oy, Wn * s, Hn * s, stroke=0, fill=1)

        p_top = c.beginPath()
        p_top.moveTo(ox, top)
        p_top.lineTo(rx, top)
        p_top.lineTo(rx + Dn * k, top + Dn * k)
        p_top.lineTo(ox + Dn * k, top + Dn * k)
        p_top.close()
        c.setFillColor(colors.Color(0.95, 0.95, 0.95))
        c.drawPath(p_top, stroke=0, fill=1)

        p_right = c.beginPath()
        p_right.moveTo(rx, oy)
        p_right.lineTo(rx + Dn * k, oy + Dn * k)
        p_right.lineTo(rx + Dn * k, top + Dn * k)
        p_right.lineTo(rx, top)
        p_right.close()
        c.setFillColor(colors.Color(0.84, 0.84, 0.84))
        c.drawPath(p_right, stroke=0, fill=1)

        c.setStrokeColor(colors.black)
        c.setLineWidth(0.85)
        for i in range(Wn + 1):
            c.line(ox + i * s, oy, ox + i * s, top)
        for j in range(Hn + 1):
            c.line(ox, oy + j * s, rx, oy + j * s)
        for i in range(Wn + 1):  # top receding lines
            c.line(ox + i * s, top, ox + i * s + Dn * k, top + Dn * k)
        for d in range(Dn + 1):
            c.line(ox + d * k, top + d * k, rx + d * k, top + d * k)
        for j in range(Hn + 1):  # right side receding lines
            c.line(rx, oy + j * s, rx + Dn * k, oy + j * s + Dn * k)
        for d in range(Dn + 1):
            c.line(rx + d * k, oy + d * k, rx + d * k, top + d * k)

        c.setLineWidth(1.5)
        p = c.beginPath()
        p.moveTo(ox, oy)
        p.lineTo(rx, oy)
        p.lineTo(rx + Dn * k, oy + Dn * k)
        p.lineTo(rx + Dn * k, top + Dn * k)
        p.lineTo(ox + Dn * k, top + Dn * k)
        p.lineTo(ox, top)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


COLOR_PAIRS = [
    ("red", "blue"),
    ("yellow", "green"),
    ("white", "black"),
    ("orange", "purple"),
]

NAMES = ["Maya", "Leo", "Anna", "Noah", "Clara", "Sam", "Elena", "Max"]


def _make_brick_choices(rng, ans_val, extra_cands=()):
    cands = {ans_val}
    for c in extra_cands:
        if c > 0 and c != ans_val:
            cands.add(c)
    for delta in [-4, -2, 2, 4, 6, -6, 8, 12, -3, 3]:
        if len(cands) >= 5:
            break
        v = ans_val + delta
        if v >= 1:
            cands.add(v)
    vals = sorted(list(cands))[:5]
    if ans_val not in vals:
        vals[-1] = ans_val
        vals.sort()
    ans_idx = vals.index(ans_val)
    return vals, ans_idx


def _generate_dynamic_brick_problem(rng, mode_idx=0):
    """Procedurally generate a 3D W x H x D brick problem with randomized dimensions and colors."""
    actor = rng.choice(NAMES)
    c_out, c_in = rng.choice(COLOR_PAIRS)

    while True:
        Wn = rng.randint(4, 7)
        Hn = rng.randint(3, 5)
        Dn = rng.randint(3, 5)
        if (Wn, Hn, Dn) != (5, 4, 4):
            break

    iw, ih, id_ = Wn - 2, Hn - 2, Dn - 2
    inside_val = iw * ih * id_
    total_val = Wn * Hn * Dn
    outside_val = total_val - inside_val

    m = mode_idx % 3
    if m in (0, 1):
        mode = "inside"
        ans_val = inside_val
        extra = [
            (Wn - 1) * (Hn - 1) * (Dn - 1),
            iw * ih * Dn,
            Wn * ih * id_,
            inside_val * 2,
            outside_val,
        ]
        opts, ans_idx = _make_brick_choices(rng, ans_val, extra_cands=extra)
        text = (
            f"{actor} built this brick ({Wn} cubes wide, {Hn} cubes tall, {Dn} cubes deep) using {c_out} and {c_in} "
            f"cubes of the same size. The outside of the brick is completely {c_out}, and all the cubes hidden inside "
            f"are {c_in}. How many <b>{c_in}</b> cubes did {actor} use?"
        )
        expl = (
            f"Removing the outer layer of {c_out} cubes reduces each dimension by 2: "
            f"the inside block of {c_in} cubes is ({Wn}-2) × ({Hn}-2) × ({Dn}-2) = {iw} × {ih} × {id_} = {inside_val}."
        )
    else:
        mode = "outside"
        ans_val = outside_val
        extra = [
            total_val,
            total_val - inside_val * 2,
            total_val - (Wn - 1) * (Hn - 1) * (Dn - 1),
            outside_val - 4,
            outside_val + 4,
        ]
        opts, ans_idx = _make_brick_choices(rng, ans_val, extra_cands=extra)
        text = (
            f"{actor} built this brick ({Wn} cubes wide, {Hn} cubes tall, {Dn} cubes deep). The outside is completely "
            f"{c_out} and all the cubes completely inside are {c_in}. How many <b>{c_out}</b> cubes did {actor} use?"
        )
        expl = (
            f"The entire brick has {Wn} × {Hn} × {Dn} = {total_val} cubes, and the hidden {c_in} core has "
            f"({Wn}-2) × ({Hn}-2) × ({Dn}-2) = {iw} × {ih} × {id_} = {inside_val} cubes. "
            f"So there are {total_val} - {inside_val} = {outside_val} {c_out} cubes."
        )

    check_brick_cubes(Wn, Hn, Dn, opts, ans_idx, mode=mode)
    return Wn, Hn, Dn, opts, ans_idx, mode, text, expl


def q_2003_9(d, key, set_num=4, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Red outside, blue inside", "Based on 2003, Problem 9")
    if include_orig:
        opts0 = [12, 24, 36, 40, 48]
        check_brick_cubes(5, 4, 4, opts0, 0, mode="inside")
        d.problem(
            "Original 2003 #9.",
            "Chris built the brick in the picture using red and blue cubes of the same "
            "size. The outside of the brick is completely red, but all cubes used inside are blue. "
            "How many blue cubes did Chris use?",
            fig_brick(5, 4, 4),
            "right",
            opts0,
        )
        key.append(("2003 #9", "A", "Brick is 5 x 4 x 4. Remove the outer layer: inside is 3 x 2 x 2 = 12 blue cubes."))

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        Wn, Hn, Dn, opts, ans_idx, mode, text, expl = _generate_dynamic_brick_problem(rng, mode_idx=m)
        check_brick_cubes(Wn, Hn, Dn, opts, ans_idx, mode=mode)
        s_scale = 11 if max(Wn, Hn, Dn) >= 6 else 12
        d.problem(f"Practice {set_num}.{idx}", text, fig_brick(Wn, Hn, Dn, s=s_scale), "right", opts)
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_9

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
