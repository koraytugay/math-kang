# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #10 - Question Generator."""
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
        c.setLineWidth(1)

    return w, h, draw


def solve_digit_occurrences(start_num, end_num, digit, mode="occurrences"):
    d_str = str(digit)
    if mode == "occurrences":
        return sum(str(n).count(d_str) for n in range(start_num, end_num + 1))
    elif mode == "houses_with_digit":
        return sum(1 for n in range(start_num, end_num + 1) if d_str in str(n))
    raise ValueError(f"Unknown mode: {mode}")


def check_digit_occurrences(start_num, end_num, digit, choices, answer_idx, mode="occurrences"):
    val = solve_digit_occurrences(start_num, end_num, digit, mode=mode)
    assert choices[answer_idx] == val, f"Expected {val} at index {answer_idx}, got {choices[answer_idx]}"
    matches = [i for i, ch in enumerate(choices) if ch == val]
    assert matches == [answer_idx], f"Expected unique match at {answer_idx}, got {matches}"


STORY_TEMPLATES = [
    (
        "Sophia lives on Maple Street where the houses are numbered sequentially from {s} to {e}. "
        "How many times does the digit {d} occur in the numbers of those houses?",
        "houses",
    ),
    (
        "A puzzle booklet has its pages numbered sequentially from {s} to {e}. "
        "How many times does the digit {d} occur in the page numbers?",
        "pages",
    ),
    (
        "The lockers in a school hallway are numbered sequentially from {s} to {e}. "
        "How many times does the digit {d} occur in the numbers of those lockers?",
        "lockers",
    ),
    (
        "The seats in a theater row are numbered sequentially from {s} to {e}. "
        "How many times does the digit {d} occur in the numbers of those seats?",
        "seats",
    ),
    (
        "Noah paints house numbers on all the doors along Oak Avenue, numbered sequentially from {s} to {e}. "
        "How many times does Noah paint the digit {d}?",
        "doors",
    ),
]


def _generate_dynamic_digit_problem(rng, variant_idx=0):
    """Procedurally generate a sequential digit-counting problem with exact place-value explanation."""
    digit = rng.randint(1, 8)
    start_num = 1 if rng.random() < 0.75 else rng.choice([10, 11, 15])

    # Pick end_num so that the double-digit number (11 * digit) is usually inside the range!
    min_end = max(start_num + 15, 10 * digit + 2)
    max_end = min(98, max(min_end + 12, 10 * digit + 25))
    end_num = rng.randint(min_end, max_end)

    d_str = str(digit)
    use_item_count = (variant_idx % 4 == 3)
    mode = "houses_with_digit" if use_item_count else "occurrences"
    ans_val = solve_digit_occurrences(start_num, end_num, digit, mode=mode)
    other_val = solve_digit_occurrences(
        start_num, end_num, digit, mode="occurrences" if use_item_count else "houses_with_digit"
    )

    ones_nums = [n for n in range(start_num, end_num + 1) if n % 10 == digit]
    tens_nums = [n for n in range(start_num, end_num + 1) if (n // 10) % 10 == digit]
    matching_nums = [n for n in range(start_num, end_num + 1) if d_str in str(n)]

    if use_item_count:
        noun = rng.choice(["houses", "lockers", "doors", "pages"])
        text = (
            f"Along Cedar Lane, the {noun} are numbered sequentially from {start_num} to {end_num}. "
            f"How many of those {noun} have the digit {digit} in their number (at least once)?"
        )
        nums_str = ", ".join(str(n) for n in matching_nums)
        expl = (
            f"The numbers from {start_num} to {end_num} that contain the digit {digit} are: "
            f"{nums_str}. Counting each number once (even {11 * digit} if present) gives {ans_val} {noun}."
        )
    else:
        tmpl, _ = STORY_TEMPLATES[variant_idx % len(STORY_TEMPLATES)]
        text = tmpl.format(s=start_num, e=end_num, d=digit)
        ones_str = ", ".join(str(n) for n in ones_nums)
        tens_str = (
            f"{tens_nums[0]} through {tens_nums[-1]}"
            if len(tens_nums) >= 4
            else ", ".join(str(n) for n in tens_nums)
        )
        expl = (
            f"In the ones place, the digit {digit} appears in {ones_str} ({len(ones_nums)} times). "
            + (
                f"In the tens place, the digit {digit} appears in {tens_str} ({len(tens_nums)} times). "
                if tens_nums
                else "It never appears in the tens place. "
            )
            + f"In total, the digit {digit} occurs {len(ones_nums)} + {len(tens_nums)} = {ans_val} times"
            + (f" (counting both {digit}s in {11 * digit})." if (11 * digit) in matching_nums else ".")
        )

    cands = {ans_val}
    if other_val > 0 and other_val != ans_val:
        cands.add(other_val)
    for delta in [-1, 1, -2, 2, 3, -3, 4]:
        if len(cands) >= 5:
            break
        v = ans_val + delta
        if v >= 1:
            cands.add(v)
    opts = list(cands)[:5]
    rng.shuffle(opts)
    ans_idx = opts.index(ans_val)
    check_digit_occurrences(start_num, end_num, digit, opts, ans_idx, mode=mode)
    return start_num, end_num, digit, opts, ans_idx, mode, text, expl


def q_2002_10(d, key, set_num=1, include_orig=True, num_practice=5, seed=None):
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

    rng = random.Random(seed)
    for idx in range(1, num_practice + 1):
        s_num, e_num, dig, opts, ans_idx, mode, text, expl = _generate_dynamic_digit_problem(
            rng, variant_idx=idx - 1
        )
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
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
