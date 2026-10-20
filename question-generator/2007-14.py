# Model: argon
"""Math Kangaroo 2007, Problem #14 - Question Generator."""
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
QUESTION_ID = (2007, 14)


def fig_aquarium(Wx, Wy, Wz, cubes_or_heights, s=26):
    kx = s * 0.28
    ky = s * 0.24

    if isinstance(cubes_or_heights, list):
        cubes = set()
        for iz, row in enumerate(cubes_or_heights):
            for ix, h in enumerate(row):
                for iy in range(h):
                    cubes.add((ix, iy, iz))
    else:
        cubes = set(cubes_or_heights)

    w = Wx * s + Wz * kx + 8
    h = Wy * s + Wz * ky + 8

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4

        def pt(ix, iy, iz):
            return ox + ix * s + iz * kx, oy + iy * s + iz * ky

        def poly(pts, fill=colors.white, stroke=colors.black, lw=0.9):
            p = c.beginPath()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
            c.setFillColor(fill)
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
            c.drawPath(p, stroke=1, fill=1)

        GRAY_FACE = colors.Color(0.65, 0.65, 0.65)

        # 1. Back/floor dashed guide lines of the aquarium
        c.setLineWidth(0.6)
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
        c.setDash(2, 2)
        c.line(*pt(0, 0, 0), *pt(0, 0, Wz))
        c.line(*pt(0, 0, Wz), *pt(Wx, 0, Wz))
        c.line(*pt(0, 0, Wz), *pt(0, Wy, Wz))
        c.setDash([])

        # 2. Draw cubes back-to-front
        for iz in range(Wz - 1, -1, -1):
            for iy in range(Wy):
                for ix in range(Wx):
                    if (ix, iy, iz) in cubes:
                        # Right face
                        if (ix + 1, iy, iz) not in cubes:
                            poly(
                                [pt(ix + 1, iy, iz), pt(ix + 1, iy, iz + 1), pt(ix + 1, iy + 1, iz + 1), pt(ix + 1, iy + 1, iz)],
                                fill=GRAY_FACE,
                                lw=0.9,
                            )
                        # Top face
                        if (ix, iy + 1, iz) not in cubes:
                            poly(
                                [pt(ix, iy + 1, iz), pt(ix + 1, iy + 1, iz), pt(ix + 1, iy + 1, iz + 1), pt(ix, iy + 1, iz + 1)],
                                fill=colors.white,
                                lw=0.9,
                            )
                        # Front face
                        if (ix, iy, iz - 1) not in cubes:
                            poly(
                                [pt(ix, iy, iz), pt(ix + 1, iy, iz), pt(ix + 1, iy + 1, iz), pt(ix, iy + 1, iz)],
                                fill=colors.white,
                                lw=0.9,
                            )

        # 3. Outer glass aquarium frame
        c.setLineWidth(1.6)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, Wx * s, Wy * s)
        c.line(*pt(0, Wy, 0), *pt(0, Wy, Wz))
        c.line(*pt(Wx, Wy, 0), *pt(Wx, Wy, Wz))
        c.line(*pt(Wx, 0, 0), *pt(Wx, 0, Wz))
        c.line(*pt(0, Wy, Wz), *pt(Wx, Wy, Wz))
        c.line(*pt(Wx, Wy, Wz), *pt(Wx, 0, Wz))

        # Always reset canvas colors
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_aquarium(capacity, cubes_count, choices, answer_idx, twist_type=None, pack_size=None):
    if twist_type == "packs":
        needed = capacity - cubes_count
        val = math.ceil(needed / pack_size)
    else:
        val = capacity - cubes_count
    assert choices[answer_idx] == val, f"Expected {val} at index {answer_idx}, got {choices[answer_idx]}"
    matching = [i for i, c in enumerate(choices) if c == val]
    assert matching == [answer_idx], f"Multiple or no choices match {val}: {matching}"


def q_2007_14(d, key, set_num=1, include_orig=True):
    d.heading(
        f"Problem {set_num}: 2007 #14 - Cube Aquarium",
        "Arranging 1 dm cubes inside a 3 dm aquarium (counting 3D cubes / volume)",
    )

    # Original 2007 #14
    if include_orig:
        H0 = [
            [1, 0, 0],
            [2, 1, 0],
            [3, 2, 1],
        ]
        opts0 = [9, 13, 17, 21, 27]
        check_aquarium(27, sum(sum(r) for r in H0), opts0, 2)
        d.problem(
            "2007 #14",
            "Daniella has an aquarium in the shape of a cube with edges 3 dm each. "
            "She started arranging cubes with edges 1 dm each inside the aquarium, "
            "in the way you can see on the picture. At most how many more such "
            "cubes can Daniella put into the aquarium?",
            fig_aquarium(3, 3, 3, H0),
            "right",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2007 #14",
            "C",
            "The aquarium holds 3 × 3 × 3 = 27 small cubes in total. Counting the cubes already inside: "
            "the front layer has 1 cube, the middle layer has 2 + 1 = 3 cubes, and the back layer has "
            "3 + 2 + 1 = 6 cubes, for a total of 1 + 3 + 6 = 10 cubes. Therefore, Daniella can put at "
            "most 27 - 10 = 17 more cubes into the aquarium.",
        ))

    # Practice .1
    H1 = [
        [1, 0, 0],
        [2, 1, 0],
        [3, 2, 2],
    ]
    opts1 = [16, 14, 12, 11, 9]
    check_aquarium(27, sum(sum(r) for r in H1), opts1, 0)
    d.problem(
        f"Practice {set_num}.1",
        "Leo has an aquarium in the shape of a cube with edges 3 dm each. "
        "He started arranging cubes with edges 1 dm each inside the aquarium, "
        "in the way you can see on the picture. At most how many more such "
        "cubes can Leo put into the aquarium?",
        fig_aquarium(3, 3, 3, H1),
        "right",
        opts1,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The aquarium holds 3 × 3 × 3 = 27 small cubes. Counting the cubes already inside: "
        "the front layer has 1 cube, the middle layer has 2 + 1 = 3 cubes, and the back layer has "
        "3 + 2 + 2 = 7 cubes, for a total of 1 + 3 + 7 = 11 cubes. Therefore, Leo can put at "
        "most 27 - 11 = 16 more cubes into the aquarium.",
    ))

    # Practice .2
    H2 = [
        [2, 0, 1],
        [2, 0, 2],
        [3, 1, 3],
    ]
    opts2 = [17, 16, 15, 14, 13]
    check_aquarium(27, sum(sum(r) for r in H2), opts2, 4)
    d.problem(
        f"Practice {set_num}.2",
        "Maya has an aquarium in the shape of a cube with edges 3 dm each. "
        "She started arranging cubes with edges 1 dm each inside the aquarium, "
        "in the way you can see on the picture. At most how many more such "
        "cubes can Maya put into the aquarium?",
        fig_aquarium(3, 3, 3, H2),
        "right",
        opts2,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "E",
        "The aquarium holds 3 × 3 × 3 = 27 small cubes. Counting the cubes already inside: "
        "the front layer has 2 + 1 = 3 cubes, the middle layer has 2 + 2 = 4 cubes, and the back layer has "
        "3 + 1 + 3 = 7 cubes, for a total of 3 + 4 + 7 = 14 cubes. Therefore, Maya can put at "
        "most 27 - 14 = 13 more cubes into the aquarium.",
    ))

    # Practice .3 (twist: cubes sold in boxes of 3)
    H3 = [
        [1, 1, 0],
        [2, 1, 0],
        [3, 2, 1],
    ]
    opts3 = [5, 6, 7, 8, 9]
    check_aquarium(27, sum(sum(r) for r in H3), opts3, 1, twist_type="packs", pack_size=3)
    d.problem(
        f"Practice {set_num}.3",
        "Lucas has an aquarium in the shape of a cube with edges 3 dm each. "
        "He arranged some 1 dm cubes inside as shown in the picture. He wants to fill the aquarium completely. "
        "If the small cubes are sold in boxes of 3 cubes each, what is the least number of boxes Lucas needs to buy?",
        fig_aquarium(3, 3, 3, H3),
        "right",
        opts3,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "B",
        "The aquarium holds 3 × 3 × 3 = 27 small cubes. Counting the cubes already inside: "
        "the front layer has 1 + 1 = 2 cubes, the middle layer has 2 + 1 = 3 cubes, and the back layer has "
        "3 + 2 + 1 = 6 cubes, for a total of 2 + 3 + 6 = 11 cubes. Lucas needs 27 - 11 = 16 more cubes. "
        "Since each box contains 3 cubes, 5 boxes provide 15 cubes (which is not enough), so Lucas needs at "
        "least 6 boxes (providing 18 cubes).",
    ))

GENERATE = q_2007_14

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
