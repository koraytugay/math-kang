# Model: argon
"""Math Kangaroo 2002, Problem #20 - Question Generator."""
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
QUESTION_ID = (2002, 20)


def make_tunnel_cubes(outer_w, outer_h, hole_w, hole_h, depth):
    """Build a set of (ix, iy, iz) unit cubes for a tunnel with centered/bottom hole."""
    cubes = set()
    x0 = (outer_w - hole_w) // 2
    y0 = (outer_h - hole_h) // 2
    for iz in range(depth):
        for iy in range(outer_h):
            for ix in range(outer_w):
                if not (x0 <= ix < x0 + hole_w and y0 <= iy < y0 + hole_h):
                    cubes.add((ix, iy, iz))
    return cubes


def make_stepped_pyramid_cubes(layer_specs):
    """layer_specs: list of (size_w, size_d, num_layers) from bottom to top, centered on bottom layer."""
    cubes = set()
    base_w, base_d, _ = layer_specs[0]
    cur_y = 0
    for w, d_len, h_layers in layer_specs:
        x0 = (base_w - w) // 2
        z0 = (base_d - d_len) // 2
        for dy in range(h_layers):
            for iz in range(z0, z0 + d_len):
                for ix in range(x0, x0 + w):
                    cubes.add((ix, cur_y + dy, iz))
        cur_y += h_layers
    return cubes


def fig_cube_structure(cubes, s=11, label=None):
    """Render an arbitrary 3D set of (ix, iy, iz) unit cubes back-to-front."""
    kx = s * 0.35
    ky = s * 0.30
    max_x = max(p[0] for p in cubes) + 1
    max_y = max(p[1] for p in cubes) + 1
    max_z = max(p[2] for p in cubes) + 1

    label_h = 14 if label else 0
    w = max_x * s + max_z * kx + 8
    h = max_y * s + max_z * ky + 8 + label_h

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4 + label_h

        def pt(ix, iy, iz):
            return ox + ix * s + iz * kx, oy + iy * s + iz * ky

        def poly(pts, fill=colors.white, stroke=colors.black, lw=0.75):
            p = c.beginPath()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
            c.setFillColor(fill)
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
            c.drawPath(p, stroke=1, fill=1)

        SIDE_SHADE = colors.Color(0.82, 0.80, 0.76)
        TOP_SHADE = colors.Color(0.96, 0.96, 0.96)

        for iz in range(max_z - 1, -1, -1):
            for iy in range(max_y):
                for ix in range(max_x):
                    if (ix, iy, iz) in cubes:
                        if (ix + 1, iy, iz) not in cubes:
                            poly(
                                [pt(ix + 1, iy, iz), pt(ix + 1, iy, iz + 1), pt(ix + 1, iy + 1, iz + 1), pt(ix + 1, iy + 1, iz)],
                                fill=SIDE_SHADE,
                            )
                        if (ix, iy + 1, iz) not in cubes:
                            poly(
                                [pt(ix, iy + 1, iz), pt(ix + 1, iy + 1, iz), pt(ix + 1, iy + 1, iz + 1), pt(ix, iy + 1, iz + 1)],
                                fill=TOP_SHADE,
                            )
                        if (ix, iy, iz - 1) not in cubes:
                            poly(
                                [pt(ix, iy, iz), pt(ix + 1, iy, iz), pt(ix + 1, iy + 1, iz), pt(ix, iy + 1, iz)],
                                fill=colors.white,
                            )

        if label:
            c.setFillColor(colors.black)
            c.setFont("Times-Roman", 10)
            c.drawCentredString(x + w / 2, y + 2, label)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_tunnel_pyramid(t_cubes, p_cubes, choices, ans_idx):
    unused = len(t_cubes) - len(p_cubes)
    matches = [i for i, ch in enumerate(choices) if int(ch) == unused]
    assert matches == [ans_idx], f"Tunnel/pyramid unused={unused}, choices={choices}, ans_idx={ans_idx}"


def q_2002_20(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Rearranging 3D Cube Tunnel into a Pyramid", "Based on 2002, Problem 20")

    # Original 2002 #20:
    # Tunnel: 5x5 front with 3x3 hole (16 cubes per layer), 4 layers deep -> 64 cubes.
    # Pyramid (3-step pyramid 5x5 + 3x3 + 1x1 = 25 + 9 + 1 = 35 cubes -> 64 - 35 = 29 unused, Choice B)
    t0 = make_tunnel_cubes(5, 5, 3, 3, 4)
    p0 = make_stepped_pyramid_cubes([(5, 5, 1), (3, 3, 1), (1, 1, 1)])
    opts0 = ["34", "29", "22", "18", "15"]
    check_tunnel_pyramid(t0, p0, opts0, 1)
    if include_orig:
        fig0 = hstack([
            fig_cube_structure(t0, s=10, label="fig.1"),
            fig_cube_structure(p0, s=10, label="fig.2"),
        ], gap=18)
        d.problem(
            "Original 2002 #20.",
            "Robert made a tunnel using some identical cubes (fig.1). When he got bored, he rearranged the tunnel "
            "into a complete 3-layer stepped pyramid (fig.2: a 5×5 bottom layer, a 3×3 middle layer, and 1 top cube). "
            "How many cubes from the original tunnel did he <i>not</i> use for the pyramid?",
            fig0,
            "right",
            opts0,
        )
        key.append((
            "2002 #20",
            "B",
            "Each of the 4 depth layers of the tunnel is a 5 × 5 square (25 cubes) with a 3 × 3 hole (9 cubes) removed, "
            "giving 25 - 9 = 16 cubes per layer, or 4 × 16 = 64 cubes in total. "
            "The 3-layer pyramid uses 5×5 + 3×3 + 1×1 = 25 + 9 + 1 = 35 cubes. "
            "So 64 - 35 = 29 cubes were not used.",
        ))

    practices = [
        # Practice .1: Tunnel 5x5 with 3x3 hole, 3 layers deep = 3 * 16 = 48 cubes.
        # Pyramid: 5x5 + 3x3 + 1x1 = 35 cubes. Unused = 48 - 35 = 13 cubes (Answer: A)
        (
            make_tunnel_cubes(5, 5, 3, 3, 3),
            make_stepped_pyramid_cubes([(5, 5, 1), (3, 3, 1), (1, 1, 1)]),
            ["13", "15", "18", "21", "23"],
            0,
            "Leo built a tunnel 3 cubes deep with a 5 × 5 outer frame and a 3 × 3 tunnel opening (fig.1). "
            "He then used some of those cubes to build a 3-layer stepped pyramid with 5 × 5, 3 × 3, and 1 × 1 layers (fig.2). "
            "How many cubes from the tunnel were left over?",
            "Each of the 3 layers of the tunnel has 5×5 - 3×3 = 25 - 9 = 16 cubes, so the tunnel has 3 × 16 = 48 cubes. "
            "The pyramid uses 25 + 9 + 1 = 35 cubes. That leaves 48 - 35 = 13 cubes unused.",
        ),
        # Practice .2: Tunnel 4x4 with 2x2 hole, 4 layers deep = 4 * (16 - 4) = 48 cubes.
        # Pyramid: 3-layer stepped pyramid of 4x4 + 2x2 + 1x1? To stay centered, 4x4 + 2x2 = 16 + 4 = 20 cubes (2-layer stepped platform)
        # Or 4x4 (16) + 3x3 (9) + 2x2 (4) + 1x1 (1) = 30 cubes! Wait: let's use 5x5 with 3x3 hole, 4 layers deep (64 cubes)
        # and pyramid with 2-cube-high 3x3 layer and 3-cube-high 1x1 spire (25 + 18 + 3 = 46 cubes) -> 64 - 46 = 18 (Answer: D)!
        (
            make_tunnel_cubes(5, 5, 3, 3, 4),
            make_stepped_pyramid_cubes([(5, 5, 1), (3, 3, 2), (1, 1, 3)]),
            ["12", "14", "16", "18", "22"],
            3,
            "Clara built a tunnel 4 cubes deep with a 5 × 5 outer square and a 3 × 3 opening (fig.1). "
            "She rearranged the cubes into a tall tower-pyramid (fig.2) consisting of one 5 × 5 base layer, "
            "two 3 × 3 middle layers, and three single cubes stacked on top. How many cubes from the tunnel did she <i>not</i> use?",
            "The tunnel has 4 layers of 5×5 - 3×3 = 16 cubes, totaling 4 × 16 = 64 cubes. "
            "The tower-pyramid uses 25 + (2 × 9) + (3 × 1) = 25 + 18 + 3 = 46 cubes. "
            "So 64 - 46 = 18 cubes were not used.",
        ),
        # Practice .3: Tunnel 4x4 with 2x2 hole, 3 layers deep = 3 * 12 = 36 cubes.
        # Stepped block (fig.2): 4x4 bottom layer (16) + 2x2 top layer (4) = 20 cubes. Unused = 36 - 20 = 16 (Answer: C)
        (
            make_tunnel_cubes(4, 4, 2, 2, 3),
            make_stepped_pyramid_cubes([(4, 4, 1), (2, 2, 1)]),
            ["10", "12", "16", "20", "24"],
            2,
            "Max made a tunnel 3 cubes deep using a 4 × 4 square frame with a 2 × 2 hole in the center (fig.1). "
            "Then he built a 2-step pedestal (fig.2) with a 4 × 4 bottom layer (1 cube high) and a 2 × 2 top layer (1 cube high). "
            "How many cubes from the tunnel were <i>not</i> used?",
            "Each of the 3 tunnel layers contains 4×4 - 2×2 = 16 - 4 = 12 cubes, so the tunnel has 3 × 12 = 36 cubes in total. "
            "The 2-step pedestal uses 4×4 + 2×2 = 16 + 4 = 20 cubes. Therefore, 36 - 20 = 16 cubes were not used.",
        ),
        # Practice .4: Tunnel 4x4 with 2x2 hole, 4 layers deep = 4 * 12 = 48 cubes.
        # Stepped pedestal (fig.2): 4x4 bottom layer (16) + two 2x2 layers (8) = 24 cubes. Unused = 48 - 24 = 24 (Answer: E)
        (
            make_tunnel_cubes(4, 4, 2, 2, 4),
            make_stepped_pyramid_cubes([(4, 4, 1), (2, 2, 2)]),
            ["14", "16", "18", "20", "24"],
            4,
            "Zoe built a tunnel 4 cubes deep with a 4 × 4 outer square and a 2 × 2 center hole (fig.1). "
            "She rearranged some of the cubes into a monument (fig.2) with one 4 × 4 base layer and two 2 × 2 layers on top. "
            "How many cubes from the tunnel did she <i>not</i> use?",
            "Each of the 4 layers of the tunnel has 16 - 4 = 12 cubes, giving 4 × 12 = 48 cubes in total. "
            "The monument uses 16 + 2 × 4 = 24 cubes. Thus, 48 - 24 = 24 cubes were left over.",
        ),
    ]

    for idx, (tc, pc, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_tunnel_pyramid(tc, pc, opts, ans_idx)
        fig_p = hstack([
            fig_cube_structure(tc, s=10, label="fig.1"),
            fig_cube_structure(pc, s=10, label="fig.2"),
        ], gap=18)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_p,
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))

GENERATE = q_2002_20

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
