# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #15 - Question Generator."""
import os
import sys
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
QUESTION_ID = (2002, 15)


def _build_flag_polygon(spec, x=0.0, y=0.0, s=1.0):
    """Build the 2D polygon vertices and pole attachment coordinates (px, att_bot, att_top)
    for a flag specification (either a string kind or a (kind, param) tuple).
    """
    if isinstance(spec, tuple):
        kind, param = spec
    else:
        kind, param = spec, 0.0

    px = x + 6 * s
    att_bot = y + 14 * s
    att_top = y + 44 * s
    fw = (36 + param) * s

    if kind == "flat":
        pts = [(px, att_bot), (px, att_top), (px + fw, att_top), (px + fw, att_bot)]
    elif kind == "fold_up_top":
        lift = (6 + 0.5 * param) * s
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + 8 * s, att_top),
            (px + 8 * s, att_top + lift),
            (px + fw, att_top + lift),
            (px + fw, att_top - 2 * s),
            (px + 8 * s, att_bot),
        ]
    elif kind == "fold_diag_peak":
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + 16 * s, att_top),
            (px + (20 + param) * s, att_top + 6 * s),
            (px + 30 * s, att_top),
            (px + fw + 2 * s, att_top),
            (px + fw + 2 * s, att_top - 6 * s),
        ]
    elif kind == "slanted_right":
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + fw + 2 * s, att_top),
            (px + fw + 2 * s, att_top - 6 * s),
            (px + fw - (8 + param) * s, att_bot),
        ]
    elif kind == "wavy_bottom":
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + fw, att_top),
            (px + fw - 4 * s, att_bot + (6 + 0.5 * param) * s),
            (px + 18 * s, att_bot),
        ]
    elif kind == "fold_down_bottom":
        dip = (5 + 0.5 * param) * s
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + 10 * s, att_top),
            (px + fw, att_bot + 4 * s),
            (px + fw, att_bot - dip),
            (px + 10 * s, att_bot - dip),
            (px + 10 * s, att_bot),
        ]
    elif kind == "flutter_inward":
        pts = [
            (px, att_bot),
            (px, att_top),
            (px + fw, att_top - 2 * s),
            (px + fw - 7 * s, (att_bot + att_top) / 2),
            (px + fw, att_bot + 2 * s),
        ]
    elif kind == "torn_pole_bottom":
        mid_y = (att_bot + att_top) / 2 + (3 + 0.5 * param) * s
        pts = [
            (px, mid_y),
            (px, att_top),
            (px + fw + 4 * s, att_top),
            (px + 14 * s, att_bot + 4 * s),
            (px + 14 * s, mid_y),
        ]
    elif kind == "torn_pole_top":
        mid_y = (att_bot + att_top) / 2 - (2 + 0.5 * param) * s
        pts = [
            (px, att_bot),
            (px, mid_y),
            (px + 14 * s, mid_y),
            (px + 14 * s, att_top),
            (px + fw, att_top),
            (px + fw - 6 * s, att_bot),
        ]
    elif kind == "torn_pole_middle":
        mid_y = (att_bot + att_top) / 2
        gap_h = (6 + 0.5 * param) * s
        pts = [
            (px, att_bot),
            (px, mid_y - gap_h),
            (px + 12 * s, mid_y),
            (px, mid_y + gap_h),
            (px, att_top),
            (px + fw, att_top),
            (px + fw, att_bot),
        ]
    elif kind == "giant_stretched":
        shift = (10 + 0.5 * param) * s
        pts = [
            (px + shift, att_bot),
            (px + shift, att_top),
            (px + fw + 4 * s, att_top),
            (px + fw + 4 * s, att_bot),
        ]
    elif kind == "torn_both_ends":
        inset = (6 + 0.4 * param) * s
        pts = [
            (px, att_bot + inset),
            (px, att_top - inset),
            (px + 12 * s, att_top),
            (px + fw, att_top),
            (px + fw, att_bot),
            (px + 12 * s, att_bot),
        ]
    else:
        raise ValueError(f"Unknown flag kind: {kind}")

    return pts, px, att_bot, att_top


def is_flag_intact_on_pole(spec, s=1.0):
    """Geometrically verify from the 2D polygon vertices whether the flag covers the full
    vertical attachment segment [att_bot, att_top] along the pole line x = px.
    """
    pts, px, att_bot, att_top = _build_flag_polygon(spec, 0.0, 0.0, s=s)
    pole_len = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if abs(x1 - px) < 1e-6 and abs(x2 - px) < 1e-6:
            lo = max(min(y1, y2), att_bot)
            hi = min(max(y1, y2), att_top)
            if hi > lo:
                pole_len += hi - lo
    return abs(pole_len - (att_top - att_bot)) < 1e-4


def fig_flag_silhouette(spec, s=1.0):
    """Draw a flagpole and shaded flag silhouette of the specified kind/spec."""
    w = 54 * s
    h = 54 * s

    def draw(c, x, y):
        py0 = y + 4 * s
        py1 = y + 44 * s
        pts, px, _, _ = _build_flag_polygon(spec, x, y, s=s)

        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.setFillColor(colors.Color(0.68, 0.70, 0.68))
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.0)
        c.drawPath(p, stroke=1, fill=1)

        # Draw thick vertical flagpole
        c.setStrokeColor(colors.black)
        c.setLineWidth(2.6)
        c.line(px, py0, px, py1 + 2 * s)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_flag_silhouette(specs, expected_idx, mode="impossible"):
    if mode == "impossible":
        matches = [i for i, sp in enumerate(specs) if not is_flag_intact_on_pole(sp)]
    else:
        matches = [i for i, sp in enumerate(specs) if is_flag_intact_on_pole(sp)]
    assert matches == [expected_idx], f"Flag silhouette geometric check failed: {matches} vs {expected_idx}"


INTACT_KINDS = [
    "flat",
    "fold_up_top",
    "fold_diag_peak",
    "slanted_right",
    "wavy_bottom",
    "fold_down_bottom",
    "flutter_inward",
]

TORN_SPECS = [
    (
        "torn_pole_bottom",
        "Because the left edge of the rectangular flag is fastened to the pole from top to bottom of the attachment, "
        "the silhouette must touch the entire attachment segment along the pole. Picture %s is missing the lower part "
        "along the pole, which can only happen if the flag is torn.",
    ),
    (
        "torn_pole_top",
        "Because the left edge of the rectangular flag is fastened to the pole along the entire attachment segment, "
        "the silhouette must cover that full segment on the pole. Picture %s is missing the upper half along the pole, "
        "which is impossible unless the flag is torn.",
    ),
    (
        "torn_pole_middle",
        "In picture %s, there is a V-shaped gap right along the middle of the flagpole where the flag is attached. "
        "Since the left edge is fixed to the pole, that gap cannot appear unless the flag is ripped.",
    ),
    (
        "giant_stretched",
        "In picture %s, there is an empty gap between the flagpole and the entire flag! Since the flag's left side is "
        "attached directly to the pole, picture %s is impossible unless the flag has come completely loose from the pole.",
    ),
    (
        "torn_both_ends",
        "In picture %s, both the top and bottom corners of the flag's left edge have pulled away from the flagpole. "
        "That cannot happen unless the flag is torn at both ends of its attachment.",
    ),
]


def _generate_dynamic_flag_problem(rng, variant_idx=0):
    """Procedurally generate a flag silhouette problem with randomized shapes and shuffled A-E options."""
    use_possible_mode = (variant_idx % 4 == 3)

    if not use_possible_mode:
        mode = "impossible"
        torn_kind, reason_tmpl = TORN_SPECS[variant_idx % len(TORN_SPECS)]
        chosen_intact = rng.sample(INTACT_KINDS, 4)
        specs = [(k, rng.choice([-2.0, 0.0, 2.0])) for k in chosen_intact]
        bad_spec = (torn_kind, rng.choice([-1.5, 0.0, 1.5]))
        all_specs = specs + [bad_spec]
        order = list(range(5))
        rng.shuffle(order)
        shuffled_specs = [all_specs[i] for i in order]
        ans_idx = order.index(4)
        letter = LETTERS[ans_idx]
        expl = reason_tmpl.replace("%s", letter)

        actor = rng.choice(["Leo", "Maya", "Sam", "Elena", "Noah"])
        noun = rng.choice(["flag", "banner"])
        text = (
            f"{actor} watches a rectangular {noun} attached along its left vertical edge to a pole "
            f"and sketches 5 silhouettes as the wind blows. Which sketch <b>cannot</b> happen unless the {noun} is torn from the pole?"
        )
    else:
        mode = "possible"
        chosen_torn = rng.sample([k for k, _ in TORN_SPECS], 4)
        good_kind = rng.choice(INTACT_KINDS)
        specs = [(k, rng.choice([-1.5, 0.0, 1.5])) for k in chosen_torn]
        good_spec = (good_kind, rng.choice([-2.0, 0.0, 2.0]))
        all_specs = specs + [good_spec]
        order = list(range(5))
        rng.shuffle(order)
        shuffled_specs = [all_specs[i] for i in order]
        ans_idx = order.index(4)
        letter = LETTERS[ans_idx]
        other_letters = ", ".join(LETTERS[i] for i in range(5) if i != ans_idx)
        text = (
            "Four of the 5 flag silhouettes below are impossible unless the rectangular flag is torn from the pole. "
            "Which silhouette <b>can</b> happen with an intact flag?"
        )
        expl = (
            f"Only in {letter} is the flag attached continuously along its full vertical segment on the flagpole. "
            f"In {other_letters}, parts of the flag are detached from the pole."
        )

    check_flag_silhouette(shuffled_specs, ans_idx, mode=mode)
    return shuffled_specs, ans_idx, mode, text, expl


def q_2002_15(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Flag Silhouette in the Wind", "Based on 2002, Problem 15")

    orig_kinds = ["fold_up_top", "torn_pole_bottom", "flat", "fold_diag_peak", "slanted_right"]
    check_flag_silhouette(orig_kinds, 1, mode="impossible")
    if include_orig:
        d.problem(
            "Original 2002 #15.",
            "From her window Karla looks at the wall of a house. There she can see the silhouette of a rectangular "
            "flag flying in the wind. At five different moments she draws the silhouette. Which of the 5 pictures "
            "cannot be right unless the flag is torn?",
            option_row([fig_flag_silhouette(k) for k in orig_kinds], gap=14),
            "below",
        )
        key.append((
            "2002 #15",
            "B",
            "The rectangular flag is attached to the flagpole along its entire left vertical edge, so the segment "
            "where the flag touches the pole must always keep its full height. In picture B, the lower half of the "
            "left edge is missing from the pole, which is impossible unless the flag is torn away from the pole.",
        ))

    rng = random.Random(seed)
    v_order = list(range(5))
    rng.shuffle(v_order)
    for idx in range(1, num_practice + 1):
        specs, ans_idx, mode, text, expl = _generate_dynamic_flag_problem(
            rng, variant_idx=v_order[(idx - 1) % len(v_order)]
        )
        check_flag_silhouette(specs, ans_idx, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            option_row([fig_flag_silhouette(sp) for sp in specs], gap=14),
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_15

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
