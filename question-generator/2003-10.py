# Model: argon
"""Math Kangaroo 2003, Problem #10 - Question Generator."""
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
QUESTION_ID = (2003, 10)


def check_metric_jump(dm_val, cm_val, mm_val, add_cm, choices_cm, ans_idx):
    assert mm_val % 10 == 0
    total_cm = dm_val * 10 + cm_val + (mm_val // 10) + add_cm
    matches = [i for i, c_cm in enumerate(choices_cm) if c_cm == total_cm]
    assert matches == [ans_idx], f"Metric jump total_cm={total_cm}, choices_cm={choices_cm}, ans_idx={ans_idx}"


def q_2003_10(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Metric Length Conversion (m, dm, cm, mm)", "Based on 2003, Problem 10")

    # Original 2003 #10: 50 dm + 50 cm + 50 mm + 123 cm = 500 + 50 + 5 + 123 = 678 cm = 6 m 78 cm (A)
    check_metric_jump(50, 50, 50, 123, [678, 573, 555, 1128, 723], 0)
    if include_orig:
        d.problem(
            "Original 2003 #10.",
            "Jumpy the kangaroo has been training for the Animal Olympics. His longest jump during the training was "
            "50 dm 50 cm and 50 mm long. He won the gold medal at the end of the Olympics with a jump that was "
            "123 cm longer. How long was Jumpy's winning jump?",
            choices=["6 m 78 cm", "5 m 73 cm", "5 m 55 cm", "11 m 28 cm", "7 m 23 cm"],
            choice_cols=3,
        )
        key.append((
            "2003 #10",
            "A",
            "Convert each part of the training jump to centimetres: 50 dm = 500 cm, 50 cm = 50 cm, and 50 mm = 5 cm. "
            "So the training jump was 500 + 50 + 5 = 555 cm. Adding 123 cm gives 555 + 123 = 678 cm, which is 6 m 78 cm.",
        ))

    practices = [
        # Practice .1: 40 dm + 40 cm + 40 mm + 135 cm = 400 + 40 + 4 + 135 = 579 cm = 5 m 79 cm (Answer: B)
        (
            40, 40, 40, 135,
            [444, 579, 539, 615, 975],
            ["4 m 44 cm", "5 m 79 cm", "5 m 39 cm", "6 m 15 cm", "9 m 75 cm"],
            1,
            "Hoppy the frog's practice jump was 40 dm, 40 cm, and 40 mm long. In the final round, he jumped "
            "135 cm farther than his practice jump. How long was Hoppy's final jump?",
            "Convert the practice jump to centimetres: 40 dm = 400 cm, 40 cm = 40 cm, and 40 mm = 4 cm, "
            "giving 400 + 40 + 4 = 444 cm. Adding 135 cm gives 444 + 135 = 579 cm = 5 m 79 cm.",
        ),
        # Practice .2: 30 dm + 70 cm + 80 mm + 114 cm = 300 + 70 + 8 + 114 = 492 cm = 4 m 92 cm (Answer: C)
        (
            30, 70, 80, 114,
            [378, 484, 492, 564, 1164],
            ["3 m 78 cm", "4 m 84 cm", "4 m 92 cm", "5 m 64 cm", "11 m 64 cm"],
            2,
            "An athlete threw a javelin 30 dm, 70 cm, and 80 mm on her first try. Her second throw was 114 cm longer "
            "than her first throw. How long was her second throw?",
            "In centimetres, 30 dm = 300 cm, 70 cm = 70 cm, and 80 mm = 8 cm, so the first throw was 300 + 70 + 8 = 378 cm. "
            "Adding 114 cm gives 378 + 114 = 492 cm, which is 4 m 92 cm.",
        ),
        # Practice .3: 60 dm + 30 cm + 90 mm + 145 cm = 600 + 30 + 9 + 145 = 784 cm = 7 m 84 cm (Answer: D)
        (
            60, 30, 90, 145,
            [639, 735, 775, 784, 865],
            ["6 m 39 cm", "7 m 35 cm", "7 m 75 cm", "7 m 84 cm", "8 m 65 cm"],
            3,
            "A paper airplane flew 60 dm, 30 cm, and 90 mm on its first flight. On its second flight, the wind helped "
            "it fly 145 cm farther. What was the total distance of the second flight?",
            "Converting to centimetres: 60 dm = 600 cm, 30 cm = 30 cm, and 90 mm = 9 cm, for a first flight of "
            "600 + 30 + 9 = 639 cm. Adding 145 cm gives 639 + 145 = 784 cm = 7 m 84 cm.",
        ),
        # Practice .4: 20 dm + 80 cm + 60 mm - 45 cm = 200 + 80 + 6 - 45 = 241 cm = 2 m 41 cm (Answer: E)
        (
            20, 80, 60, -45,
            [286, 331, 295, 235, 241],
            ["2 m 86 cm", "3 m 31 cm", "2 m 95 cm", "2 m 35 cm", "2 m 41 cm"],
            4,
            "A wooden board is 20 dm, 80 cm, and 60 mm long. A carpenter saws off a piece that is 45 cm long. "
            "How long is the remaining board?",
            "Convert the initial length to centimetres: 20 dm = 200 cm, 80 cm = 80 cm, and 60 mm = 6 cm, "
            "totaling 200 + 80 + 6 = 286 cm. Subtracting 45 cm leaves 286 - 45 = 241 cm = 2 m 41 cm.",
        ),
    ]

    for idx, (dm_v, cm_v, mm_v, add_v, ch_cm, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_metric_jump(dm_v, cm_v, mm_v, add_v, ch_cm, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2003_10

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
