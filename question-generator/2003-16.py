# Model: argon
"""Math Kangaroo 2003, Problem #16 - Question Generator."""
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
QUESTION_ID = (2003, 16)


def total_digits_for_pages(n_pages):
    return sum(len(str(p)) for p in range(1, n_pages + 1))


def check_pages_from_digits(total_digits, choices, ans_idx):
    matching_pages = [p for p in range(1, 500) if total_digits_for_pages(p) == total_digits]
    assert len(matching_pages) == 1, f"Invalid total_digits={total_digits}: matching_pages={matching_pages}"
    ans_pages = matching_pages[0]
    matches = [i for i, ch in enumerate(choices) if int(ch) == ans_pages]
    assert matches == [ans_idx], f"Book pages={ans_pages}, choices={choices}, ans_idx={ans_idx}"


def q_2003_16(d, key, set_num=1, include_orig=True, num_practice=3):
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

    practices = [
        # Practice .1: 49 digits -> 9 + 2*(N-9) = 49 -> 2*(N-9)=40 -> N-9=20 -> N = 29 pages (Answer: D)
        (
            49,
            ["20", "24", "25", "29", "40"],
            3,
            "It takes exactly <b>49 digits</b> to print all the page numbers of a storybook (starting from page 1). "
            "How many pages are in the storybook?",
            "Pages 1 to 9 take 9 digits, leaving 49 - 9 = 40 digits. Each two-digit page takes 2 digits, "
            "which gives 40 ÷ 2 = 20 two-digit pages. Adding the 9 single-digit pages gives 9 + 20 = 29 pages.",
        ),
        # Practice .2: 63 digits -> 9 + 2*(N-9) = 63 -> 2*(N-9)=54 -> N-9=27 -> N = 36 pages (Answer: B)
        (
            63,
            ["31", "36", "38", "42", "54"],
            1,
            "All the pages of a puzzle booklet are numbered starting from 1. A total of <b>63 digits</b> are used "
            "for the page numbers. How many pages does the booklet have?",
            "Subtracting the 9 digits used for pages 1–9 leaves 63 - 9 = 54 digits. "
            "Those 54 digits form 54 ÷ 2 = 27 two-digit page numbers (pages 10 to 36). "
            "So the booklet has 9 + 27 = 36 pages.",
        ),
        # Practice .3: 27 digits -> 9 + 2*(N-9) = 27 -> 2*(N-9)=18 -> N-9=9 -> N = 18 pages (Answer: A)
        (
            27,
            ["18", "19", "21", "23", "27"],
            0,
            "Leo numbered all the pages of his comic notebook starting from page 1 and wrote <b>27 digits</b> in total. "
            "How many pages did he number?",
            "Pages 1 to 9 use 9 digits, leaving 27 - 9 = 18 digits for two-digit pages. "
            "That gives 18 ÷ 2 = 9 two-digit pages, so there are 9 + 9 = 18 pages in total.",
        ),
        # Practice .4: 85 digits -> 9 + 2*(N-9) = 85 -> 2*(N-9)=76 -> N-9=38 -> N = 47 pages (Answer: E)
        (
            85,
            ["38", "42", "44", "45", "47"],
            4,
            "A magazine uses <b>85 digits</b> to number all of its pages from page 1 to the last page. "
            "How many pages are in the magazine?",
            "Pages 1 to 9 use 9 digits, leaving 85 - 9 = 76 digits. Dividing by 2 digits per page gives "
            "76 ÷ 2 = 38 two-digit pages. In total, there are 9 + 38 = 47 pages.",
        ),
    ]

    for idx, (tot_d, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_pages_from_digits(tot_d, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2003_16

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
