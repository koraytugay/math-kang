# Model: argon
"""Math Kangaroo 2002, Problem #15 - Question Generator."""
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
QUESTION_ID = (2002, 15)


def fig_flag_silhouette(kind, s=1.0):
    """Draw a flagpole and shaded flag silhouette of the specified kind."""
    w = 54 * s
    h = 54 * s

    def draw(c, x, y):
        px = x + 6 * s
        py0 = y + 4 * s
        py1 = y + 44 * s  # Top of attachment on pole (pole height = 40*s, attachment height = 30*s: py1-30*s to py1)
        att_bot = y + 14 * s
        att_top = y + 44 * s
        fw = 36 * s

        # Flag polygon vertices depending on kind
        if kind == "flat":
            # Full rectangular silhouette (like 2002 #15 C)
            pts = [(px, att_bot), (px, att_top), (px + fw, att_top), (px + fw, att_bot)]
        elif kind == "fold_up_top":
            # Like 2002 #15 A: attached from att_bot to att_top, loose part rises slightly above att_top
            pts = [
                (px, att_bot),
                (px, att_top),
                (px + 8 * s, att_top),
                (px + 8 * s, att_top + 6 * s),
                (px + fw, att_top + 6 * s),
                (px + fw, att_top - 2 * s),
                (px + 8 * s, att_bot),
            ]
        elif kind == "torn_pole_bottom":
            # Like 2002 #15 B (TORN!): missing lower half along the pole!
            mid_y = (att_bot + att_top) / 2 + 3 * s
            pts = [
                (px, mid_y),
                (px, att_top),
                (px + fw + 4 * s, att_top),
                (px + 14 * s, att_bot + 4 * s),
                (px + 14 * s, mid_y),
            ]
        elif kind == "fold_diag_peak":
            # Like 2002 #15 D: full attachment along pole, diagonal fold with peak on top
            pts = [
                (px, att_bot),
                (px, att_top),
                (px + 16 * s, att_top),
                (px + 20 * s, att_top + 6 * s),
                (px + 30 * s, att_top),
                (px + fw + 2 * s, att_top),
                (px + fw + 2 * s, att_top - 6 * s),
            ]
        elif kind == "slanted_right":
            # Like 2002 #15 E: full attachment along pole, right edge slanted inward
            pts = [
                (px, att_bot),
                (px, att_top),
                (px + fw + 2 * s, att_top),
                (px + fw + 2 * s, att_top - 6 * s),
                (px + fw - 8 * s, att_bot),
            ]
        elif kind == "torn_pole_top":
            # TORN: missing upper half along the pole!
            mid_y = (att_bot + att_top) / 2 - 2 * s
            pts = [
                (px, att_bot),
                (px, mid_y),
                (px + 14 * s, mid_y),
                (px + 14 * s, att_top),
                (px + fw, att_top),
                (px + fw - 6 * s, att_bot),
            ]
        elif kind == "torn_pole_middle":
            # TORN: V-gap cut right out of the middle of the pole attachment!
            mid_y = (att_bot + att_top) / 2
            pts = [
                (px, att_bot),
                (px, mid_y - 6 * s),
                (px + 12 * s, mid_y),
                (px, mid_y + 6 * s),
                (px, att_top),
                (px + fw, att_top),
                (px + fw, att_bot),
            ]
        elif kind == "giant_stretched":
            # IMPOSSIBLE: horizontal length is fine, but vertical pole edge is fine, wait:
            # What if there is a hole/split or detached from pole completely?
            pts = [
                (px + 10 * s, att_bot),
                (px + 10 * s, att_top),
                (px + fw + 4 * s, att_top),
                (px + fw + 4 * s, att_bot),
            ]
        elif kind == "wavy_bottom":
            pts = [
                (px, att_bot),
                (px, att_top),
                (px + fw, att_top),
                (px + fw - 4 * s, att_bot + 6 * s),
                (px + 18 * s, att_bot),
            ]
        else:
            pts = [(px, att_bot), (px, att_top), (px + fw, att_top), (px + fw, att_bot)]

        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.setFillColor(colors.Color(0.68, 0.70, 0.68))
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.0)
        c.drawPath(p, stroke=1, fill=1)

        # Draw thick vertical flagpole
        c.setStrokeColor(colors.black)
        c.setLineWidth(2.6)
        c.line(px, py0, px, py1 + 2 * s)
        c.setLineWidth(1.0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_flag_silhouette(kinds, expected_idx, mode="impossible"):
    torn_kinds = {"torn_pole_bottom", "torn_pole_top", "torn_pole_middle", "giant_stretched"}
    if mode == "impossible":
        matches = [i for i, k in enumerate(kinds) if k in torn_kinds]
    else:
        matches = [i for i, k in enumerate(kinds) if k not in torn_kinds]
    assert matches == [expected_idx], f"Flag silhouette mismatch: {matches} vs {expected_idx}"


def q_2002_15(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Flag Silhouette in the Wind", "Based on 2002, Problem 15")

    orig_kinds = ["fold_up_top", "torn_pole_bottom", "flat", "fold_diag_peak", "slanted_right"]
    check_flag_silhouette(orig_kinds, 1, mode="impossible")
    if include_orig:
        d.problem(
            "Original 2002 #15.",
            "From her window Karla looks at the wall of a house. There she can see the silhouette of a rectangular "
            "flag flying in the wind. At five different moments she draws the silhouette. Which of the 5 pictures "
            "cannot be right unless the flag is torn?",
            option_row([fig_flag_silhouette(k) for k in orig_kinds], gap=14),
            "below",
        )
        key.append((
            "2002 #15",
            "B",
            "The rectangular flag is attached to the flagpole along its entire left vertical edge, so the segment "
            "where the flag touches the pole must always keep its full height. In picture B, the lower half of the "
            "left edge is missing from the pole, which is impossible unless the flag is torn away from the pole.",
        ))

    practices = [
        (
            ["flat", "fold_diag_peak", "torn_pole_top", "slanted_right", "wavy_bottom"],
            2,
            "impossible",
            "Leo watches a rectangular banner attached along its left vertical edge to a flagpole. "
            "He sketches 5 silhouettes as the wind blows. Which sketch <b>cannot</b> happen unless the banner is torn from the pole?",
            "Because the left edge of the rectangular banner is fastened to the pole from top to bottom of the attachment, "
            "the silhouette must touch the entire attachment segment along the pole. Sketch C is missing the upper half along the pole, "
            "which can only happen if the banner is torn.",
        ),
        (
            ["torn_pole_middle", "flat", "slanted_right", "fold_up_top", "fold_diag_peak"],
            0,
            "impossible",
            "Maya draws 5 silhouettes of a rectangular flag flying in the wind. One silhouette is impossible "
            "unless the flag is ripped along the pole. Which one is it?",
            "In picture A, there is a triangular gap right along the middle of the flagpole where the flag is supposed to be "
            "attached. Since the left edge is fixed to the pole, that gap cannot appear unless the flag is torn.",
        ),
        (
            ["slanted_right", "fold_up_top", "wavy_bottom", "giant_stretched", "flat"],
            3,
            "impossible",
            "Sam looks at the shadow of a rectangular flag fastened to a vertical pole. Which of the 5 shadows below "
            "is <b>impossible</b> unless the flag has come completely loose from the pole?",
            "In shadow D, there is an empty gap between the flagpole and the entire flag! Since the flag's left side is "
            "attached directly to the pole, shadow D is impossible unless the flag is torn off the pole.",
        ),
        (
            ["torn_pole_bottom", "torn_pole_top", "torn_pole_middle", "giant_stretched", "slanted_right"],
            4,
            "possible",
            "Four of the 5 flag silhouettes below are impossible unless the rectangular flag is torn from the pole. "
            "Which silhouette <b>can</b> happen with an intact flag?",
            "Only in E is the flag attached continuously along its full vertical segment on the flagpole while the free right edge "
            "folds slightly inward in the wind. In A, B, C, and D, parts of the flag are detached from the pole.",
        ),
    ]

    for idx, (kinds, ans_idx, mode, text, expl) in enumerate(practices[:num_practice], start=1):
        check_flag_silhouette(kinds, ans_idx, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            option_row([fig_flag_silhouette(k) for k in kinds], gap=14),
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_15

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
