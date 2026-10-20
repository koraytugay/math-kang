# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2003, Problem #10 - Question Generator."""
import os
import sys
import re
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2003, 10)


def format_m_cm(total_cm):
    m = total_cm // 100
    cm = total_cm % 100
    return f"{m} m {cm} cm"


def parse_m_cm(s):
    m_obj = re.fullmatch(r"\s*(\d+)\s*m\s*(\d+)\s*cm\s*", s)
    assert m_obj is not None, f"Invalid m/cm choice format: {s!r}"
    m_val, cm_val = int(m_obj.group(1)), int(m_obj.group(2))
    assert 0 <= cm_val < 100, f"cm part out of range [0, 99]: {s!r}"
    return m_val * 100 + cm_val


def check_metric_jump(dm_val, cm_val, mm_val, add_cm, choices_cm, opts_str, ans_idx):
    assert mm_val % 10 == 0
    total_cm = dm_val * 10 + cm_val + (mm_val // 10) + add_cm
    parsed_cm = [parse_m_cm(s) for s in opts_str]
    assert parsed_cm == list(choices_cm), f"String choices {opts_str} != {choices_cm}"
    matches = [i for i, c_cm in enumerate(choices_cm) if c_cm == total_cm]
    assert matches == [ans_idx], f"Metric jump total_cm={total_cm}, choices_cm={choices_cm}, ans_idx={ans_idx}"


ADD_STORIES = [
    (
        "Hoppy the frog's practice jump was {dm} dm, {cm} cm, and {mm} mm long. In the final round, he jumped "
        "{add} cm farther than his practice jump. How long was Hoppy's final jump?",
        "practice jump",
        "final jump",
    ),
    (
        "An athlete threw a javelin {dm} dm, {cm} cm, and {mm} mm on her first try. Her second throw was {add} cm longer "
        "than her first throw. How long was her second throw?",
        "first throw",
        "second throw",
    ),
    (
        "A paper airplane flew {dm} dm, {cm} cm, and {mm} mm on its first flight. On its second flight, the wind helped "
        "it fly {add} cm farther. What was the total distance of the second flight?",
        "first flight",
        "second flight",
    ),
    (
        "Leo's toy car rolled {dm} dm, {cm} cm, and {mm} mm down a ramp. After he oiled the wheels, it rolled "
        "{add} cm farther. How far did the toy car roll on the second run?",
        "first roll",
        "second roll",
    ),
]

SUB_STORIES = [
    (
        "A wooden board is {dm} dm, {cm} cm, and {mm} mm long. A carpenter saws off a piece that is {sub} cm long. "
        "How long is the remaining board?",
        "initial length",
    ),
    (
        "A coil of rope is {dm} dm, {cm} cm, and {mm} mm long. Maya cuts off a {sub} cm piece to tie a parcel. "
        "How much rope is left on the coil?",
        "initial rope length",
    ),
]


def _generate_dynamic_metric_problem(rng, variant_idx=0):
    """Procedurally generate a metric length conversion problem (dm, cm, mm -> m, cm)."""
    use_sub = (variant_idx % 4 == 3)
    while True:
        dm_v = rng.choice([20, 30, 40, 50, 60, 70])
        cm_v = rng.choice([20, 30, 40, 50, 60, 70, 80, 90])
        mm_v = rng.choice([20, 30, 40, 50, 60, 70, 80, 90])
        if (dm_v, cm_v, mm_v) != (50, 50, 50):
            break

    dm_in_cm = dm_v * 10
    mm_in_cm = mm_v // 10
    base_cm = dm_in_cm + cm_v + mm_in_cm

    if not use_sub:
        add_v = rng.randint(112, 188)
        if (base_cm + add_v) % 100 == 0:
            add_v += 3
        total_cm = base_cm + add_v
        tmpl, lbl1, _ = ADD_STORIES[variant_idx % len(ADD_STORIES)]
        text = tmpl.format(dm=dm_v, cm=cm_v, mm=mm_v, add=add_v)
        expl = (
            f"Convert the {lbl1} to centimetres: {dm_v} dm = {dm_in_cm} cm, {cm_v} cm = {cm_v} cm, and "
            f"{mm_v} mm = {mm_in_cm} cm, giving {dm_in_cm} + {cm_v} + {mm_in_cm} = {base_cm} cm. "
            f"Adding {add_v} cm gives {base_cm} + {add_v} = {total_cm} cm = {format_m_cm(total_cm)}."
        )
    else:
        sub_v = rng.randint(34, 88)
        if (base_cm - sub_v) % 100 == 0:
            sub_v += 3
        add_v = -sub_v
        total_cm = base_cm - sub_v
        tmpl, lbl1 = SUB_STORIES[variant_idx % len(SUB_STORIES)]
        text = tmpl.format(dm=dm_v, cm=cm_v, mm=mm_v, sub=sub_v)
        expl = (
            f"Convert the {lbl1} to centimetres: {dm_v} dm = {dm_in_cm} cm, {cm_v} cm = {cm_v} cm, and "
            f"{mm_v} mm = {mm_in_cm} cm, totaling {dm_in_cm} + {cm_v} + {mm_in_cm} = {base_cm} cm. "
            f"Subtracting {sub_v} cm leaves {base_cm} - {sub_v} = {total_cm} cm = {format_m_cm(total_cm)}."
        )

    cands = {total_cm}
    trap_cands = [
        base_cm,
        total_cm - mm_in_cm,
        total_cm - cm_v + (cm_v // 10),
        total_cm - mm_in_cm + mm_v,
        base_cm - add_v,
        (dm_v + cm_v + mm_v) * 5 + abs(add_v),
    ]
    for c in trap_cands:
        if len(cands) >= 5:
            break
        if c >= 105 and c != total_cm:
            cands.add(c)
    for delta in [-10, 10, -20, 20, 45, -45]:
        if len(cands) >= 5:
            break
        v = total_cm + delta
        if v >= 105 and v != total_cm:
            cands.add(v)

    ch_cm = list(cands)[:5]
    rng.shuffle(ch_cm)
    ans_idx = ch_cm.index(total_cm)
    opts_str = [format_m_cm(c) for c in ch_cm]
    check_metric_jump(dm_v, cm_v, mm_v, add_v, ch_cm, opts_str, ans_idx)
    return dm_v, cm_v, mm_v, add_v, ch_cm, opts_str, ans_idx, text, expl


def q_2003_10(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Metric Length Conversion (m, dm, cm, mm)", "Based on 2003, Problem 10")

    opts0 = ["6 m 78 cm", "5 m 73 cm", "5 m 55 cm", "11 m 28 cm", "7 m 23 cm"]
    check_metric_jump(50, 50, 50, 123, [678, 573, 555, 1128, 723], opts0, 0)
    if include_orig:
        d.problem(
            "Original 2003 #10.",
            "Jumpy the kangaroo has been training for the Animal Olympics. His longest jump during the training was "
            "50 dm 50 cm and 50 mm long. He won the gold medal at the end of the Olympics with a jump that was "
            "123 cm longer. How long was Jumpy's winning jump?",
            choices=opts0,
            choice_cols=3,
        )
        key.append((
            "2003 #10",
            "A",
            "Convert each part of the training jump to centimetres: 50 dm = 500 cm, 50 cm = 50 cm, and 50 mm = 5 cm. "
            "So the training jump was 500 + 50 + 5 = 555 cm. Adding 123 cm gives 555 + 123 = 678 cm, which is 6 m 78 cm.",
        ))

    rng = random.Random(seed)
    v_order = list(range(4))
    rng.shuffle(v_order)
    for idx in range(1, num_practice + 1):
        dm_v, cm_v, mm_v, add_v, ch_cm, opts, ans_idx, text, expl = _generate_dynamic_metric_problem(
            rng, variant_idx=v_order[(idx - 1) % len(v_order)]
        )
        check_metric_jump(dm_v, cm_v, mm_v, add_v, ch_cm, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2003_10

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
