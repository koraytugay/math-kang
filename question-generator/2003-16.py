# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #16 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2003, 16)


def total_digits_for_pages(n_pages):
    return sum(len(str(p)) for p in range(1, n_pages + 1))


def check_pages_from_digits(total_digits, choices, ans_idx):
    matching_pages = [p for p in range(1, 500) if total_digits_for_pages(p) == total_digits]
    assert len(matching_pages) == 1, f"Invalid total_digits={total_digits}: matching_pages={matching_pages}"
    ans_pages = matching_pages[0]
    matches = [i for i, ch in enumerate(choices) if int(ch) == ans_pages]
    assert matches == [ans_idx], f"Book pages={ans_pages}, choices={choices}, ans_idx={ans_idx}"


BOOK_TEMPLATES = [
    (
        "It takes exactly <b>{tot_d} digits</b> to print all the page numbers of a storybook (starting from page 1). "
        "How many pages are in the storybook?"
    ),
    (
        "All the pages of a puzzle booklet are numbered starting from 1. A total of <b>{tot_d} digits</b> are used "
        "for the page numbers. How many pages does the booklet have?"
    ),
    (
        "Leo numbered all the pages of his comic notebook starting from page 1 and wrote <b>{tot_d} digits</b> in total. "
        "How many pages did he number?"
    ),
    (
        "A magazine uses <b>{tot_d} digits</b> to number all of its pages from page 1 to the last page. "
        "How many pages are in the magazine?"
    ),
    (
        "Maya's diary has its pages numbered sequentially starting from page 1. If all the page numbers together "
        "contain <b>{tot_d} digits</b>, how many pages are in her diary?"
    ),
]


def _generate_dynamic_book_pages(rng, variant_idx=0):
    """Procedurally generate a book-page-digits problem with realistic trap distractors."""
    use_three_digit = (variant_idx % 5 == 4)

    if not use_three_digit:
        while True:
            n_pages = rng.randint(15, 88)
            if n_pages != 22:
                break
        tot_d = total_digits_for_pages(n_pages)
        rem_d = tot_d - 9
        two_digit_pages = n_pages - 9
        assert rem_d == 2 * two_digit_pages
        expl = (
            f"Pages 1 through 9 use 9 single digits, leaving {tot_d} - 9 = {rem_d} digits for the two-digit pages. "
            f"Since each two-digit page uses 2 digits, there are {rem_d} ÷ 2 = {two_digit_pages} two-digit pages. "
            f"In total, there are 9 + {two_digit_pages} = {n_pages} pages."
        )
        traps = [two_digit_pages, tot_d // 2, n_pages - 3, n_pages + 4, rem_d]
    else:
        n_pages = rng.randint(102, 128)
        tot_d = total_digits_for_pages(n_pages)
        rem_3 = tot_d - 189
        three_digit_pages = n_pages - 99
        assert rem_3 == 3 * three_digit_pages
        expl = (
            f"Pages 1–9 use 9 digits and pages 10–99 use 90 × 2 = 180 digits (189 digits in total for pages 1–99). "
            f"That leaves {tot_d} - 189 = {rem_3} digits for three-digit pages, or {rem_3} ÷ 3 = {three_digit_pages} "
            f"three-digit pages. Altogether, the book has 99 + {three_digit_pages} = {n_pages} pages."
        )
        traps = [90 + three_digit_pages, n_pages - 9, n_pages + 3, n_pages - 3, (tot_d - 9) // 2]

    cands = {n_pages}
    for t in traps:
        if len(cands) >= 5:
            break
        if t >= 10 and t != n_pages:
            cands.add(t)
    for delta in [-2, 2, -5, 5, -7, 7]:
        if len(cands) >= 5:
            break
        v = n_pages + delta
        if v >= 10:
            cands.add(v)

    vals = sorted(list(cands))[:5]
    if n_pages not in vals:
        vals[-1] = n_pages
        vals.sort()
    opts = [str(v) for v in vals]
    ans_idx = vals.index(n_pages)
    text = BOOK_TEMPLATES[variant_idx % len(BOOK_TEMPLATES)].format(tot_d=tot_d)
    check_pages_from_digits(tot_d, opts, ans_idx)
    return tot_d, opts, ans_idx, text, expl


def q_2003_16(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Counting Digits in Book Page Numbers", "Based on 2003, Problem 16")

    opts0 = ["12", "15", "22", "28", "35"]
    check_pages_from_digits(35, opts0, 2)
    if include_orig:
        d.problem(
            "Original 2003 #16.",
            "The number of digits used to write all the page numbers in a book is 35. "
            "How many pages is the book in total?",
            choices=opts0,
        )
        key.append((
            "2003 #16",
            "C",
            "Pages 1 through 9 use 9 single digits, leaving 35 - 9 = 26 digits for the two-digit pages. "
            "Since each two-digit page uses 2 digits, there are 26 ÷ 2 = 13 two-digit pages. "
            "In total, the book has 9 + 13 = 22 pages.",
        ))

    rng = random.Random(seed)
    v_order = list(range(5))
    rng.shuffle(v_order)
    for idx in range(1, num_practice + 1):
        tot_d, opts, ans_idx, text, expl = _generate_dynamic_book_pages(
            rng, variant_idx=v_order[(idx - 1) % len(v_order)]
        )
        check_pages_from_digits(tot_d, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_16

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
