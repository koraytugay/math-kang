# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #12 - Question Generator."""
import os
import sys
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    NUM_WORDS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2007, 12)

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def format_date_tuple(dt_tuple):
    y, m, d_num = dt_tuple
    return f"{MONTH_NAMES[m]} {d_num}, {y}"


def _shift_date(base_date_tuple, sign_y, years_diff, sign_d, days_diff):
    y, m, day = base_date_tuple
    mid = date(y + sign_y * years_diff, m, day)
    res = mid + timedelta(days=sign_d * days_diff)
    return (res.year, res.month, res.day)


def check_birthday_offset(base_date_tuple, rel, years_diff, days_diff, choices_tuples, opts_str, ans_idx):
    sign = 1 if rel == "older" else -1
    res_tuple = _shift_date(base_date_tuple, sign, years_diff, sign, days_diff)
    assert [format_date_tuple(ct) for ct in choices_tuples] == list(opts_str)
    matches = [i for i, ct in enumerate(choices_tuples) if ct == res_tuple]
    assert matches == [ans_idx], f"Birthday offset got {res_tuple}, choices={choices_tuples}, ans_idx={ans_idx}"


NAME_PAIRS = [
    ("Clara", "Leo"),
    ("Max", "Nina"),
    ("Sophia", "Ethan"),
    ("Lucas", "Maya"),
    ("Anna", "Ben"),
    ("Noah", "Elena"),
    ("Sam", "Zoe"),
    ("Iris", "Jack"),
]

BOUNDARY_MONTH_DAYS = [
    (1, 1),
    (12, 31),
    (5, 1),
    (7, 31),
    (10, 1),
    (8, 31),
]


def _generate_dynamic_birthday_problem(rng, mode_idx=0):
    """Procedurally generate a calendar birthday offset problem across month/year boundaries."""
    p1, p2 = rng.choice(NAME_PAIRS)
    rel = "older" if mode_idx % 2 == 0 else "younger"
    sign = 1 if rel == "older" else -1

    while True:
        yr = rng.randint(2008, 2020)
        m, day = rng.choice(BOUNDARY_MONTH_DAYS)
        yd = rng.choice([1, 2, 3])
        dd = rng.choice([1, 2, 3])
        if (yr, m, day, rel, yd, dd) != (2002, 1, 1, "older", 1, 1):
            break

    base_dt = (yr, m, day)
    correct_dt = _shift_date(base_dt, sign, yd, sign, dd)
    mid_dt = (yr + sign * yd, m, day)

    # Classic sign/rollover trap distractors
    trap1 = _shift_date(base_dt, -sign, yd, -sign, dd)
    trap2 = _shift_date(base_dt, sign, yd, -sign, dd)
    trap3 = _shift_date(base_dt, -sign, yd, sign, dd)
    trap4 = (correct_dt[0] + 1, correct_dt[1], correct_dt[2])
    trap5 = (correct_dt[0] - 1, correct_dt[1], correct_dt[2])

    cands = [correct_dt]
    for t in [trap1, trap2, trap3, trap4, trap5]:
        if len(cands) >= 5:
            break
        if t not in cands:
            cands.append(t)

    rng.shuffle(cands)
    ans_idx = cands.index(correct_dt)
    opts_str = [format_date_tuple(ct) for ct in cands]
    check_birthday_offset(base_dt, rel, yd, dd, cands, opts_str, ans_idx)

    y_phrase = "one year" if yd == 1 else f"{NUM_WORDS[yd]} years"
    d_phrase = "one day" if dd == 1 else f"{NUM_WORDS[dd]} days"
    dir_word = "AFTER" if rel == "older" else "BEFORE"
    opp_rel = "younger" if rel == "older" else "older"

    text = (
        f"{p1}, who is <b>{rel}</b> than {p2} by {y_phrase} and {d_phrase}, was born on "
        f"{format_date_tuple(base_dt)}. What is the date of {p2}'s birthday?"
    )
    expl = (
        f"Since {p1} is {rel} than {p2}, {p2} is {opp_rel} and was born {y_phrase} and {d_phrase} {dir_word} "
        f"{format_date_tuple(base_dt)}. Shifting by {y_phrase} gives {format_date_tuple(mid_dt)}, and "
        f"{d_phrase} {dir_word.lower()} that is {format_date_tuple(correct_dt)}."
    )
    return base_dt, rel, yd, dd, cands, opts_str, ans_idx, text, expl


def q_2007_12(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Calendar & Birthday Date Reasoning", "Based on 2007, Problem 12")

    c_tuples0 = [(2003, 1, 2), (2001, 1, 2), (2000, 12, 31), (2002, 12, 31), (2003, 12, 31)]
    opts0 = ["January 2, 2003", "January 2, 2001", "December 31, 2000", "December 31, 2002", "December 31, 2003"]
    check_birthday_offset((2002, 1, 1), "older", 1, 1, c_tuples0, opts0, 0)
    if include_orig:
        d.problem(
            "Original 2007 #12.",
            "Basil, who is older than Peter by one year and one day, was born on January 1, 2002. "
            "What is the date of Peter's birthday?",
            choices=opts0,
            choice_cols=3,
        )
        key.append((
            "2007 #12",
            "A",
            "Since Basil is older than Peter, Peter is younger and was born 1 year and 1 day AFTER Basil. "
            "One year after January 1, 2002 is January 1, 2003, and one day after that is January 2, 2003.",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2, 3]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        b_date, rel, yd, dd, c_tups, opts, ans_idx, text, expl = _generate_dynamic_birthday_problem(rng, mode_idx=m)
        check_birthday_offset(b_date, rel, yd, dd, c_tups, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_12

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
