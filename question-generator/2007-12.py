# Model: argon
"""Math Kangaroo 2007, Problem #12 - Question Generator."""
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
QUESTION_ID = (2007, 12)


def check_birthday_offset(base_date_tuple, rel, years_diff, days_diff, choices_tuples, ans_idx):
    from datetime import date, timedelta
    y, m, day = base_date_tuple
    # Shift by years first, then days
    # rel == "older": base person is older than target -> target was born LATER (+years, +days)
    # rel == "younger": base person is younger than target -> target was born EARLIER (-years, -days)
    if rel == "older":
        mid = date(y + years_diff, m, day)
        res = mid + timedelta(days=days_diff)
    else:
        mid = date(y - years_diff, m, day)
        res = mid - timedelta(days=days_diff)
    res_tuple = (res.year, res.month, res.day)
    matches = [i for i, ct in enumerate(choices_tuples) if ct == res_tuple]
    assert matches == [ans_idx], f"Birthday offset got {res_tuple}, choices={choices_tuples}, ans_idx={ans_idx}"


def q_2007_12(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Calendar & Birthday Date Reasoning", "Based on 2007, Problem 12")

    # Original 2007 #12: Basil (born Jan 1, 2002) is older than Peter by 1 year and 1 day -> Peter born Jan 2, 2003 (A)
    c_tuples0 = [(2003, 1, 2), (2001, 1, 2), (2000, 12, 31), (2002, 12, 31), (2003, 12, 31)]
    opts0 = ["January 2, 2003", "January 2, 2001", "December 31, 2000", "December 31, 2002", "December 31, 2003"]
    check_birthday_offset((2002, 1, 1), "older", 1, 1, c_tuples0, 0)
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

    practices = [
        # Practice .1: Clara (born Jan 1, 2015) is YOUNGER than Leo by 1 year and 1 day -> Leo born 1 yr 1 day BEFORE Jan 1, 2015 = Dec 31, 2013 (Answer: C)
        (
            (2015, 1, 1), "younger", 1, 1,
            [(2016, 1, 2), (2014, 1, 2), (2013, 12, 31), (2014, 12, 31), (2016, 12, 31)],
            ["January 2, 2016", "January 2, 2014", "December 31, 2013", "December 31, 2014", "December 31, 2016"],
            2,
            "Clara, who is <b>younger</b> than Leo by one year and one day, was born on January 1, 2015. "
            "What is the date of Leo's birthday?",
            "Because Clara is younger than Leo, Leo is older and was born 1 year and 1 day BEFORE Clara. "
            "One year before January 1, 2015 is January 1, 2014, and one day before that is December 31, 2013.",
        ),
        # Practice .2: Max (born Dec 31, 2010) is OLDER than Nina by 1 year and 2 days -> Nina born 1 yr 2 days AFTER Dec 31, 2010 = Jan 2, 2012 (Answer: B)
        (
            (2010, 12, 31), "older", 1, 2,
            [(2011, 1, 2), (2012, 1, 2), (2009, 12, 29), (2011, 12, 29), (2012, 1, 1)],
            ["January 2, 2011", "January 2, 2012", "December 29, 2009", "December 29, 2011", "January 1, 2012"],
            1,
            "Max, who is <b>older</b> than Nina by one year and two days, was born on December 31, 2010. "
            "What is the date of Nina's birthday?",
            "Since Max is older than Nina, Nina was born 1 year and 2 days AFTER December 31, 2010. "
            "One year later is December 31, 2011, and two days after that is January 2, 2012.",
        ),
        # Practice .3: Sophia (born May 1, 2014) is YOUNGER than Ethan by 2 years and 1 day -> Ethan born 2 yrs 1 day BEFORE May 1, 2014 = April 30, 2012 (Answer: D)
        (
            (2014, 5, 1), "younger", 2, 1,
            [(2016, 5, 2), (2012, 5, 2), (2012, 4, 31) if False else (2016, 4, 30), (2012, 4, 30), (2013, 4, 30)],
            ["May 2, 2016", "May 2, 2012", "April 30, 2016", "April 30, 2012", "April 30, 2013"],
            3,
            "Sophia, who is <b>younger</b> than Ethan by two years and one day, was born on May 1, 2014. "
            "What is the date of Ethan's birthday?",
            "Since Sophia is younger than Ethan, Ethan was born 2 years and 1 day BEFORE May 1, 2014. "
            "Two years before May 1, 2014 is May 1, 2012, and one day before May 1, 2012 is April 30, 2012.",
        ),
        # Practice .4: Lucas (born Jan 1, 2018) is OLDER than Maya by 2 years and 3 days -> Maya born Jan 4, 2020 (Answer: E)
        (
            (2018, 1, 1), "older", 2, 3,
            [(2015, 12, 29), (2016, 1, 4), (2019, 1, 4), (2020, 12, 29), (2020, 1, 4)],
            ["December 29, 2015", "January 4, 2016", "January 4, 2019", "December 29, 2020", "January 4, 2020"],
            4,
            "Lucas, who is <b>older</b> than Maya by two years and three days, was born on January 1, 2018. "
            "What is the date of Maya's birthday?",
            "Because Lucas is older, Maya was born 2 years and 3 days AFTER January 1, 2018. "
            "Two years after January 1, 2018 is January 1, 2020, and 3 days later is January 4, 2020.",
        ),
    ]

    for idx, (b_date, rel, yd, dd, c_tups, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_birthday_offset(b_date, rel, yd, dd, c_tups, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_12

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
