# Model: argon
"""Math Kangaroo 2007, Problem #17 - Question Generator."""
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
QUESTION_ID = (2007, 17)


def fig_painted_cube(Wx, Wy, Wz, s=14):
    kx = s * 0.38
    ky = s * 0.30
    w = Wx * s + Wz * kx + 8
    h = Wy * s + Wz * ky + 8

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4

        def pt(ix, iy, iz):
            return ox + ix * s + iz * kx, oy + iy * s + iz * ky

        def poly(pts, fill, stroke=colors.black, lw=1.0):
            p = c.beginPath()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
            c.setFillColor(fill)
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
            c.drawPath(p, stroke=1, fill=1)

        # Front face (grey)
        poly([pt(0, 0, 0), pt(Wx, 0, 0), pt(Wx, Wy, 0), pt(0, Wy, 0)], fill=colors.Color(0.75, 0.75, 0.75), lw=1.5)
        # Top face (lighter grey)
        poly([pt(0, Wy, 0), pt(Wx, Wy, 0), pt(Wx, Wy, Wz), pt(0, Wy, Wz)], fill=colors.Color(0.84, 0.84, 0.84), lw=1.5)
        # Right face (darker grey)
        poly([pt(Wx, 0, 0), pt(Wx, 0, Wz), pt(Wx, Wy, Wz), pt(Wx, Wy, 0)], fill=colors.Color(0.62, 0.62, 0.62), lw=1.5)

        # Grid lines
        c.setLineWidth(0.9)
        c.setStrokeColor(colors.black)
        for ix in range(1, Wx):
            c.line(*pt(ix, 0, 0), *pt(ix, Wy, 0))
            c.line(*pt(ix, Wy, 0), *pt(ix, Wy, Wz))
        for iy in range(1, Wy):
            c.line(*pt(0, iy, 0), *pt(Wx, iy, 0))
            c.line(*pt(Wx, iy, 0), *pt(Wx, iy, Wz))
        for iz in range(1, Wz):
            c.line(*pt(0, Wy, iz), *pt(Wx, Wy, iz))
            c.line(*pt(Wx, 0, iz), *pt(Wx, Wy, iz))

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def count_painted_faces(Wx, Wy, Wz, target_faces):
    cnt = 0
    for ix in range(Wx):
        for iy in range(Wy):
            for iz in range(Wz):
                faces = (
                    (1 if ix == 0 else 0)
                    + (1 if ix == Wx - 1 else 0)
                    + (1 if iy == 0 else 0)
                    + (1 if iy == Wy - 1 else 0)
                    + (1 if iz == 0 else 0)
                    + (1 if iz == Wz - 1 else 0)
                )
                if faces == target_faces:
                    cnt += 1
    return cnt


def check_painted_cube(Wx, Wy, Wz, target_faces, choices, ans_idx):
    cnt = count_painted_faces(Wx, Wy, Wz, target_faces)
    matches = [i for i, ch in enumerate(choices) if int(ch) == cnt]
    assert matches == [ans_idx], f"Painted cube ({Wx}x{Wy}x{Wz}, faces={target_faces}) -> {cnt}, choices={choices}, ans_idx={ans_idx}"


def q_2007_17(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Painted Cube Cut into Unit Cubes", "Based on 2007, Problem 17")

    opts0 = ["4", "6", "8", "10", "12"]
    check_painted_cube(3, 3, 3, 2, opts0, 4)
    if include_orig:
        d.problem(
            "Original 2007 #17.",
            "A cube with a side length of 3 cm is painted grey and cut into smaller cubes with a side length "
            "of 1 cm each. How many of the smaller cubes will have <b>exactly 2</b> faces painted?",
            fig_painted_cube(3, 3, 3, s=14),
            "right",
            opts0,
        )
        key.append((
            "2007 #17",
            "E",
            "In a 3 × 3 × 3 cube, the unit cubes with 2 painted faces lie in the middle of each of the 12 edges "
            "(excluding the 8 corners). Since there is 1 such cube on each of the 12 edges, there are 12 cubes "
            "with exactly 2 faces painted.",
        ))

    practices = [
        # Practice .1: 3x3x3 cube, exactly 1 face painted -> 6 face-center cubes (Answer: B)
        (
            3, 3, 3, 1,
            ["4", "6", "8", "9", "12"],
            1,
            "A 3 cm × 3 cm × 3 cm wooden cube is painted grey on the outside and cut into 27 small 1 cm cubes. "
            "How many of the small cubes have <b>exactly 1</b> face painted?",
            "A cube has 6 faces, and in a 3 × 3 × 3 cube only the single center cube on each face has 1 painted face. "
            "That gives 6 × 1 = 6 small cubes.",
        ),
        # Practice .2: 4x4x4 cube, exactly 2 faces painted -> 12 * (4 - 2) = 24 cubes (Answer: D)
        (
            4, 4, 4, 2,
            ["8", "12", "16", "24", "32"],
            3,
            "A cube with side length 4 cm is painted grey on all 6 faces and then cut into 1 cm unit cubes. "
            "How many of the unit cubes have <b>exactly 2</b> faces painted?",
            "The cubes with 2 faces painted lie along the 12 edges, excluding the 2 corners on each edge. "
            "On a 4 cm edge there are 4 - 2 = 2 such cubes, so across all 12 edges there are 12 × 2 = 24 cubes.",
        ),
        # Practice .3: 4x4x4 cube, exactly 1 face painted -> 6 * (4 - 2)^2 = 24 cubes (Answer: C)
        (
            4, 4, 4, 1,
            ["6", "16", "24", "36", "48"],
            2,
            "A 4 cm × 4 cm × 4 cm cube is painted grey on the outside and cut into 64 unit cubes of side 1 cm. "
            "How many of the unit cubes have <b>exactly 1</b> face painted?",
            "On each of the 6 faces of the 4 × 4 × 4 cube, the inner 2 × 2 = 4 squares (not touching any edge) "
            "have 1 painted face. Across all 6 faces, that is 6 × 4 = 24 unit cubes.",
        ),
        # Practice .4: 4x3x3 rectangular block, exactly 2 faces painted ->
        # 4 edges of length 4 have (4-2)=2 each -> 8; 8 edges of length 3 have (3-2)=1 each -> 8; total = 16 (Answer: C)
        (
            4, 3, 3, 2,
            ["12", "14", "16", "18", "20"],
            2,
            "A 4 cm × 3 cm × 3 cm rectangular block is painted grey on the outside and cut into 1 cm unit cubes. "
            "How many of the unit cubes have <b>exactly 2</b> faces painted?",
            "Cubes with 2 painted faces sit along the 12 edges (between the corners). The 4 edges of length 4 cm "
            "each have 4 - 2 = 2 such cubes (4 × 2 = 8), and the 8 edges of length 3 cm each have 3 - 2 = 1 such cube "
            "(8 × 1 = 8). Altogether there are 8 + 8 = 16 cubes.",
        ),
    ]

    for idx, (wx, wy, wz, tf, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_painted_cube(wx, wy, wz, tf, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_painted_cube(wx, wy, wz, s=12),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2007_17

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
