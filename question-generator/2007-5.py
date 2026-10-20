# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #5 - Question Generator."""
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
QUESTION_ID = (2007, 5)


def eval_cloud_chain(start_val, ops):
    val = start_val
    for op, k in ops:
        if op == "+":
            val += k
        elif op == "-":
            val -= k
        elif op in ("×", "*"):
            val *= k
        elif op in ("÷", ":", "/"):
            if val % k != 0:
                return None
            val //= k
        else:
            raise ValueError(f"Unknown op: {op}")
    return val


def check_cloud_chain(ops, end_val, choices, ans_idx):
    matches = []
    for i, ch in enumerate(choices):
        out = eval_cloud_chain(int(ch), ops)
        if out == end_val:
            matches.append(i)
    assert matches == [ans_idx], f"Cloud chain check failed: ops={ops}, end_val={end_val}, matches={matches} vs {ans_idx}"


def _draw_cloud(c, cx, cy, cw, ch, fill_color):
    """Draw a fluffy cloud centered at (cx, cy) with width cw and height ch."""
    bumps = [
        (0.0, 0.0, 0.34, 0.34),
        (-0.27, -0.04, 0.23, 0.27),
        (0.27, -0.04, 0.23, 0.27),
        (-0.14, 0.14, 0.23, 0.26),
        (0.14, 0.14, 0.23, 0.26),
        (-0.13, -0.14, 0.24, 0.24),
        (0.13, -0.14, 0.24, 0.24),
    ]
    c.setFillColor(colors.black)
    for dx, dy, rx, ry in bumps:
        c.ellipse(
            cx + dx * cw - rx * cw - 1.3,
            cy + dy * ch - ry * ch - 1.3,
            cx + dx * cw + rx * cw + 1.3,
            cy + dy * ch + ry * ch + 1.3,
            stroke=0,
            fill=1,
        )
    c.setFillColor(fill_color)
    for dx, dy, rx, ry in bumps:
        c.ellipse(
            cx + dx * cw - rx * cw,
            cy + dy * ch - ry * ch,
            cx + dx * cw + rx * cw,
            cy + dy * ch + ry * ch,
            stroke=0,
            fill=1,
        )


def fig_cloud_chain(ops, end_val):
    """Draw N+1 clouds connected by N operation arrows from left to right."""
    n_clouds = len(ops) + 1
    cw, ch = 58, 30
    arrow_w = 50
    w = n_clouds * cw + len(ops) * arrow_w + 8
    h = 42

    def draw(c, x, y):
        cy = y + h / 2 - 2
        for i in range(n_clouds):
            cx = x + 4 + cw / 2 + i * (cw + arrow_w)
            is_first = i == 0
            is_last = i == n_clouds - 1
            fill_col = colors.Color(0.28, 0.28, 0.28) if is_first else colors.white
            _draw_cloud(c, cx, cy, cw, ch, fill_col)
            if is_first:
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 11)
                c.drawCentredString(cx, cy - 4, "?")
            elif is_last:
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(cx, cy - 4.5, str(end_val))

            if i < len(ops):
                op_sym, k = ops[i]
                ax0 = cx + cw * 0.50 + 2
                ax1 = cx + cw + arrow_w - cw * 0.50 - 2
                c.setStrokeColor(colors.black)
                c.setFillColor(colors.black)
                c.setLineWidth(1.4)
                c.line(ax0, cy, ax1, cy)
                p = c.beginPath()
                p.moveTo(ax1, cy)
                p.lineTo(ax1 - 6.5, cy + 3.4)
                p.lineTo(ax1 - 6.5, cy - 3.4)
                p.close()
                c.drawPath(p, stroke=0, fill=1)
                c.setFont("Helvetica-Bold", 10.5)
                c.drawCentredString((ax0 + ax1) / 2, cy + 6.5, f"{op_sym} {k}")

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


NAMES = ["Leo", "Maya", "Noah", "Sofia", "Clara", "Sam", "Elena", "Max"]
INV_OP = {"+": "-", "-": "+", "×": "÷", "÷": "×"}


def _generate_dynamic_cloud_problem(rng):
    """Procedurally generate a 3-step cloud number chain problem."""
    actor = rng.choice(NAMES)
    for _ in range(400):
        start_val = rng.randint(3, 15)
        op_types = rng.sample(["+", "-", "×", "÷"], 3)
        if not ({"×", "÷"} & set(op_types)):
            continue
        vals = [start_val]
        ops = []
        ok = True
        for op in op_types:
            cur = vals[-1]
            if op == "+":
                k = rng.randint(2, 9)
                nxt = cur + k
            elif op == "-":
                if cur <= 3:
                    ok = False
                    break
                k = rng.randint(2, min(9, cur - 2))
                nxt = cur - k
            elif op == "×":
                if cur > 18:
                    ok = False
                    break
                k = rng.randint(2, 4 if cur <= 12 else 3)
                nxt = cur * k
            else:
                divs = [d for d in range(2, 7) if cur % d == 0 and cur // d >= 2]
                if not divs:
                    ok = False
                    break
                k = rng.choice(divs)
                nxt = cur // k
            ops.append((op, k))
            vals.append(nxt)
        if not ok:
            continue
        end_val = vals[-1]
        if (ops, end_val) == ([("-", 2), (":", 3), ("+", 4)], 5):
            continue

        offset = rng.randint(0, 4)
        step = rng.choice([1, 2])
        lo = max(1, start_val - offset * step)
        ch_vals = [lo + i * step for i in range(5)]
        if start_val not in ch_vals:
            ch_vals[offset] = start_val
            ch_vals.sort()
        opts = [str(v) for v in ch_vals]
        ans_idx = ch_vals.index(start_val)
        check_cloud_chain(ops, end_val, opts, ans_idx)

        rev_steps = []
        for i in range(2, -1, -1):
            op, k = ops[i]
            inv = INV_OP[op]
            rev_steps.append(f"before {op} {k} the number was {vals[i + 1]} {inv} {k} = {vals[i]}")
        text = (
            f"{actor} wrote a secret number in the dark cloud and followed the arrow calculations shown "
            f"in the diagram to get <b>{end_val}</b> in the last cloud. What number did {actor} write in the dark cloud?"
        )
        expl = f"Working backwards from {end_val}: {'; '.join(rev_steps)}."
        return ops, end_val, opts, ans_idx, text, expl

    raise RuntimeError("Failed to generate cloud chain problem")


def q_2007_5(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Number Chain in the Clouds", "Based on 2007, Problem 5")

    orig_ops = [("-", 2), (":", 3), ("+", 4)]
    orig_opts = ["1", "3", "5", "7", "9"]
    check_cloud_chain(orig_ops, 5, orig_opts, 2)
    if include_orig:
        d.problem(
            "Original 2007 #5.",
            "Emma wrote her favourite number in the dark cloud and performed correctly several "
            "calculations following the sequence in the diagram. What is Emma's favourite number?",
            fig_cloud_chain(orig_ops, 5),
            "below",
            choices=orig_opts,
        )
        key.append((
            "2007 #5",
            "C",
            "Work backwards from the last cloud (5): before + 4 the number was 5 - 4 = 1; "
            "before ÷ 3 it was 1 × 3 = 3; and before - 2 it was 3 + 2 = 5.",
        ))

    rng = random.Random(seed)
    for idx in range(1, num_practice + 1):
        ops, end_val, opts, ans_idx, text, expl = _generate_dynamic_cloud_problem(rng)
        check_cloud_chain(ops, end_val, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_cloud_chain(ops, end_val),
            "below",
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_5

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
