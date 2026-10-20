# Model: argon
"""Math Kangaroo 2003, Problem #12 - Question Generator."""
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
QUESTION_ID = (2003, 12)


RIGHT_OF = {"F": "L", "K": "R"}
LEFT_OF = {"F": "R", "K": "L"}


def house_valid(net, opt):
    layout, gm, sm = opt  # layout "GL": gable face left, side right; "SL": side left, gable right
    for g in ("F", "K"):
        nb = RIGHT_OF[g] if layout == "GL" else LEFT_OF[g]
        if net[g] == gm and net[nb] == sm:
            return True
    return False


def check_house(net, opts, answer):
    good = [i for i, o in enumerate(opts) if house_valid(net, o)]
    assert good == [answer], (net, good, answer)


def draw_mark(c, mark, P, side):
    """P(s, t) maps face coords (s along base 0..1, t = height 0..1 of wall) to page."""
    if mark is None:
        return
    if mark == "door":
        a, b = (0.4, 0.6) if side else (0.36, 0.64)
        pts = [P(a, 0), P(b, 0), P(b, 0.62), P(a, 0.62)]
        c.setFillColor(DARK)
    elif mark == "win":
        a, b = (0.4, 0.6) if side else (0.34, 0.66)
        pts = [P(a, 0.32), P(b, 0.32), P(b, 0.68), P(a, 0.68)]
        c.setFillColor(colors.white)
    if mark in ("door", "win"):
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close(); c.drawPath(p, stroke=1, fill=1)
        if mark == "win":
            m1, m2 = P((a + b) / 2, 0.32), P((a + b) / 2, 0.68)
            c.line(m1[0], m1[1], m2[0], m2[1])
            n1, n2 = P(a, 0.5), P(b, 0.5)
            c.line(n1[0], n1[1], n2[0], n2[1])
    elif mark == "dot":
        cx, cy = P(0.5, 0.5)
        c.setFillColor(colors.black); c.circle(cx, cy, 2.6, stroke=0, fill=1)
    c.setFillColor(colors.black)


def fig_net(net, s=27):
    wg, ls, h, p = 1.0, 1.25, 0.85, 0.5
    sl = math.hypot(wg / 2, p)
    rf = 0.85  # roof depth drawn in net
    # bounding box in units
    nx = rf * p / sl; ny = rf * (wg / 2) / sl
    xmin, xmax = -h, wg + h
    ymin, ymax = -(h + p), ls + h + p + ny
    W, H = (xmax - xmin) * s, (ymax - ymin) * s

    def draw(c, x, y):
        def T(u, v):
            return x + (u - xmin) * s, y + (v - ymin) * s

        def poly(pts, fill=None):
            pa = c.beginPath(); pa.moveTo(*T(*pts[0]))
            for q in pts[1:]: pa.lineTo(*T(*q))
            pa.close()
            if fill is not None:
                c.setFillColor(fill)
            c.drawPath(pa, stroke=1, fill=1 if fill is not None else 0)
            c.setFillColor(colors.black)
        c.setLineWidth(1.1)
        faces = {"K": ((0, ls), (wg, 0), (0, 1)), "F": ((0, 0), (wg, 0), (0, -1)),
                 "L": ((0, 0), (0, ls), (-1, 0)), "R": ((wg, 0), (0, ls), (1, 0))}
        poly([(0, 0), (wg, 0), (wg, ls), (0, ls)], colors.white)
        for name, (O, e, n) in faces.items():
            def A(sv, tv, O=O, e=e, n=n):
                return (O[0] + sv * e[0] + tv * n[0], O[1] + sv * e[1] + tv * n[1])
            if name in ("F", "K"):
                pk = A(0.5, h + p)
                poly([A(0, 0), A(1, 0), A(1, h), pk, A(0, h)], colors.white)
                if name == "K":  # roofs on the slanted edges
                    for P1, P2, sx in ((A(0, h), pk, -1), (pk, A(1, h), 1)):
                        off = (sx * nx, ny)
                        poly([P1, P2, (P2[0] + off[0], P2[1] + off[1]), (P1[0] + off[0], P1[1] + off[1])], DARK)
            else:
                poly([A(0, 0), A(1, 0), A(1, h), A(0, h)], colors.white)
            draw_mark(c, net[name], lambda sv, tv, A=A: T(*A(sv, tv * h)), name in "LR")
    return W, H, draw


def fig_house(opt, s=30):
    layout, gm, sm = opt
    wg, ls, h, p = 0.95, 1.15, 1.25, 0.55
    ca, sa = math.cos(math.radians(28)), math.sin(math.radians(28))
    u = (-ca * wg * s, sa * wg * s)   # gable face direction
    v = (ca * ls * s, sa * ls * s)    # side face direction
    W = (ca * wg + ca * ls) * s
    H = (h + p) * s + max(u[1] / 2 + v[1], 0) + 2

    def draw(c, x, y):
        mir = layout == "SL"
        ox = x + (ca * ls * s if mir else ca * wg * s)

        def M(px, py):
            return (ox - px if mir else ox + px, y + py)

        def poly(pts, fill):
            pa = c.beginPath(); pa.moveTo(*M(*pts[0]))
            for q in pts[1:]: pa.lineTo(*M(*q))
            pa.close(); c.setFillColor(fill); c.drawPath(pa, stroke=1, fill=1); c.setFillColor(colors.black)
        c.setLineWidth(1.1)
        H_ = h * s; P_ = p * s
        pk = (u[0] / 2, u[1] / 2 + H_ + P_)
        poly([(0, 0), u, (u[0], u[1] + H_), pk, (0, H_)], colors.white)
        poly([(0, 0), v, (v[0], v[1] + H_), (0, H_)], colors.white)
        poly([(0, H_), pk, (pk[0] + v[0], pk[1] + v[1]), (v[0], v[1] + H_)], DARK)
        draw_mark(c, gm, lambda sv, tv: M(sv * u[0], sv * u[1] + tv * H_), False)
        draw_mark(c, sm, lambda sv, tv: M(sv * v[0], sv * v[1] + tv * H_), True)
    return W, H, draw


def house_problem(net, opts, answer):
    check_house(net, opts, answer)
    return vstack([fig_net(net), option_row([fig_house(o) for o in opts], gap=16)], gap=14)


def q_2003_12(d, key, set_num=5, include_orig=True):
    d.heading(f"Set {set_num} - Folding a house", "Based on 2003, Problem 12")
    tip = (
        "<i>(The dark parts at the top are the roof and the middle square is the floor; "
        "fold the walls away from you so the drawings are on the outside of the house.)</i>"
    )
    if include_orig:
        net = {"F": "door", "K": None, "L": None, "R": "dot"}
        opts = [("GL", None, "dot"), ("SL", "door", None), ("GL", "door", "dot"), ("SL", None, "dot"), ("GL", None, "door")]
        d.problem("Original 2003 #12.", "The picture has been drawn on paper and cut out to make a house. "
                  "Which of the houses did it become? " + tip, house_problem(net, opts, 0), "below")
        key.append(("2003 #12", "A", "Stand in front of the door wall: the dot wall is on your LEFT. So from the back (no door), the dot is on the right of the plain end wall - house A."))

    net = {"F": None, "K": "door", "L": "dot", "R": None}
    opts = [("GL", "door", "dot"), ("SL", "door", None), ("SL", "door", "dot"), ("GL", None, None), ("SL", None, "dot")]
    d.problem(f"Practice {set_num}.1", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 2), "below")
    key.append((f"{set_num}.1", "C", "The door is on the end wall that has the roof attached. Facing that door, the dot wall is on your left."))

    net = {"F": "door", "K": "dot", "L": "win", "R": None}
    opts = [("GL", "dot", "win"), ("SL", "door", "win"), ("SL", "dot", None), ("GL", "door", "win"), ("GL", "door", None)]
    d.problem(f"Practice {set_num}.2", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 3), "below")
    key.append((f"{set_num}.2", "D", "Facing the door wall, the window wall is on your right and the plain wall on your left. Only D shows that."))

    net = {"F": "dot", "K": None, "L": "door", "R": "win"}
    opts = [("SL", "dot", "door"), ("GL", "dot", "door"), ("GL", None, "door"), ("SL", None, "win"), ("GL", "dot", "win")]
    d.problem(f"Practice {set_num}.3", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 1), "below")
    key.append((f"{set_num}.3", "B", "Facing the dot end wall: the door wall is on your right, the window wall on your left. B shows the dot wall with the door wall to its right."))

GENERATE = q_2003_12

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
