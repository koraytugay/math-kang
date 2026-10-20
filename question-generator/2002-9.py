# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #9 - Question Generator."""
import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    GRAY,
    NUM_WORDS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 9)


def solve_balance_scale(
    left_small,
    left_big,
    right_small,
    right_big,
    add_left_small=0,
    add_left_big=0,
    query_big_count=1,
):
    """Exact algebraic solver for the two-pan balance scale problem.
    Returns (w, initial_tilt, answer_val) where 1 big fruit = w small fruits,
    initial_tilt in {-1, 0, 1} (-1 = left heavier, 0 = level, +1 = right heavier),
    and answer_val = query_big_count * w.
    """
    # After adjustment: (left_small + add_left_small) + (left_big + add_left_big) * w = right_small + right_big * w
    net_big = right_big - (left_big + add_left_big)
    net_small = (left_small + add_left_small) - right_small
    if net_big < 0:
        net_big, net_small = -net_big, -net_small
    assert net_big > 0 and net_small > 0 and net_small % net_big == 0, (
        f"Invalid balance equation: {net_small} small = {net_big} big"
    )
    w = net_small // net_big
    left_init = left_small + left_big * w
    right_init = right_small + right_big * w
    if right_init > left_init:
        tilt = 1
    elif left_init > right_init:
        tilt = -1
    else:
        tilt = 0
    return w, tilt, query_big_count * w


def _draw_pan_items(c, px, ty, items):
    """Draw circle items on a pan centered at px, sitting on y=ty, stacking into 2 rows if wide."""
    if not items:
        return
    gap = 1.6
    max_pan_w = 64.0
    total_w = sum(2 * r for r in items) + gap * (len(items) - 1)
    if total_w <= max_pan_w or len(items) <= 4:
        rows = [items]
    else:
        # Split into bottom row (slightly more items) and top row
        n_bot = (len(items) + 1) // 2
        rows = [items[:n_bot], items[n_bot:]]

    curr_y = ty
    for row in rows:
        row_w = sum(2 * r for r in row) + gap * (len(row) - 1)
        ox = px - row_w / 2.0
        max_r = max(row)
        for r in row:
            if r >= 6:
                c.setFillColor(GRAY if r < 8 else colors.Color(0.55, 0.55, 0.55))
            else:
                c.setFillColor(colors.white)
            c.circle(ox + r, curr_y + r, r, stroke=1, fill=1)
            ox += 2 * r + gap
        curr_y += 2 * max_r - 0.5


def fig_balance(left, right, tilt):
    """left/right: lists of radii; tilt: +1 right side down, -1 left down, 0 level."""
    W, H = 220, 98

    def draw(c, x, y):
        cx = x + W / 2
        c.setFillColor(GRAY)
        c.ellipse(cx - 32, y, cx + 32, y + 8, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.6)
        piv = y + 34
        c.line(cx, y + 4, cx, piv)
        ang = -0.09 * tilt
        L = 80
        lx, ly = cx - L * math.cos(ang), piv - L * math.sin(ang)
        rx, ry = cx + L * math.cos(ang), piv + L * math.sin(ang)
        c.setLineWidth(2.2)
        c.line(lx, ly, rx, ry)
        c.setLineWidth(1.2)
        for px, py, items in ((lx, ly, left), (rx, ry, right)):
            ty = py + 16
            c.line(px, py, px, ty)
            c.line(px - 36, ty, px + 36, ty)
            c.line(px - 36, ty, px - 42, ty + 8)
            c.line(px + 36, ty, px + 42, ty + 8)
            _draw_pan_items(c, px, ty, items)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return W, H, draw


FRUIT_PAIRS = [
    ("orange", "oranges", "melon", "melons"),
    ("plum", "plums", "lemon", "lemons"),
    ("cherry", "cherries", "apple", "apples"),
    ("strawberry", "strawberries", "pear", "pears"),
    ("grape", "grapes", "peach", "peaches"),
    ("apricot", "apricots", "grapefruit", "grapefruits"),
]


def _make_fruit_choices(rng, ans_val, s_pl, extra_candidates=()):
    cands = {ans_val}
    for c in extra_candidates:
        if c > 0 and c != ans_val:
            cands.add(c)
    for delta in [1, -1, 2, -2, 3, -3, 4]:
        if len(cands) >= 5:
            break
        v = ans_val + delta
        if v >= 1:
            cands.add(v)
    vals = sorted(list(cands))[:5]
    ans_idx = vals.index(ans_val)
    return [f"{v} {s_pl}" for v in vals], ans_idx


def _generate_dynamic_balance_problem(rng, mode=0):
    """Procedurally generate a two-pan balance problem across 3 distinct algebraic modes."""
    s_sg, s_pl, b_sg, b_pl = rng.choice(FRUIT_PAIRS)
    r_small = 3.8
    r_big = rng.choice([7.5, 8.5])
    big_desc = "gray circles" if r_big < 8 else "big circles"

    m = mode % 3
    if m == 0:
        # Mode 0: Left plate has S small fruits, right plate has B big fruits.
        # Adding k big fruit(s) to the left plate makes the balance level.
        B = rng.choice([2, 3, 4])
        k = rng.randint(1, B - 1)
        net_b = B - k
        max_w = min(7, 14 // net_b)
        w = rng.randint(2, max(2, max_w))
        S = net_b * w

        w_chk, tilt, ans_val = solve_balance_scale(
            left_small=S, left_big=0, right_small=0, right_big=B,
            add_left_small=0, add_left_big=k, query_big_count=1,
        )
        assert w_chk == w and tilt == 1 and ans_val == w

        left_items = [r_small] * S
        right_items = [r_big] * B
        k_phrase = f"one more {b_sg}" if k == 1 else f"{k} more {b_pl}"
        b_phrase = f"1 {b_sg}" if B == 1 else f"{B} {b_pl}"
        text = (
            f"On one plate of a balance there are {S} {s_pl} (small circles) and on the other "
            f"there are {b_phrase} ({big_desc}). When we put {k_phrase} on the {s_sg} plate, "
            f"the balance is level. One {b_sg} weighs the same as:"
        )
        choices, ans_idx = _make_fruit_choices(rng, ans_val, s_pl, extra_candidates=[S, B, S // B if S >= B else 2])
        if net_b == 1:
            expl = (
                f"{S} {s_pl} + {k} {b_sg if k == 1 else b_pl} = {B} {b_pl}. "
                f"Taking {k} {b_sg if k == 1 else b_pl} off each side gives 1 {b_sg} = {w} {s_pl}."
            )
        else:
            expl = (
                f"{S} {s_pl} + {k} {b_sg if k == 1 else b_pl} = {B} {b_pl}, so {S} {s_pl} = {net_b} {b_pl}, "
                f"and 1 {b_sg} = {S} ÷ {net_b} = {w} {s_pl}."
            )
        return text, fig_balance(left_items, right_items, tilt), choices, ans_idx, expl

    elif m == 1:
        # Mode 1: Level scale with B big + S1 small on left, S2 small on right.
        # Ask how many small fruits weigh the same as Q big fruits.
        B = rng.choice([1, 2])
        w = rng.randint(3, 6 if B == 1 else 5)
        S1 = rng.randint(1, 4)
        S2 = B * w + S1
        Q = rng.choice([2, 3]) if B == 1 else rng.choice([1, 3])

        w_chk, tilt, ans_val = solve_balance_scale(
            left_small=S1, left_big=B, right_small=S2, right_big=0,
            add_left_small=0, add_left_big=0, query_big_count=Q,
        )
        assert w_chk == w and tilt == 0 and ans_val == Q * w

        left_items = [r_big] * B + [r_small] * S1
        right_items = [r_small] * S2
        b_left_str = f"1 {b_sg}" if B == 1 else f"{B} {b_pl}"
        s1_str = f"1 {s_sg}" if S1 == 1 else f"{S1} {s_pl}"
        q_str = f"1 {b_sg}" if Q == 1 else f"{Q} {b_pl}"
        text = (
            f"The balance is level. On the left plate there {'is' if B == 1 else 'are'} {b_left_str} "
            f"({'big circle' if B == 1 else big_desc}) and {s1_str}; on the right plate there are "
            f"{S2} {s_pl}. How many {s_pl} weigh the same as <b>{q_str}</b>?"
        )
        choices, ans_idx = _make_fruit_choices(rng, ans_val, s_pl, extra_candidates=[w, S2, Q * (w + 1), Q * (w - 1)])
        expl = (
            f"Take {s1_str} off each side: {b_left_str} = {S2 - S1} {s_pl}"
            + (f", so 1 {b_sg} = {w} {s_pl}" if B > 1 else "")
            + (f". Therefore {q_str} = {ans_val} {s_pl}." if Q > 1 else ".")
        )
        return text, fig_balance(left_items, right_items, tilt), choices, ans_idx, expl

    else:
        # Mode 2: Left plate has S small fruits (heavier), right plate has B big fruits.
        # Removing k small fruits from the left plate makes the balance level.
        B = rng.choice([2, 3])
        w = rng.randint(2, 4)
        k = rng.randint(1, 3)
        S = B * w + k

        w_chk, tilt, ans_val = solve_balance_scale(
            left_small=S, left_big=0, right_small=0, right_big=B,
            add_left_small=-k, add_left_big=0, query_big_count=1,
        )
        assert w_chk == w and tilt == -1 and ans_val == w

        left_items = [r_small] * S
        right_items = [r_big] * B
        k_str = f"1 {s_sg}" if k == 1 else f"{k} {s_pl}"
        text = (
            f"On the left plate of a balance there are {S} {s_pl} (small circles) and on the right "
            f"plate there are {B} {b_pl} ({big_desc}). When we take {k_str} off the left plate, "
            f"the balance becomes level. One {b_sg} weighs the same as:"
        )
        choices, ans_idx = _make_fruit_choices(rng, ans_val, s_pl, extra_candidates=[S - k, B, w + 1, w + 2])
        expl = (
            f"Removing {k_str} leaves {S - k} {s_pl} balancing {B} {b_pl}. "
            f"So 1 {b_sg} = {S - k} ÷ {B} = {w} {s_pl}."
        )
        return text, fig_balance(left_items, right_items, tilt), choices, ans_idx, expl


def q_2002_9(d, key, set_num=3, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Balance scales", "Based on 2002, Problem 9")
    if include_orig:
        w, tilt, ans_val = solve_balance_scale(6, 0, 0, 2, add_left_big=1, query_big_count=1)
        assert w == 6 and tilt == 1 and ans_val == 6
        d.problem(
            "Original 2002 #9.",
            "On one plate of a balance there are 6 oranges (small circles) and on the "
            "other there are melons (big circles). When we put one more melon, exactly like the others, on the "
            "orange plate, the balance is level. The weight of one melon is the same as:",
            fig_balance([4] * 6, [9, 9], tilt),
            "right",
            ["2 oranges", "3 oranges", "4 oranges", "5 oranges", "6 oranges"],
            3,
        )
        key.append(("2002 #9", "E", "6 oranges + 1 melon = 2 melons. Take one melon off each side: 6 oranges = 1 melon."))

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        mode = modes[(idx - 1) % len(modes)]
        text, fig, choices, ans_idx, expl = _generate_dynamic_balance_problem(rng, mode=mode)
        d.problem(f"Practice {set_num}.{idx}", text, fig, "right", choices, 3)
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_9

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
