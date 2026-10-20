# Model: argon
"""Math Kangaroo 2002, Problem #10 - Question Generator."""
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
QUESTION_ID = (2002, 10)


def fig_house_street(first_num, second_num, last_num, target_digit):
    """Draw a compact row of three little houses showing the numbering range first_num, second_num, ..., last_num."""
    w = 136
    h = 46

    def draw_house(c, hx, hy, label):
        bw, bh = 28, 22
        roof_h = 12
        # House body
        c.setFillColor(colors.Color(0.93, 0.93, 0.93))
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.1)
        c.rect(hx, hy, bw, bh, stroke=1, fill=1)
        # Roof triangle
        p = c.beginPath()
        p.moveTo(hx - 3, hy + bh)
        p.lineTo(hx + bw / 2, hy + bh + roof_h)
        p.lineTo(hx + bw + 3, hy + bh)
        p.close()
        c.setFillColor(colors.Color(0.78, 0.78, 0.78))
        c.drawPath(p, stroke=1, fill=1)
        # Number plaque inside house
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(hx + bw / 2, hy + 7, str(label))

    def draw(c, x, y):
        by = y + 6
        draw_house(c, x + 4, by, first_num)
        draw_house(c, x + 40, by, second_num)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 83, by + 9, "...")
        draw_house(c, x + 98, by, last_num)
        # Ground line
        c.setLineWidth(0.9)
        c.setStrokeColor(colors.black)
        c.line(x, by, x + w - 4, by)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_digit_occurrences(start_num, end_num, digit, choices, answer_idx, mode="occurrences"):
    d_str = str(digit)
    if mode == "occurrences":
        val = sum(str(n).count(d_str) for n in range(start_num, end_num + 1))
    elif mode == "houses_with_digit":
        val = sum(1 for n in range(start_num, end_num + 1) if d_str in str(n))
    else:
        raise ValueError(f"Unknown mode: {mode}")
    assert choices[answer_idx] == val, f"Expected {val} at index {answer_idx}, got {choices[answer_idx]}"
    matches = [i for i, ch in enumerate(choices) if ch == val]
    assert matches == [answer_idx], f"Expected unique match at {answer_idx}, got {matches}"


def q_2002_10(d, key, set_num=1, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #10 - Digit Occurrences in House Numbers",
        "Counting how many times a digit appears across a sequential range of numbers",
    )

    if include_orig:
        opts0 = [2, 4, 8, 16, 32]
        check_digit_occurrences(1, 24, 2, opts0, 2)
        d.problem(
            "2002 #10",
            "Joseph lives on a short street where the houses are numbered sequentially from 1 to 24. "
            "How many times does the digit 2 occur in the numbers of those houses?",
            fig_house_street(1, 2, 24, 2),
            "right",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2002 #10",
            "C",
            "List the house numbers from 1 to 24 that contain the digit 2: "
            "2, 12, 20, 21, 22, 23, and 24. Notice that house number 22 contains two 2s! "
            "Counting every digit 2 gives 1 + 1 + 1 + 1 + 2 + 1 + 1 = 8 times.",
        ))

    practices = [
        # Practice .1 (Answer: A) 10)
        (
            1, 35, 3, [10, 8, 9, 11, 12], 0, "occurrences",
            "Sophia lives on Maple Street where the houses are numbered sequentially from 1 to 35. "
            "How many times does the digit 3 occur in the numbers of those houses?",
            "In the ones place, the digit 3 appears in 3, 13, 23, and 33 (4 times). "
            "In the tens place, the digit 3 appears in 30, 31, 32, 33, 34, and 35 (6 times). "
            "In total, the digit 3 occurs 4 + 6 = 10 times (counting both 3s in 33).",
        ),
        # Practice .2 (Answer: B) 7)
        (
            1, 42, 4, [6, 7, 8, 9, 14], 1, "occurrences",
            "A puzzle booklet has its pages numbered sequentially from 1 to 42. "
            "How many times does the digit 4 occur in the page numbers?",
            "In the ones place, the digit 4 appears in 4, 14, 24, and 34 (4 times). "
            "In the tens place, the digit 4 appears in 40, 41, and 42 (3 times). "
            "In total, the digit 4 occurs 4 + 3 = 7 times.",
        ),
        # Practice .3 (Answer: D) 13)
        (
            1, 29, 1, [11, 12, 14, 13, 15], 3, "occurrences",
            "The lockers in a school hallway are numbered sequentially from 1 to 29. "
            "How many times does the digit 1 occur in the numbers of those lockers?",
            "In the ones place, the digit 1 appears in 1, 11, and 21 (3 times). "
            "In the tens place, the digit 1 appears in all ten numbers from 10 to 19 (10 times). "
            "In total, the digit 1 occurs 3 + 10 = 13 times (with 11 contributing two 1s).",
        ),
        # Practice .4 (Answer: E) 12)
        (
            10, 30, 2, [9, 10, 11, 13, 12], 4, "occurrences",
            "The seats in a theater row are numbered sequentially from 10 to 30. "
            "How many times does the digit 2 occur in the numbers of those seats?",
            "Between 10 and 30, the digit 2 appears in the ones place in 12 and 22 (2 times), "
            "and in the tens place in every number from 20 to 29 (10 times). "
            "In total, the digit 2 occurs 2 + 10 = 12 times.",
        ),
        # Practice .5 (Answer: A) 12)
        (
            1, 55, 5, [12, 10, 11, 13, 15], 0, "occurrences",
            "Noah paints house numbers on all the doors along Oak Avenue, numbered sequentially from 1 to 55. "
            "How many times does Noah paint the digit 5?",
            "In the ones place, the digit 5 appears in 5, 15, 25, 35, 45, and 55 (6 times). "
            "In the tens place, the digit 5 appears in 50, 51, 52, 53, 54, and 55 (6 times). "
            "Altogether, Noah paints the digit 5 a total of 6 + 6 = 12 times.",
        ),
    ]

    for idx, (s_num, e_num, dig, opts, ans_idx, mode, text, expl) in enumerate(practices[:num_practice], start=1):
        check_digit_occurrences(s_num, e_num, dig, opts, ans_idx, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_house_street(s_num, s_num + 1, e_num, dig),
            "right",
            opts,
            choice_cols=5,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_10

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
