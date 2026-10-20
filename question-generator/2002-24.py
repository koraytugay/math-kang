# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #24 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    NUM_WORDS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 24)


def fig_odometer(num_val):
    """Draw a neat mechanical odometer display showing the digits of num_val in individual cells."""
    s_digits = str(num_val)
    n = len(s_digits)
    cell_w = 16
    cell_h = 22
    pad = 6
    w = n * cell_w + 2 * pad + 20
    h = cell_h + 2 * pad

    def draw(c, x, y):
        ox = x + pad
        oy = y + pad
        c.setFillColor(colors.Color(0.92, 0.92, 0.92))
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.2)
        c.roundRect(ox - 2, oy - 2, n * cell_w + 4, cell_h + 4, 3, stroke=1, fill=1)
        for i, ch in enumerate(s_digits):
            cx = ox + i * cell_w
            c.setFillColor(colors.white)
            c.setLineWidth(0.9)
            c.rect(cx, oy, cell_w, cell_h, stroke=1, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(cx + cell_w / 2, oy + 6, ch)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ox + n * cell_w + 5, oy + 6, "km")
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return w, h, draw


def next_distinct_digits_distance(start_num):
    assert len(set(str(start_num))) == len(str(start_num)), f"Start number {start_num} does not have distinct digits"
    n = start_num + 1
    while len(set(str(n))) != len(str(n)):
        n += 1
    return n - start_num, n


def check_odometer_distinct(start_num, choices, ans_idx):
    dist, _ = next_distinct_digits_distance(start_num)
    matches = [i for i, ch in enumerate(choices) if int(ch) == dist]
    assert matches == [ans_idx], f"Odometer start={start_num}, dist={dist}, choices={choices}, ans_idx={ans_idx}"


VEHICLES = [
    ("A car's odometer", "six"),
    ("An odometer on a bus", "six"),
    ("A delivery van's odometer", "six"),
    ("A motorcycle trip counter", "five"),
    ("A bicycle trip counter", "four"),
]


def _generate_dynamic_odometer_problem(rng, mode=0):
    """Procedurally generate a distinct-digit odometer problem where the next distinct-digit number
    is a non-trivial jump (11 to 65 km ahead).
    """
    m = mode % 3
    if m in (0, 1):
        # 6-digit odometer where tens digit rolls through 1, 2, or 3 already-used digits
        num_digits = 6
        k_run = rng.choice([1, 2, 3])  # how many consecutive tens digits are blocked by the first 4 digits
        tens_d = rng.randint(4, 8 - k_run)
        blocked_tens = [tens_d + i for i in range(1, k_run + 1)]
        avail_other = [d for d in range(1, 10) if d != tens_d and d not in blocked_tens and d != (tens_d + k_run + 1)]
        rng.shuffle(avail_other)
        prefix4 = blocked_tens + avail_other[: 4 - len(blocked_tens)]
        rng.shuffle(prefix4)
        ones_cands = [d for d in [7, 8, 9] if d not in prefix4 and d != tens_d and d != (tens_d + k_run + 1)]
        ones_d = rng.choice(ones_cands) if ones_cands else 9
        if ones_d in prefix4 or ones_d == tens_d:
            # Fallback to rejection sampling
            pass
        digits = prefix4 + [tens_d, ones_d]
        if len(set(digits)) != 6:
            # Rejection sample 6-digit distinct number with dist >= 11
            while True:
                first_d = rng.randint(1, 8)
                rest = rng.sample([d for d in range(10) if d != first_d], 5)
                digits = [first_d] + rest
                start_num = int("".join(str(d) for d in digits))
                dist, next_n = next_distinct_digits_distance(start_num)
                if 11 <= dist <= 65:
                    break
        else:
            start_num = int("".join(str(d) for d in digits))
            dist, next_n = next_distinct_digits_distance(start_num)
        veh_desc = rng.choice(["A car's odometer", "The odometer of a bus", "A delivery van's odometer"])
        len_word = "six"
    else:
        # 4-digit or 5-digit trip counter rolling over a century/decade boundary
        num_digits = rng.choice([4, 5])
        while True:
            first_d = rng.randint(1, 8)
            rest = rng.sample([d for d in range(10) if d != first_d], num_digits - 1)
            digits = [first_d] + rest
            start_num = int("".join(str(d) for d in digits))
            dist, next_n = next_distinct_digits_distance(start_num)
            if 11 <= dist <= 55:
                break
        veh_desc = "A bicycle trip counter" if num_digits == 4 else "A motorcycle trip counter"
        len_word = NUM_WORDS[num_digits]

    cands = {dist}
    to_next_ten = 10 - (start_num % 10)
    for c in [1, to_next_ten, dist - 10, dist + 10, dist + 100, dist - 1, dist + 2]:
        if len(cands) >= 5:
            break
        if c >= 1 and c != dist:
            cands.add(c)
    for d in [5, 11, 15, 21, 31, 41]:
        if len(cands) >= 5:
            break
        cands.add(d)
    vals = sorted(list(cands))[:5]
    if dist not in vals:
        vals[-1] = dist
        vals.sort()
    opts = [str(v) for v in vals]
    ans_idx = vals.index(dist)
    check_odometer_distinct(start_num, opts, ans_idx)

    next_digits_str = ", ".join(str(next_n))
    text = (
        f"{veh_desc} shows <b>{start_num}</b>, where all {len_word} digits are different. "
        f"After how many more kilometres will all {len_word} digits be different again?"
    )
    expl = (
        f"Every number between {start_num + 1} and {next_n - 1} repeats at least one digit. "
        f"The very next number with all distinct digits is {next_n} (digits {next_digits_str}). "
        f"That happens after {next_n} - {start_num} = {dist} km."
    )
    return start_num, opts, ans_idx, text, expl


def q_2002_24(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Odometer with All Different Digits", "Based on 2002, Problem 24")

    opts0 = ["1", "21", "431", "12431", "13776"]
    check_odometer_distinct(187569, opts0, 1)
    if include_orig:
        d.problem(
            "Original 2002 #24.",
            "The odometer of my car indicates 187569. All the digits of this number are different. "
            "After how many more kilometres will this happen again?",
            fig_odometer(187569),
            "right",
            choices=opts0,
        )
        key.append((
            "2002 #24",
            "B",
            "Starting from 187569, numbers 187570–187579 repeat the digit 7, and 187580–187589 repeat the digit 8. "
            "The very next number is 187590, whose digits (1, 8, 7, 5, 9, 0) are all different! "
            "That takes 187590 - 187569 = 21 km.",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        s_num, opts, ans_idx, text, expl = _generate_dynamic_odometer_problem(rng, mode=m)
        check_odometer_distinct(s_num, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_odometer(s_num),
            "right",
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_24

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
