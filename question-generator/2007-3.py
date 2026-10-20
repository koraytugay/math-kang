# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #3 - Question Generator."""
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
QUESTION_ID = (2007, 3)


def check_common_letters(words, choices, ans_idx, mode="shared"):
    sets = [set(w.upper()) for w in words]
    if mode == "shared":
        res = sets[0].intersection(*sets[1:])
    elif mode == "union":
        res = sets[0].union(*sets[1:])
    else:
        raise ValueError(f"Unknown mode: {mode}")
    cnt = len(res)
    matches = [i for i, ch in enumerate(choices) if int(ch) == cnt]
    assert matches == [ans_idx], f"Words={words} mode={mode}: {res} ({cnt}), choices={choices}, ans_idx={ans_idx}"
    return sorted(res)


WORD_POOL = [
    "TRIANGLE", "RECTANGLE", "PENTAGON", "HEXAGON", "OCTAGON",
    "DOLPHIN", "PENGUIN", "ELEPHANT", "GIRAFFE", "CROCODILE",
    "BUTTERFLY", "DINOSAUR", "SQUIRREL", "TORTOISE", "STARFISH",
    "SEAHORSE", "BALLOON", "BANANA", "PINEAPPLE", "WATERMELON",
    "STRAWBERRY", "CHOCOLATE", "PRETZEL", "PANCAKE", "SANDWICH",
    "SUNFLOWER", "RAINBOW", "MOUNTAIN", "WATERFALL", "SNOWFLAKE",
    "TREASURE", "NOTEBOOK", "BACKPACK", "CALENDAR", "UMBRELLA",
    "AIRPLANE", "BICYCLE", "SAILBOAT", "COMPASS", "LANTERN",
]


def _generate_dynamic_word_problem(rng, mode_idx=0):
    """Procedurally generate a word-letter set problem with randomized words from WORD_POOL."""
    m = mode_idx % 3

    if m in (0, 1):
        # 2 words: how many different letters appear in BOTH words?
        while True:
            w1, w2 = rng.sample(WORD_POOL, 2)
            shared = sorted(set(w1) & set(w2))
            if 2 <= len(shared) <= 6:
                break
        words = [w1, w2]
        mode = "shared"
        cnt = len(shared)
        offset = rng.randint(0, 4)
        lo = max(1, cnt - offset)
        vals = [lo + i for i in range(5)]
        ans_idx = vals.index(cnt)
        opts = [str(v) for v in vals]
        check_common_letters(words, opts, ans_idx, mode=mode)

        s1_str = ", ".join(sorted(set(w1)))
        s2_str = ", ".join(sorted(set(w2)))
        sh_str = ", ".join(shared)
        if m == 0:
            text = f"How many different letters do the words <b>{w1}</b> and <b>{w2}</b> have in common?"
        else:
            text = f"How many different letters appear in <b>both</b> the word <b>{w1}</b> and the word <b>{w2}</b>?"
        expl = (
            f"The distinct letters of {w1} are {{{s1_str}}} and of {w2} are {{{s2_str}}}. "
            f"The letters that appear in both words are {{{sh_str}}}, giving {cnt} common letters."
        )
        return words, opts, ans_idx, mode, text, expl

    else:
        # 3 words: how many different letters appear in ALL THREE words?
        for _ in range(400):
            w1, w2, w3 = rng.sample(WORD_POOL, 3)
            shared = sorted(set(w1) & set(w2) & set(w3))
            if 1 <= len(shared) <= 4:
                words = [w1, w2, w3]
                mode = "shared"
                cnt = len(shared)
                offset = rng.randint(0, 4)
                lo = max(0, cnt - offset)
                vals = [lo + i for i in range(5)]
                ans_idx = vals.index(cnt)
                opts = [str(v) for v in vals]
                check_common_letters(words, opts, ans_idx, mode=mode)
                sh_str = ", ".join(shared)
                text = (
                    f"How many different letters appear in <b>all three</b> of the words "
                    f"<b>{w1}</b>, <b>{w2}</b>, and <b>{w3}</b>?"
                )
                expl = (
                    f"Checking which letters appear in {w1}, {w2}, and {w3}: "
                    f"only {{{sh_str}}} appear in all three words, giving {cnt} common "
                    f"{'letter' if cnt == 1 else 'letters'}."
                )
                return words, opts, ans_idx, mode, text, expl
        raise RuntimeError("Could not find 3-word intersection")


def q_2007_3(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Common Letters in Two Words", "Based on 2007, Problem 3")

    opts0 = ["1", "2", "3", "4", "5"]
    check_common_letters(["KANGAROO", "PROBLEM"], opts0, 1, mode="shared")
    if include_orig:
        d.problem(
            "Original 2007 #3.",
            "How many common letters do the words <b>KANGAROO</b> and <b>PROBLEM</b> have?",
            choices=opts0,
        )
        key.append((
            "2007 #3",
            "B",
            "The distinct letters in KANGAROO are {K, A, N, G, R, O}, and in PROBLEM are {P, R, O, B, L, E, M}. "
            "The letters that appear in both words are R and O, so they have 2 common letters.",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        words, opts, ans_idx, mode, text, expl = _generate_dynamic_word_problem(rng, mode_idx=m)
        check_common_letters(words, opts, ans_idx, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_3

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
