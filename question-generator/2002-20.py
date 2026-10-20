# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #20 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    hstack,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 20)


def make_tunnel_cubes(outer_w, outer_h, hole_w, hole_h, depth):
    """Build a set of (ix, iy, iz) unit cubes for a tunnel with centered hole."""
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
        c.setLineWidth(1)

    return w, h, draw


def check_tunnel_pyramid(t_cubes, p_cubes, choices, ans_idx):
    unused = len(t_cubes) - len(p_cubes)
    assert unused > 0, f"Expected positive unused cubes, got {unused}"
    matches = [i for i, ch in enumerate(choices) if int(ch) == unused]
    assert matches == [ans_idx], f"Tunnel/pyramid unused={unused}, choices={choices}, ans_idx={ans_idx}"


NAMES = ["Leo", "Clara", "Max", "Zoe", "Noah", "Maya", "Sam", "Elena"]


def _generate_dynamic_tunnel_pyramid(rng, variant_idx=0):
    """Procedurally generate a 3D tunnel-to-pyramid cube counting problem."""
    actor = rng.choice(NAMES)
    use_5x5 = (variant_idx % 2 == 0)

    if use_5x5:
        outer_s, hole_s = 5, 3
        h1 = rng.choice([1, 2])
        h2 = rng.choice([1, 2])
        h3 = rng.choice([1, 2, 3])
        layer_specs = [(5, 5, h1), (3, 3, h2), (1, 1, h3)]
        p_cubes = make_stepped_pyramid_cubes(layer_specs)
        p_count = len(p_cubes)
        per_layer = outer_s * outer_s - hole_s * hole_s  # 16
        min_depth = (p_count // per_layer) + 1
        depth = rng.randint(max(3, min_depth), max(4, min_depth + 1))
        t_cubes = make_tunnel_cubes(outer_s, outer_s, hole_s, hole_s, depth)
        t_count = len(t_cubes)
        unused = t_count - p_count

        l1_str = f"{h1} layer of 5 × 5" if h1 == 1 else f"{h1} layers of 5 × 5"
        l2_str = f"{h2} layer of 3 × 3" if h2 == 1 else f"{h2} layers of 3 × 3"
        l3_str = f"{h3} single cube" if h3 == 1 else f"a stack of {h3} single cubes"
        text = (
            f"{actor} built a tunnel {depth} cubes deep with a 5 × 5 outer square and a 3 × 3 tunnel opening (fig.1). "
            f"{actor} then rearranged the cubes into a stepped pyramid (fig.2) with {l1_str} at the base, "
            f"{l2_str} in the middle, and {l3_str} on top. How many cubes from the tunnel were <i>not</i> used?"
        )
        expl = (
            f"Each of the {depth} depth layers of the tunnel has 5×5 - 3×3 = 25 - 9 = 16 cubes, so the tunnel has "
            f"{depth} × 16 = {t_count} cubes in total. The stepped pyramid uses "
            f"{h1}×25 + {h2}×9 + {h3}×1 = {p_count} cubes. Therefore, {t_count} - {p_count} = {unused} cubes were not used."
        )
    else:
        outer_s, hole_s = 4, 2
        h1 = rng.choice([1, 2])
        h2 = rng.choice([1, 2, 3])
        layer_specs = [(4, 4, h1), (2, 2, h2)]
        p_cubes = make_stepped_pyramid_cubes(layer_specs)
        p_count = len(p_cubes)
        per_layer = outer_s * outer_s - hole_s * hole_s  # 12
        min_depth = (p_count // per_layer) + 1
        depth = rng.randint(max(3, min_depth), max(4, min_depth + 1))
        t_cubes = make_tunnel_cubes(outer_s, outer_s, hole_s, hole_s, depth)
        t_count = len(t_cubes)
        unused = t_count - p_count

        l1_str = f"{h1} layer of 4 × 4" if h1 == 1 else f"{h1} layers of 4 × 4"
        l2_str = f"{h2} layer of 2 × 2" if h2 == 1 else f"{h2} layers of 2 × 2"
        text = (
            f"{actor} made a tunnel {depth} cubes deep using a 4 × 4 square frame with a 2 × 2 hole in the center (fig.1). "
            f"Then {actor} built a stepped pedestal (fig.2) with {l1_str} at the bottom and {l2_str} on top. "
            f"How many cubes from the tunnel were <i>not</i> used?"
        )
        expl = (
            f"Each of the {depth} tunnel layers contains 4×4 - 2×2 = 16 - 4 = 12 cubes, so the tunnel has "
            f"{depth} × 12 = {t_count} cubes in total. The pedestal uses {h1}×16 + {h2}×4 = {p_count} cubes. "
            f"Therefore, {t_count} - {p_count} = {unused} cubes were not used."
        )

    cands = {unused}
    for delta in [-4, -2, 2, 4, -6, 6, 1, -1, 3, -3]:
        if len(cands) >= 5:
            break
        v = unused + delta
        if v >= 1:
            cands.add(v)
    vals = sorted(list(cands))[:5]
    if rng.random() < 0.4:
        vals = list(reversed(vals))
    opts = [str(v) for v in vals]
    ans_idx = vals.index(unused)
    check_tunnel_pyramid(t_cubes, p_cubes, opts, ans_idx)
    return t_cubes, p_cubes, opts, ans_idx, text, expl


def q_2002_20(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Rearranging 3D Cube Tunnel into a Pyramid", "Based on 2002, Problem 20")

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

    rng = random.Random(seed)
    for idx in range(1, num_practice + 1):
        tc, pc, opts, ans_idx, text, expl = _generate_dynamic_tunnel_pyramid(rng, variant_idx=idx - 1)
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
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
