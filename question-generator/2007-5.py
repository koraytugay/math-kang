# Model: argon
"""Math Kangaroo 2007, Problem #5 - Question Generator."""
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

    return w, h, draw


def q_2007_5(d, key, set_num=1, include_orig=True, num_practice=3):
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

    practices = [
        # Practice .1: ((? + 3) × 2) - 5 = 13 -> ? = 6 (Answer: C)
        (
            [("+", 3), ("×", 2), ("-", 5)],
            13,
            ["4", "5", "6", "7", "8"],
            2,
            "Leo wrote his secret number in the dark cloud and followed the arrow calculations shown "
            "in the diagram to get <b>13</b> in the last cloud. What is Leo's secret number?",
            "Working backwards from 13: before - 5 the number was 13 + 5 = 18; before × 2 it was 18 ÷ 2 = 9; "
            "and before + 3 it was 9 - 3 = 6.",
        ),
        # Practice .2: ((? × 3) - 4) ÷ 2 = 7 -> ? = 6 (Answer: B)
        (
            [("×", 3), ("-", 4), ("÷", 2)],
            7,
            ["4", "6", "7", "8", "10"],
            1,
            "Maya wrote her favourite number in the dark cloud and performed the three steps in the diagram "
            "to reach <b>7</b>. What number did Maya write in the dark cloud?",
            "Working backwards from 7: before ÷ 2 the number was 7 × 2 = 14; before - 4 it was 14 + 4 = 18; "
            "and before × 3 it was 18 ÷ 3 = 6.",
        ),
        # Practice .3: ((? - 5) × 4) + 6 = 22 -> ? = 9 (Answer: D)
        (
            [("-", 5), ("×", 4), ("+", 6)],
            22,
            ["6", "7", "8", "9", "11"],
            3,
            "Noah wrote a number in the dark cloud and calculated step by step along the arrows to get <b>22</b> "
            "at the end. Which number did Noah start with?",
            "Working backwards from 22: before + 6 the number was 22 - 6 = 16; before × 4 it was 16 ÷ 4 = 4; "
            "and before - 5 it was 4 + 5 = 9.",
        ),
        # Practice .4: ((? + 6) ÷ 4) × 5 = 15 -> ? = 6 (Answer: A)
        (
            [("+", 6), ("÷", 4), ("×", 5)],
            15,
            ["6", "8", "10", "12", "14"],
            0,
            "Sofia wrote a number in the dark cloud and followed the sequence of calculations in the diagram "
            "to end up with <b>15</b>. What number did Sofia write in the dark cloud?",
            "Working backwards from 15: before × 5 the number was 15 ÷ 5 = 3; before ÷ 4 it was 3 × 4 = 12; "
            "and before + 6 it was 12 - 6 = 6.",
        ),
    ]

    for idx, (ops, end_val, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
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
