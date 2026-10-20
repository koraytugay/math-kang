# Model: argon
"""Math Kangaroo 2007, Problem #24 - Question Generator."""
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
QUESTION_ID = (2007, 24)


def fig_folding_sequence():
    """Draw the 4-step folding and corner-cutting diagram from 2007 #24."""
    w, h = 155, 48

    def draw(c, x, y):
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.setLineWidth(1.0)
        # Step 1: full square 32x32 with vertical dashed midline
        s = 30
        x1 = x + 4
        y1 = y + 4
        c.rect(x1, y1, s, s, stroke=1, fill=0)
        c.setDash(3, 2)
        c.line(x1 + s / 2, y1, x1 + s / 2, y1 + s)
        c.setDash([])
        # Curved arrow 1
        p = c.beginPath()
        p.moveTo(x1 + 6, y1 + s + 3)
        p.curveTo(x1 + 12, y1 + s + 10, x1 + 20, y1 + s + 10, x1 + 25, y1 + s + 3)
        c.drawPath(p, stroke=1, fill=0)
        c.line(x1 + 25, y1 + s + 3, x1 + 22, y1 + s + 6)
        c.line(x1 + 25, y1 + s + 3, x1 + 22, y1 + s + 2)

        # Step 2: half rectangle 15x30 with horizontal dashed midline
        x2 = x1 + s + 14
        c.rect(x2, y1, s / 2, s, stroke=1, fill=0)
        c.setDash(3, 2)
        c.line(x2, y1 + s / 2, x2 + s / 2, y1 + s / 2)
        c.setDash([])
        # Curved arrow 2 (top to bottom)
        p2 = c.beginPath()
        p2.moveTo(x2 + s / 2 + 2, y1 + s - 4)
        p2.curveTo(x2 + s / 2 + 10, y1 + s - 6, x2 + s / 2 + 10, y1 + s / 2 + 2, x2 + s / 2 + 2, y1 + s / 2 - 2)
        c.drawPath(p2, stroke=1, fill=0)

        # Step 3: small square 15x15
        x3 = x2 + s / 2 + 16
        c.rect(x3, y1, s / 2, s / 2, stroke=1, fill=0)
        # Arrow 3
        c.line(x3 + s / 2 + 3, y1 + s / 4, x3 + s / 2 + 11, y1 + s / 4)
        c.line(x3 + s / 2 + 11, y1 + s / 4, x3 + s / 2 + 8, y1 + s / 4 + 2.5)
        c.line(x3 + s / 2 + 11, y1 + s / 4, x3 + s / 2 + 8, y1 + s / 4 - 2.5)

        # Step 4: small square 15x15 with top-left corner cut
        x4 = x3 + s / 2 + 14
        hs = s / 2
        cut = 5
        p3 = c.beginPath()
        p3.moveTo(x4, y1)
        p3.lineTo(x4 + hs, y1)
        p3.lineTo(x4 + hs, y1 + hs)
        p3.lineTo(x4 + cut, y1 + hs)
        p3.lineTo(x4, y1 + hs - cut)
        p3.close()
        c.drawPath(p3, stroke=1, fill=0)
        c.setDash(2, 2)
        c.line(x4, y1 + hs - cut, x4 + cut, y1 + hs)
        c.setDash([])

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def fig_unfolded_paper(design_kind, s=36):
    """Draw an unfolded square paper design resulting from cutting corners/edges."""
    w = h = s + 6

    def draw(c, x, y):
        ox = x + 3
        oy = y + 3
        d = s * 0.22
        mid = s / 2.0

        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.setLineWidth(1.1)

        def stroke_poly(pts):
            p = c.beginPath()
            p.moveTo(ox + pts[0][0], oy + pts[0][1])
            for px, py in pts[1:]:
                p.lineTo(ox + px, oy + py)
            p.close()
            c.drawPath(p, stroke=1, fill=0)

        if design_kind == "four_corners":
            # A: Octagon (all 4 outer corners cut off)
            stroke_poly([
                (d, 0), (s - d, 0),
                (s, d), (s, s - d),
                (s - d, s), (d, s),
                (0, s - d), (0, d),
            ])
        elif design_kind == "top_bot_notches":
            # B: V-notches in middle of top and bottom edges
            stroke_poly([
                (0, 0), (mid - d * 0.7, 0), (mid, d), (mid + d * 0.7, 0), (s, 0),
                (s, s), (mid + d * 0.7, s), (mid, s - d), (mid - d * 0.7, s), (0, s),
            ])
        elif design_kind == "left_right_notches":
            # C: V-notches in middle of left and right edges
            stroke_poly([
                (0, 0), (s, 0),
                (s, mid - d * 0.7), (s - d, mid), (s, mid + d * 0.7),
                (s, s), (0, s),
                (0, mid + d * 0.7), (d, mid), (0, mid - d * 0.7),
            ])
        elif design_kind == "center_diamond":
            # D: Solid outer square with diamond hole in the center
            c.rect(ox, oy, s, s, stroke=1, fill=0)
            stroke_poly([
                (mid, mid - d), (mid + d, mid), (mid, mid + d), (mid - d, mid),
            ])
        elif design_kind == "all_four_edge_notches":
            # IMPOSSIBLE with 1 corner cut: notches on all 4 edges at once!
            stroke_poly([
                (0, 0), (mid - d * 0.65, 0), (mid, d * 0.85), (mid + d * 0.65, 0), (s, 0),
                (s, mid - d * 0.65), (s - d * 0.85, mid), (s, mid + d * 0.65),
                (s, s), (mid + d * 0.65, s), (mid, s - d * 0.85), (mid - d * 0.65, s), (0, s),
                (0, mid + d * 0.65), (d * 0.85, mid), (0, mid - d * 0.65),
            ])
        elif design_kind == "single_top_notch":
            # IMPOSSIBLE with 2 folds: notch on ONLY the top edge!
            stroke_poly([
                (0, 0), (s, 0), (s, s),
                (mid + d * 0.7, s), (mid, s - d), (mid - d * 0.7, s), (0, s),
            ])
        elif design_kind == "two_opposite_corners":
            # IMPOSSIBLE: only 2 opposite outer corners cut off!
            stroke_poly([
                (d, 0), (s, 0), (s, s - d), (s - d, s), (0, s), (0, d),
            ])
        else:
            c.rect(ox, oy, s, s, stroke=1, fill=0)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_paper_fold_designs(designs, target_set, expected_idx):
    matches = [i for i, d_kind in enumerate(designs) if d_kind in target_set]
    assert matches == [expected_idx], f"Paper fold check failed: matches={matches} vs {expected_idx}"


def q_2007_24(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Folding a Square Paper Twice & Cutting a Corner", "Based on 2007, Problem 24")

    valid_4_corners = {"four_corners", "top_bot_notches", "left_right_notches", "center_diamond"}
    orig_A_to_D = ["four_corners", "top_bot_notches", "left_right_notches", "center_diamond"]
    assert all(k in valid_4_corners for k in orig_A_to_D)

    if include_orig:
        row_AD = option_row([fig_unfolded_paper(k) for k in orig_A_to_D], gap=18)
        d.problem(
            "Original 2007 #24.",
            "A square piece of paper is folded twice in such a way that the result is a square again. "
            "In the new square, one of the corners is cut out and then the paper is unfolded. "
            "Which of the following designs (A, B, C, D) cannot be obtained this way? "
            "(Choose <b>E</b> if all four designs can be obtained this way.)",
            vstack([fig_folding_sequence(), row_AD], gap=8),
            "below",
            choices=["Design A", "Design B", "Design C", "Design D", "All of these designs can be obtained this way"],
            choice_cols=3,
        )
        key.append((
            "2007 #24",
            "E",
            "When the square is folded in half vertically and then horizontally, the resulting small square has 4 corners: "
            "(1) the 4 loose outer corners (cutting it gives A), (2) the folded top/bottom midpoints (cutting it gives B), "
            "(3) the folded left/right midpoints (cutting it gives C), and (4) the center point where both creases meet "
            "(cutting it gives D). Since all four designs A–D can be obtained by choosing which corner to cut, the answer is E.",
        ))

    practices = [
        # Practice .1: One of the 5 visual options is IMPOSSIBLE ("all_four_edge_notches" at C) -> Answer: C
        (
            ["four_corners", "top_bot_notches", "all_four_edge_notches", "left_right_notches", "center_diamond"],
            {"all_four_edge_notches"},
            2,
            "A square piece of paper is folded in half vertically and then in half horizontally to form a smaller square. "
            "<b>Exactly one</b> of the four corners of this folded square is cut off with a straight snip, and the paper is unfolded. "
            "Which of the 5 designs below <b>cannot</b> be obtained?",
            "Cutting a single corner of the twice-folded square can cut the 4 outer corners (A), the top and bottom edge midpoints (B), "
            "the left and right edge midpoints (D), or the center (E). To get notches on all four edges at once (C), you would have to "
            "cut two different corners of the folded square, so C cannot be obtained with one corner cut.",
        ),
        # Practice .2: Which design is obtained when you cut the corner where BOTH fold creases meet (the completely folded center corner)? -> center_diamond at D
        (
            ["four_corners", "top_bot_notches", "left_right_notches", "center_diamond", "all_four_edge_notches"],
            {"center_diamond"},
            3,
            "A square sheet of paper is folded in half twice (once vertically, once horizontally) to make a smaller square. "
            "You cut off the single corner where <b>both folded creases meet</b>, and then unfold the paper. Which design do you get?",
            "The corner where the vertical crease and horizontal crease meet is the exact center of the original square! "
            "Cutting that corner removes a diamond-shaped hole right in the middle of the unfolded square (D).",
        ),
        # Practice .3: Which design is obtained when you cut the corner made of the 4 loose outer corners? -> four_corners at A
        (
            ["four_corners", "top_bot_notches", "left_right_notches", "center_diamond", "single_top_notch"],
            {"four_corners"},
            0,
            "A square piece of paper is folded in half vertically and then in half horizontally into a smaller square. "
            "One of its corners consists of <b>4 loose paper corners</b> (with no fold creases). If you cut off that corner "
            "and unfold the paper, which shape do you get?",
            "The corner with 4 loose layers contains all 4 outer corners of the original square stacked together. "
            "Snipping it cuts off all 4 outer corners of the unfolded square, producing the octagon in A.",
        ),
        # Practice .4: Which of the 5 designs CANNOT be obtained by cutting one corner of the twice-folded square? ("single_top_notch" at B)
        (
            ["center_diamond", "single_top_notch", "four_corners", "top_bot_notches", "left_right_notches"],
            {"single_top_notch"},
            1,
            "A square paper is folded in half twice to form a smaller square, and one corner of the folded square is cut off. "
            "When unfolded, the cut pattern must be symmetric across both fold lines. Which design below <b>cannot</b> be obtained?",
            "Because the paper was folded in half both vertically and horizontally, any cut must be symmetric across both the "
            "vertical and horizontal midlines. Design B has a notch on the top edge only (and not on the bottom edge), which is impossible!",
        ),
    ]

    for idx, (d_kinds, target_s, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_paper_fold_designs(d_kinds, target_s, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            option_row([fig_unfolded_paper(k) for k in d_kinds], gap=14),
            "below",
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_24

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
