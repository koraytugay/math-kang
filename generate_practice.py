"""Generate Math Kangaroo practice sets (originals + similar new problems).

Usage:  python generate_practice.py   ->  writes practice_2002_2003.pdf (with answer key on the last page)
Requires: reportlab
"""
import os
import math
import itertools
import argparse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

GEN_DIR = "generated"


def get_timestamp_filename():
    os.makedirs(GEN_DIR, exist_ok=True)
    return os.path.join(GEN_DIR, datetime.now().strftime("%Y-%m-%d-%H-%M-%S.pdf"))


def ensure_gen_path(path):
    os.makedirs(GEN_DIR, exist_ok=True)
    if not os.path.dirname(path):
        return os.path.join(GEN_DIR, path)
    return path


OUT = os.path.join(GEN_DIR, "practice_2002_2003.pdf")
PW, PH = letter
ML, MR, MT, MB = 54, 54, 60, 54
TW = PW - ML - MR
LETTERS = "ABCDE"
DARK = colors.Color(0.25, 0.25, 0.25)
GRAY = colors.Color(0.78, 0.78, 0.78)

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=11, leading=15)


# ----------------------------------------------------------------- layout
class Doc:
    def __init__(self, path):
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.c = canvas.Canvas(path, pagesize=letter)
        self.page = 1
        self.y = PH - MT
        self._footer()

    def _footer(self):
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(colors.grey)
        self.c.drawCentredString(PW / 2, 30, "Math Kangaroo practice (Grades 3-4)  -  page %d" % self.page)
        self.c.setFillColor(colors.black)

    def new_page(self):
        self.c.showPage()
        self.page += 1
        self.y = PH - MT
        self._footer()

    def need(self, h):
        if self.y - h < MB:
            self.new_page()

    def heading(self, text, sub=None):
        self.need(140)
        c = self.c
        c.setFont("Helvetica-Bold", 14)
        c.drawString(ML, self.y - 14, text)
        self.y -= 20
        if sub:
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(ML, self.y - 10, sub)
            self.y -= 14
        c.setLineWidth(0.8)
        c.line(ML, self.y - 2, PW - MR, self.y - 2)
        self.y -= 12

    def problem(self, label, text, fig=None, fig_pos="right", choices=None, choice_cols=5):
        """fig = (w, h, drawfn(c, x, y_bottom))."""
        c = self.c
        txt_w = TW - (fig[0] + 14 if fig and fig_pos == "right" else 0)
        p = Paragraph("<b>%s</b>&nbsp;&nbsp;%s" % (label, text), BODY)
        _, ph = p.wrap(txt_w, 1000)
        ch_h = 0
        if choices:
            rows = math.ceil(len(choices) / choice_cols)
            ch_h = rows * 16 + 4
        if fig and fig_pos == "right":
            h = max(ph + ch_h, fig[1]) + 16
        elif fig:
            h = ph + 8 + fig[1] + 6 + ch_h + 16
        else:
            h = ph + ch_h + 16
        self.need(h)
        top = self.y
        p.drawOn(c, ML, top - ph)
        y = top - ph
        if fig and fig_pos == "right":
            fig[2](c, PW - MR - fig[0], top - fig[1])
        elif fig:
            y -= 8
            fig[2](c, ML + (TW - fig[0]) / 2, y - fig[1])
            y -= fig[1] + 6
        if choices:
            cw = txt_w / choice_cols
            y -= 4
            for i, ch in enumerate(choices):
                r, col = divmod(i, choice_cols)
                yy = y - 12 - r * 16
                c.setFont("Helvetica-Bold", 11)
                c.drawString(ML + col * cw, yy, LETTERS[i] + ")")
                c.setFont("Helvetica", 11)
                c.drawString(ML + col * cw + 16, yy, str(ch))
        self.y = top - h

    def save(self):
        self.c.save()


def option_row(items, gap=18, label_h=14):
    """items: list of (w, h, drawfn). Draws them in a row labelled A..E."""
    w = sum(i[0] for i in items) + gap * (len(items) - 1) + 16 * len(items)
    h = max(i[1] for i in items) + label_h

    def draw(c, x, y):
        cx = x
        for k, (iw, ih, fn) in enumerate(items):
            c.setFillColor(colors.black)
            c.setStrokeColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(cx, y + h - 11, LETTERS[k] + ")")
            fn(c, cx + 16, y + (h - label_h - ih) / 2)
            cx += iw + 16 + gap
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
    return w, h, draw


def hstack(figs, gap=20):
    w = sum(f[0] for f in figs) + gap * (len(figs) - 1)
    h = max(f[1] for f in figs)

    def draw(c, x, y):
        cx = x
        for fw, fh, fn in figs:
            fn(c, cx, y + (h - fh) / 2)
            cx += fw + gap
    return w, h, draw


def vstack(figs, gap=12):
    w = max(f[0] for f in figs)
    h = sum(f[1] for f in figs) + gap * (len(figs) - 1)

    def draw(c, x, y):
        cy = y + h
        for fw, fh, fn in figs:
            cy -= fh
            fn(c, x + (w - fw) / 2, cy)
            cy -= gap
    return w, h, draw


# ------------------------------------------------- Set 1: cut-up square
SYMS = [lambda r, c: (r, c), lambda r, c: (c, -r), lambda r, c: (-r, -c), lambda r, c: (-c, r),
        lambda r, c: (r, -c), lambda r, c: (-c, -r), lambda r, c: (-r, c), lambda r, c: (c, r)]


def canon(cells):
    best = None
    for f in SYMS:
        pts = [f(r, c) for r, c in cells]
        mr = min(p[0] for p in pts); mc = min(p[1] for p in pts)
        key = tuple(sorted((p[0] - mr, p[1] - mc) for p in pts))
        best = key if best is None or key < best else best
    return best


def pieces_of(grid):
    d = {}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            d.setdefault(ch, []).append((r, c))
    return d


def check_cut(grid, options, answer):
    shapes = {canon(v) for v in pieces_of(grid).values()}
    bad = [i for i, o in enumerate(options) if canon(o) not in shapes]
    assert bad == [answer], (grid, bad, answer)


def fig_partition(grid, s=16):
    n_r, n_c = len(grid), len(grid[0])

    def draw(c, x, y):
        c.setLineWidth(1.4)
        top = y + n_r * s
        c.rect(x, y, n_c * s, n_r * s)
        for r in range(n_r):
            for col in range(n_c):
                if col + 1 < n_c and grid[r][col] != grid[r][col + 1]:
                    xx = x + (col + 1) * s
                    c.line(xx, top - r * s, xx, top - (r + 1) * s)
                if r + 1 < n_r and grid[r][col] != grid[r + 1][col]:
                    yy = top - (r + 1) * s
                    c.line(x + col * s, yy, x + (col + 1) * s, yy)
    return n_c * s, n_r * s, draw


def fig_poly(cells, s=13):
    rs = [p[0] for p in cells]; cs = [p[1] for p in cells]
    r0, c0 = min(rs), min(cs)
    cells = {(r - r0, c - c0) for r, c in cells}
    n_r = max(r for r, _ in cells) + 1; n_c = max(c for _, c in cells) + 1

    def draw(c, x, y):
        c.setLineWidth(1.2)
        top = y + n_r * s
        for r, col in cells:
            x0, y1 = x + col * s, top - r * s
            if (r - 1, col) not in cells: c.line(x0, y1, x0 + s, y1)
            if (r + 1, col) not in cells: c.line(x0, y1 - s, x0 + s, y1 - s)
            if (r, col - 1) not in cells: c.line(x0, y1, x0, y1 - s)
            if (r, col + 1) not in cells: c.line(x0 + s, y1, x0 + s, y1 - s)
    return n_c * s, n_r * s, draw


def cut_problem(grid, options, answer):
    check_cut(grid, options, answer)
    return vstack([fig_partition(grid), option_row([fig_poly(o) for o in options], gap=14)], gap=14)


# ------------------------------------------------- Set 2: skylines
def tok_path(tokens):
    """Yield drawing segments and bbox for a skyline token list."""
    x = y = 0
    pts = [(0, 0)]
    segs = []
    for t in tokens:
        k = t[0]
        if k == "H":
            segs.append(("L", x, y, x + t[1], y)); x += t[1]
        elif k == "V":
            segs.append(("L", x, y, x, y + t[1])); y += t[1]
        elif k == "D":
            segs.append(("L", x, y, x + t[1], y + t[2])); x += t[1]; y += t[2]
        elif k == "A":
            w = t[1]; hh = w * 0.42
            segs.append(("C", x, y, w, hh)); pts.append((x, y + hh)); x += w
        pts.append((x, y))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return segs, (min(xs), min(ys), max(xs), max(ys))


def fig_tokens(tokens, sc, lw=1.3):
    segs, (x0, y0, x1, y1) = tok_path(tokens)

    def draw(c, x, y):
        c.setLineWidth(lw)
        for s in segs:
            if s[0] == "L":
                c.line(x + (s[1] - x0) * sc, y + (s[2] - y0) * sc, x + (s[3] - x0) * sc, y + (s[4] - y0) * sc)
            else:
                _, ax, ay, w, hh = s
                X, Y = x + (ax - x0) * sc, y + (ay - y0) * sc
                p = c.beginPath(); p.moveTo(X, Y)
                p.curveTo(X, Y + hh * sc * 4 / 3, X + w * sc, Y + hh * sc * 4 / 3, X + w * sc, Y)
                c.drawPath(p, stroke=1, fill=0)
    return (x1 - x0) * sc, (y1 - y0) * sc, draw


def skyline_problem(sky, pieces, sc):
    return vstack([fig_tokens(sky, sc), option_row([fig_tokens(p, sc) for p in pieces], gap=26)], gap=18)


# ------------------------------------------------- Set 3: balance
def fig_balance(left, right, tilt):
    """left/right: lists of radii; tilt: +1 right side down, -1 left down, 0 level."""
    W, H = 220, 95

    def draw(c, x, y):
        cx = x + W / 2
        c.setFillColor(GRAY); c.ellipse(cx - 32, y, cx + 32, y + 8, stroke=0, fill=1)
        c.setFillColor(colors.black); c.setLineWidth(1.6)
        piv = y + 34
        c.line(cx, y + 4, cx, piv)
        ang = -0.09 * tilt
        L = 80
        lx, ly = cx - L * math.cos(ang), piv - L * math.sin(ang)
        rx, ry = cx + L * math.cos(ang), piv + L * math.sin(ang)
        c.setLineWidth(2.2); c.line(lx, ly, rx, ry)
        c.setLineWidth(1.2)
        for px, py, items in ((lx, ly, left), (rx, ry, right)):
            ty = py + 16
            c.line(px, py, px, ty)
            c.line(px - 36, ty, px + 36, ty)
            c.line(px - 36, ty, px - 42, ty + 8); c.line(px + 36, ty, px + 42, ty + 8)
            total = sum(2 * r for r in items) + 1.5 * (len(items) - 1)
            ox = px - total / 2
            for r in items:
                if r >= 6:
                    c.setFillColor(GRAY if r < 8 else colors.Color(0.55, 0.55, 0.55))
                    c.circle(ox + r, ty + r, r, stroke=1, fill=1)
                else:
                    c.setFillColor(colors.white)
                    c.circle(ox + r, ty + r, r, stroke=1, fill=1)
                c.setFillColor(colors.black)
                ox += 2 * r + 1.5
    return W, H, draw


# ------------------------------------------------- Set 4: brick of cubes
def fig_brick(Wn, Hn, Dn, s=13):
    k = 0.45 * s  # oblique offset per depth unit
    w = Wn * s + Dn * k; h = Hn * s + Dn * k

    def draw(c, x, y):
        c.setLineWidth(0.9)
        c.setFillColor(colors.white)
        for i in range(Wn + 1):
            c.line(x + i * s, y, x + i * s, y + Hn * s)
        for j in range(Hn + 1):
            c.line(x, y + j * s, x + Wn * s, y + j * s)
        top = y + Hn * s
        for i in range(Wn + 1):  # top receding lines
            c.line(x + i * s, top, x + i * s + Dn * k, top + Dn * k)
        for d in range(Dn + 1):
            c.line(x + d * k, top + d * k, x + Wn * s + d * k, top + d * k)
        rx = x + Wn * s
        for j in range(Hn + 1):  # right side receding lines
            c.line(rx, y + j * s, rx + Dn * k, y + j * s + Dn * k)
        for d in range(Dn + 1):
            c.line(rx + d * k, y + d * k, rx + d * k, top + d * k)
        c.setLineWidth(1.5)
        p = c.beginPath()
        p.moveTo(x, y); p.lineTo(rx, y); p.lineTo(rx + Dn * k, y + Dn * k); p.lineTo(rx + Dn * k, top + Dn * k)
        p.lineTo(x + Dn * k, top + Dn * k); p.lineTo(x, top); p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(colors.black)
    return w, h, draw


# ------------------------------------------------- Set 5: house nets
# Net faces: F (front gable, below floor), K (back gable, above floor), L, R (side walls).
# Seen from outside: facing F, net-R is on your left and net-L on your right;
# facing K, net-L is on your left and net-R on your right.
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


# ------------------------------------------------- Set 6: letter on grid
def shoelace(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2


def fig_letter(gw, gh, polys, s=15):
    def draw(c, x, y):
        c.setLineWidth(0.6)
        for i in range(gw + 1): c.line(x + i * s, y, x + i * s, y + gh * s)
        for j in range(gh + 1): c.line(x, y + j * s, x + gw * s, y + j * s)
        c.setLineWidth(2.2)
        for pts in polys:
            pa = c.beginPath(); pa.moveTo(x + pts[0][0] * s, y + pts[0][1] * s)
            for q in pts[1:]: pa.lineTo(x + q[0] * s, y + q[1] * s)
            pa.close()
            c.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.85))
            c.drawPath(pa, stroke=1, fill=1)
        c.setFillColor(colors.black)
    return gw * s, gh * s, draw


def letter_area(polys):
    return sum(shoelace(p) for p in polys)


# ================================================================== content
def append_answer_key(d, key, title="Answer Key & Explanations", subtitle=None):
    d.new_page()
    c = d.c
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PW / 2, PH - 70, title)
    if subtitle:
        c.setFont("Helvetica", 11)
        c.drawCentredString(PW / 2, PH - 90, subtitle)
        d.y = PH - 115
    else:
        d.y = PH - 95
    d.heading("Solutions & kid-friendly explanations")
    for lab, ans, why in key:
        p = Paragraph("<b>%s:&nbsp; %s</b>&nbsp;&nbsp;&nbsp;%s" % (lab, ans, why), BODY)
        _, ph = p.wrap(TW, 1000)
        d.need(ph + 8)
        p.drawOn(d.c, ML, d.y - ph)
        d.y -= ph + 8


def write_answer_key(path, title, subtitle, key):
    kd = Doc(path)
    append_answer_key(kd, key, title=title, subtitle=subtitle)
    kd.save()
    print("wrote", path)


# ------------------------------------------------- 2002 #1: Kangaroo grid puzzle
def fig_tile(strokes, s=26):
    """Draw a single square tile of size s with strokes."""
    w = h = s

    def draw(c, x, y):
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.rect(x, y, s, s, stroke=1, fill=0)
        c.setLineWidth(1.5)
        for kind, pts in strokes:
            if kind == "line":
                (x1, y1), (x2, y2) = pts
                c.line(x + x1 * s, y + y1 * s, x + x2 * s, y + y2 * s)
            elif kind == "curve":
                (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pts
                p = c.beginPath()
                p.moveTo(x + x1 * s, y + y1 * s)
                p.curveTo(x + cx1 * s, y + cy1 * s, x + cx2 * s, y + cy2 * s, x + x2 * s, y + y2 * s)
                c.drawPath(p, stroke=1, fill=0)
    return w, h, draw


def fig_tile_grid(n_rows, n_cols, cell_strokes, missing_rc, s=26):
    """Draw a grid of tiles where missing_rc is dashed with a question mark."""
    w = n_cols * s
    h = n_rows * s

    def draw(c, x, y):
        top = y + h
        for r in range(n_rows):
            for col in range(n_cols):
                cx = x + col * s
                cy = top - (r + 1) * s
                if (r, col) == missing_rc:
                    c.setLineWidth(1.0)
                    c.setStrokeColor(colors.black)
                    c.setDash(2, 2)
                    c.rect(cx, cy, s, s, stroke=1, fill=0)
                    c.setDash([])
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 5, "?")
                else:
                    c.setLineWidth(0.8)
                    c.setStrokeColor(colors.black)
                    c.rect(cx, cy, s, s, stroke=1, fill=0)
                    strokes = cell_strokes.get((r, col), [])
                    c.setLineWidth(1.5)
                    for kind, pts in strokes:
                        if kind == "line":
                            (x1, y1), (x2, y2) = pts
                            c.line(cx + x1 * s, cy + y1 * s, cx + x2 * s, cy + y2 * s)
                        elif kind == "curve":
                            (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pts
                            p = c.beginPath()
                            p.moveTo(cx + x1 * s, cy + y1 * s)
                            p.curveTo(cx + cx1 * s, cy + cy1 * s, cx + cx2 * s, cy + cy2 * s, cx + x2 * s, cy + y2 * s)
                            c.drawPath(p, stroke=1, fill=0)
    return w, h, draw


def check_missing_tile(tile_opts, correct_idx, top_conn, bot_conn, left_conn, right_conn):
    results = []
    for opt in tile_opts:
        ok = (
            opt.get("top", []) == top_conn
            and opt.get("bot", []) == bot_conn
            and opt.get("left", []) == left_conn
            and opt.get("right", []) == right_conn
        )
        results.append(ok)
    assert results[correct_idx] is True
    matches = [i for i, r in enumerate(results) if r]
    assert matches == [correct_idx], f"Expected unique match {correct_idx}, got {matches}"


def q_2002_1(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Missing puzzle tile", "Based on 2002, Problem 1")

    # Original 2002 #1
    t0_meta = [
        {"left": [0.5], "right": [0.8]},
        {"top": [0.2], "left": [0.5]},
        {"top": [0.2, 0.8], "right": [0.5]},
        {"top": [0.2, 0.5], "bot": [0.5]},
        {"left": [0.3], "bot": [0.7]},
    ]
    check_missing_tile(t0_meta, 3, [0.2, 0.5], [0.5], [], [])

    if include_orig:
        grid0 = {
            (0, 3): [("curve", ((0.1, 0.9), (0.1, 0.4), (0.2, 0.2), (0.2, 0.0))),
                     ("curve", ((0.7, 0.8), (0.6, 0.4), (0.5, 0.2), (0.5, 0.0)))],
            (2, 3): [("line", ((0.5, 1.0), (0.5, 0.0)))],
            (1, 2): [("curve", ((0.2, 0.7), (0.5, 0.7), (0.8, 0.5), (1.0, 0.5)))],
            (2, 2): [("curve", ((0.3, 0.9), (0.4, 0.5), (0.5, 0.3), (0.7, 0.0)))],
            (2, 1): [("line", ((0.0, 0.2), (1.0, 0.2)))],
            (2, 0): [("curve", ((1.0, 0.2), (0.6, 0.2), (0.3, 0.4), (0.1, 0.7)))],
        }
        opt0_strokes = [
            [("line", ((0.0, 0.5), (1.0, 0.8)))],
            [("curve", ((0.2, 1.0), (0.2, 0.6), (0.1, 0.5), (0.0, 0.5)))],
            [("line", ((0.2, 1.0), (1.0, 0.5))), ("line", ((0.8, 1.0), (1.0, 0.5)))],
            [("curve", ((0.2, 1.0), (0.2, 0.5), (0.5, 0.5), (0.5, 0.0))),
             ("line", ((0.5, 1.0), (0.5, 0.5)))],
            [("curve", ((0.0, 0.3), (0.4, 0.3), (0.7, 0.3), (0.7, 0.0)))],
        ]
        fig0 = vstack([
            fig_tile_grid(3, 4, grid0, (1, 3), s=28),
            option_row([fig_tile(s, s=28) for s in opt0_strokes], gap=16),
        ], gap=12)
        d.problem(
            "Original 2002 #1.",
            "Which of the squares below is missing from the picture of the kangaroo?",
            fig0,
            "below",
        )
        key.append((
            "2002 #1",
            "D",
            "Looking at the grid, the neck lines enter the missing square from the top at two points, "
            "and the leg continues down through the bottom edge. Tile D is the only square with two lines at the top "
            "and one line at the bottom connecting to the kangaroo's body.",
        ))

    # Practice 1.1: 3x3 grid track, missing center tile (1, 1). Enters top at 0.5, exits right at 0.5.
    t1_meta = [
        {"top": [0.5], "bot": [0.5]},
        {"top": [0.5], "right": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"left": [0.5], "bot": [0.5]},
        {"top": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t1_meta, 1, [0.5], [], [], [0.5])
    grid1 = {
        (0, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (1, 2): [("curve", ((0.0, 0.5), (0.4, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        (2, 2): [("curve", ((0.5, 1.0), (0.5, 0.5), (0.3, 0.2), (0.0, 0.2)))],
        (2, 1): [("line", ((1.0, 0.2), (0.0, 0.2)))],
        (2, 0): [("curve", ((1.0, 0.2), (0.5, 0.2), (0.2, 0.4), (0.2, 1.0)))],
        (1, 0): [("line", ((0.2, 0.0), (0.2, 1.0)))],
    }
    opt1_strokes = [
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("curve", ((0.0, 0.5), (0.3, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.6), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig1 = vstack([
        fig_tile_grid(3, 3, grid1, (1, 1), s=28),
        option_row([fig_tile(s, s=28) for s in opt1_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.1",
        "A train track runs across the grid below. Which tile belongs in the empty square marked with a question mark (?) "
        "to complete the continuous track?",
        fig1,
        "below",
    )
    key.append((
        f"{set_num}.1",
        "B",
        "The track enters the empty square from the top at the center and continues out to the right. "
        "Tile B contains the curved track connecting the top edge to the right edge.",
    ))

    # Practice 1.2: 4x3 grid, missing tile (1, 2). Enters left at 0.5, exits bottom at 0.5.
    t2_meta = [
        {"top": [0.5], "right": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"top": [0.5], "bot": [0.5]},
        {"left": [0.5], "bot": [0.5]},
        {"top": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t2_meta, 3, [], [0.5], [0.5], [])
    grid2 = {
        (1, 0): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (1, 1): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (2, 2): [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        (2, 3): [("line", ((0.0, 0.5), (1.0, 0.5)))],
    }
    opt2_strokes = [
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("curve", ((0.0, 0.5), (0.4, 0.5), (0.5, 0.3), (0.5, 0.0)))],
        [("curve", ((0.5, 1.0), (0.5, 0.6), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig2 = vstack([
        fig_tile_grid(3, 4, grid2, (1, 2), s=28),
        option_row([fig_tile(s, s=28) for s in opt2_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.2",
        "A pipe connects across the grid. Which tile is missing at the question mark (?) "
        "to connect the left pipe to the bottom pipe?",
        fig2,
        "below",
    )
    key.append((
        f"{set_num}.2",
        "D",
        "The incoming pipe comes from the left at the middle, and exits through the bottom edge at the middle. "
        "Tile D correctly turns the pipe from left to bottom.",
    ))

    # Practice 1.3: 3x3 grid crossing tracks, missing center tile (1, 1). Crossing (top-bot and left-right).
    t3_meta = [
        {"top": [0.5], "bot": [0.5]},
        {"left": [0.5], "right": [0.5]},
        {"top": [0.5], "bot": [0.5], "left": [0.5], "right": [0.5]},
        {"top": [0.5], "right": [0.5]},
        {"bot": [0.5], "left": [0.5]},
    ]
    check_missing_tile(t3_meta, 2, [0.5], [0.5], [0.5], [0.5])
    grid3 = {
        (0, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (2, 1): [("line", ((0.5, 1.0), (0.5, 0.0)))],
        (1, 0): [("line", ((0.0, 0.5), (1.0, 0.5)))],
        (1, 2): [("line", ((0.0, 0.5), (1.0, 0.5)))],
    }
    opt3_strokes = [
        [("line", ((0.5, 1.0), (0.5, 0.0)))],
        [("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("line", ((0.5, 1.0), (0.5, 0.0))), ("line", ((0.0, 0.5), (1.0, 0.5)))],
        [("curve", ((0.5, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.5)))],
        [("curve", ((0.5, 0.0), (0.5, 0.4), (0.3, 0.5), (0.0, 0.5)))],
    ]
    fig3 = vstack([
        fig_tile_grid(3, 3, grid3, (1, 1), s=28),
        option_row([fig_tile(s, s=28) for s in opt3_strokes], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.3",
        "Two roads cross each other on the map below: one road runs vertically and the other runs horizontally. "
        "Which tile belongs in the empty square marked with a question mark (?) so both roads can continue across the square?",
        fig3,
        "below",
    )
    key.append((
        f"{set_num}.3",
        "C",
        "Both the vertical road (top to bottom) and the horizontal road (left to right) pass through the missing square. "
        "Tile C shows the intersection of both roads.",
    ))


def q_2002_4(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Cutting a square into pieces", "Based on 2002, Problem 4")
    if include_orig:
        orig = ["AABD", "ABBD", "CCBF", "EFFF"]
        opts = [[(0, 0)], [(0, 0), (0, 1)], [(0, 0), (0, 1), (1, 1)],
                [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)], [(0, 0), (1, 0), (2, 0), (2, 1)]]
        d.problem("Original 2002 #4.", "The square was cut along the lines. Which of the shapes below was "
                  "<b>not</b> obtained this way?", cut_problem(orig, opts, 3), "below")
        key.append(("2002 #4", "D", "The pieces are: 1 small square, 2 dominoes, an L of 3, a T of 4 and an L of 4. There is no U-shaped piece."))

    g = ["AAAB", "CDAB", "CDDD", "CEEF"]
    o = [[(0, 0)], [(0, 0), (0, 1), (0, 2), (1, 1)], [(0, 0), (0, 1), (0, 2)],
         [(0, 0), (1, 0), (2, 0), (0, 1)], [(0, 0), (1, 0)]]
    d.problem(f"Practice {set_num}.1", "The square was cut along the lines. Which of the shapes below was "
              "<b>not</b> obtained this way?", cut_problem(g, o, 1), "below")
    key.append((f"{set_num}.1", "B", "Pieces: two L-shapes of 4, a straight 3, two dominoes, one small square. No T-shape."))

    g = ["AABBB", "ACCBE", "ACDDE", "FCDEE", "FFDGG"]
    o = [[(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1)], [(0, 1), (0, 2), (1, 0), (1, 1)],
         [(0, 1), (1, 0), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)]]
    d.problem(f"Practice {set_num}.2", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 2), "below")
    key.append((f"{set_num}.2", "C", "Pieces: four L-shapes of 4, one T, one L of 3, one domino. There is no zig-zag (S) piece."))

    g = ["AAABB", "ACCCB", "DDCEB", "DFFEE", "DFGGG"]
    o = [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 0), (2, 0)],
         [(0, 0), (0, 1), (1, 0), (2, 0)], [(0, 0), (0, 1), (1, 0), (1, 1)]]
    d.problem(f"Practice {set_num}.3", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 4), "below")
    key.append((f"{set_num}.3", "E", "Pieces: three L-shapes of 4, one T, two L-shapes of 3, one straight 3. No 2x2 square."))


# ------------------------------------------------- 2002 #6: Square vs rectangle perimeter
def fig_square_rect(s1_val, s2_val, label_s1, label_s2=None, label_mb=None, size=95):
    w = size + 45
    h = size + 25
    cut_ratio = s2_val / s1_val

    def draw(c, x, y):
        ox = x + 25
        oy = y + 12
        sw = size
        sh = size
        mx = ox + cut_ratio * sw

        # Light gray fill for AMTD rectangle
        c.setFillColor(colors.Color(0.88, 0.88, 0.88))
        c.rect(ox, oy, cut_ratio * sw, sh, stroke=0, fill=1)

        # Draw square border and dividing line MT
        c.setLineWidth(1.4)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, sw, sh, stroke=1, fill=0)
        c.setLineWidth(1.2)
        c.line(mx, oy, mx, oy + sh)

        # Labels for vertices A, B, C, D, M, T
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(ox - 10, oy - 9, "A")
        c.drawString(ox + sw + 3, oy - 9, "B")
        c.drawString(ox + sw + 3, oy + sh + 3, "C")
        c.drawString(ox - 10, oy + sh + 3, "D")
        c.drawString(mx - 4, oy - 10, "M")
        c.drawString(mx - 3, oy + sh + 3, "T")

        # Dimension labels
        c.setFont("Helvetica", 9)
        c.drawCentredString(ox - 16, oy + sh / 2 - 3, label_s1)
        if label_s2:
            c.drawCentredString(ox + (cut_ratio * sw) / 2, oy + sh + 4, label_s2)
        if label_mb:
            c.drawCentredString(mx + ((1 - cut_ratio) * sw) / 2, oy - 10, label_mb)

    return w, h, draw


def check_square_rect_diff(s1, s2, opts, correct_idx, twist_mb=None):
    if twist_mb is not None:
        am = s1 - twist_mb
        diff = 2 * (s1 - am)
    else:
        diff = 2 * (s1 - s2)
    assert opts[correct_idx] == diff, f"Expected {diff}, got {opts[correct_idx]}"
    matches = [i for i, v in enumerate(opts) if v == diff]
    assert matches == [correct_idx], f"Multiple matches: {matches}"


def q_2002_6(d, key, set_num=2, include_orig=True):
    d.heading(f"Set {set_num} - Square and rectangle perimeters", "Based on 2002, Problem 6")

    # Original 2002 #6: s1=10, s2=3. Perimeter diff = 4(10) - 2(10+3) = 40 - 26 = 14 cm.
    opts0 = [14, 10, 7, 6, 4]
    check_square_rect_diff(10, 3, opts0, 0)
    if include_orig:
        fig0 = fig_square_rect(10, 3, "10 cm", label_s2="3 cm")
        d.problem(
            "Original 2002 #6.",
            "The side of the square <i>ABCD</i> is 10 cm. The side <i>AM</i> of the rectangle <i>AMTD</i> is 3 cm. "
            "How much greater is the perimeter of the square than the perimeter of the rectangle <i>AMTD</i>?",
            fig0,
            "right",
            [f"{v} cm" for v in opts0],
            choice_cols=5,
        )
        key.append((
            "2002 #6",
            "A",
            "Perimeter of square ABCD = 4 × 10 = 40 cm. Perimeter of rectangle AMTD = 2 × (10 + 3) = 26 cm. "
            "Difference = 40 - 26 = 14 cm (or simply 2 × MB = 2 × 7 = 14 cm).",
        ))

    # Practice 2.1: s1=12, s2=4. Diff = 2*(12-4) = 16 cm. Answer: B (16 cm)
    opts1 = [10, 16, 18, 20, 24]
    check_square_rect_diff(12, 4, opts1, 1)
    fig1 = fig_square_rect(12, 4, "12 cm", label_s2="4 cm")
    d.problem(
        f"Practice {set_num}.1",
        "The side of square <i>ABCD</i> is 12 cm. The side <i>AM</i> of rectangle <i>AMTD</i> is 4 cm. "
        "How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig1,
        "right",
        [f"{v} cm" for v in opts1],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "B",
        "Perimeter of square ABCD = 4 × 12 = 48 cm. Perimeter of rectangle AMTD = 2 × (12 + 4) = 32 cm. "
        "Difference = 48 - 32 = 16 cm.",
    ))

    # Practice 2.2: s1=15, s2=6. Diff = 2*(15-6) = 18 cm. Answer: C (18 cm)
    opts2 = [14, 16, 18, 22, 24]
    check_square_rect_diff(15, 6, opts2, 2)
    fig2 = fig_square_rect(15, 6, "15 cm", label_s2="6 cm")
    d.problem(
        f"Practice {set_num}.2",
        "The side of square <i>ABCD</i> is 15 cm. The side <i>AM</i> of rectangle <i>AMTD</i> is 6 cm. "
        "How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig2,
        "right",
        [f"{v} cm" for v in opts2],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "C",
        "Perimeter of square ABCD = 4 × 15 = 60 cm. Perimeter of rectangle AMTD = 2 × (15 + 6) = 42 cm. "
        "Difference = 60 - 42 = 18 cm.",
    ))

    # Practice 2.3: twist - gives MB = 7 cm, s1 = 18 cm. Diff = 2 * MB = 14 cm. Answer: B (14 cm)
    opts3 = [12, 14, 16, 18, 22]
    check_square_rect_diff(18, None, opts3, 1, twist_mb=7)
    fig3 = fig_square_rect(18, 11, "18 cm", label_mb="MB = 7 cm")
    d.problem(
        f"Practice {set_num}.3",
        "The side of square <i>ABCD</i> is 18 cm. A line segment <i>MT</i> divides the square into two rectangles. "
        "The length of segment <i>MB</i> is 7 cm. How much greater is the perimeter of square <i>ABCD</i> than the perimeter of rectangle <i>AMTD</i>?",
        fig3,
        "right",
        [f"{v} cm" for v in opts3],
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "B",
        "Since AB = 18 cm and MB = 7 cm, AM = 18 - 7 = 11 cm. "
        "Perimeter of square = 4 × 18 = 72 cm. Perimeter of rectangle AMTD = 2 × (18 + 11) = 58 cm. "
        "Difference = 72 - 58 = 14 cm (which is simply 2 × MB = 2 × 7 = 14 cm).",
    ))


def q_2002_7(d, key, set_num=2, include_orig=True):
    d.heading(f"Set {set_num} - Pieces of a skyline", "Based on 2002, Problem 7")
    if include_orig:
        sky = [("A", 40), ("A", 40), ("H", 42), ("V", 40), ("H", 83), ("V", 42), ("D", 42, 43), ("D", 43, -43),
               ("V", -42), ("H", 83), ("V", -40), ("H", 42), ("D", 40, 40), ("D", 40, -40), ("V", 80), ("A", 40),
               ("A", 40), ("V", -80), ("H", 40), ("V", 40), ("H", 45), ("V", 85), ("H", 15), ("V", -85), ("H", 65),
               ("V", -40), ("H", 40)]
        pcs = [[("V", -30), ("H", 40), ("V", -40), ("H", 30)],
               [("D", 40, -40), ("V", 80), ("A", 40)],
               [("A", 40), ("V", -50), ("H", 25), ("V", 50), ("A", 40)],
               [("H", 40), ("V", -40), ("H", 42), ("D", 40, 40)],
               [("A", 40), ("A", 40), ("V", -50)]]
        d.problem("Original 2002 #7.", "Far away we see the skyline of a castle. Which of the pieces "
                  "<b>cannot</b> belong to the skyline?", skyline_problem(sky, pcs, 0.36), "below")
        key.append(("2002 #7", "C", "Wherever there are two arches, they sit right next to each other. There is never a U-shaped dip between two arches."))

    sky = [("H", 60), ("A", 35), ("A", 35), ("H", 40), ("V", 75), ("H", 30), ("D", 25, 35), ("D", 25, -35),
           ("H", 30), ("V", -75), ("H", 40), ("V", 110), ("H", 20), ("V", -110), ("H", 60)]
    pcs = [[("V", 50), ("D", 25, 35), ("D", 25, -35), ("H", 30)],
           [("D", 25, -35), ("H", 30), ("V", -75), ("H", 25)],
           [("A", 35), ("A", 35), ("H", 40), ("V", 50)],
           [("V", 40), ("H", 30), ("D", 25, 35)],
           [("H", 25), ("V", 110), ("H", 20), ("V", -110), ("H", 25)]]
    d.problem(f"Practice {set_num}.1", "Here is the skyline of a town. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.48), "below")
    key.append((f"{set_num}.1", "A", "In the skyline there is a flat part between the wall and the pointed roof. Piece A has the roof sitting straight on the wall."))

    sky = [("H", 50), ("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -15), ("H", 20),
           ("V", 15), ("H", 25), ("V", -50), ("H", 40), ("A", 50), ("H", 40), ("D", 35, 50), ("H", 40),
           ("D", 35, -50), ("H", 40)]
    pcs = [[("V", -30), ("H", 40), ("A", 50), ("H", 20)],
           [("A", 50), ("H", 40), ("D", 35, 50), ("H", 20)],
           [("H", 20), ("D", 35, -50), ("H", 40)],
           [("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50), ("H", 20)],
           [("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50)]]
    d.problem(f"Practice {set_num}.2", "Here is the skyline of a castle. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.42), "below")
    key.append((f"{set_num}.2", "E", "The castle wall has TWO notches at the top. Piece E shows a whole tower top with only one notch."))

    sky = [("H", 50), ("A", 30), ("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40), ("V", -60), ("H", 40),
           ("A", 60), ("H", 25), ("V", 90), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 50)]
    pcs = [[("A", 60), ("H", 25), ("V", 60)],
           [("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40)],
           [("V", 50), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 20)],
           [("A", 30), ("H", 25), ("V", -40)],
           [("V", -40), ("H", 40), ("A", 60)]]
    d.problem(f"Practice {set_num}.3", "Here is a skyline with a small arch, a tower and a dome. Which piece "
              "<b>cannot</b> belong to it?", skyline_problem(sky, pcs, 0.45), "below")
    key.append((f"{set_num}.3", "D", "After each arch the line goes flat and then UP. Piece D goes down after the arch."))


def q_2002_9(d, key, set_num=3, include_orig=True):
    d.heading(f"Set {set_num} - Balance scales", "Based on 2002, Problem 9")
    if include_orig:
        d.problem("Original 2002 #9.", "On one plate of a balance there are 6 oranges (small circles) and on the "
                  "other there are melons (big circles). When we put one more melon, exactly like the others, on the "
                  "orange plate, the balance is level. The weight of one melon is the same as:",
                  fig_balance([4] * 6, [9, 9], 1), "right",
                  ["2 oranges", "3 oranges", "4 oranges", "5 oranges", "6 oranges"], 3)
        key.append(("2002 #9", "E", "6 oranges + 1 melon = 2 melons. Take one melon off each side: 6 oranges = 1 melon."))

    d.problem(f"Practice {set_num}.1", "On one plate there are 8 plums (small circles) and on the other 3 lemons "
              "(gray circles). When we put one more lemon on the plum plate, the balance is level. "
              "One lemon weighs the same as:",
              fig_balance([4] * 8, [7, 7, 7], 1), "right",
              ["2 plums", "3 plums", "4 plums", "5 plums", "8 plums"], 3)
    key.append((f"{set_num}.1", "C", "8 plums + 1 lemon = 3 lemons, so 8 plums = 2 lemons, so 1 lemon = 4 plums."))

    d.problem(f"Practice {set_num}.2", "On one plate there are 10 cherries (small circles) and on the other 4 apples "
              "(gray circles). When we put 2 more apples on the cherry plate, the balance is level. "
              "One apple weighs the same as:",
              fig_balance([3.4] * 10, [7, 7, 7, 7], 1), "right",
              ["2 cherries", "3 cherries", "4 cherries", "5 cherries", "10 cherries"], 3)
    key.append((f"{set_num}.2", "D", "10 cherries + 2 apples = 4 apples, so 10 cherries = 2 apples, so 1 apple = 5 cherries."))

    d.problem(f"Practice {set_num}.3", "The balance is level. On the left plate there is 1 melon (big circle) and 3 "
              "oranges; on the right plate there are 9 oranges. How many oranges weigh the same as "
              "<b>2 melons</b>?",
              fig_balance([9, 4, 4, 4], [4] * 9, 0), "right", [6, 8, 9, 12, 18])
    key.append((f"{set_num}.3", "D", "Take 3 oranges off each side: 1 melon = 6 oranges, so 2 melons = 12 oranges."))


def q_2003_9(d, key, set_num=4, include_orig=True):
    d.heading(f"Set {set_num} - Red outside, blue inside", "Based on 2003, Problem 9")
    if include_orig:
        d.problem("Original 2003 #9.", "Chris built the brick in the picture using red and blue cubes of the same "
                  "size. The outside of the brick is completely red, but all cubes used inside are blue. "
                  "How many blue cubes did Chris use?", fig_brick(5, 4, 4), "right", [12, 24, 36, 40, 48])
        key.append(("2003 #9", "A", "Brick is 5 x 4 x 4. Remove the outer layer: inside is 3 x 2 x 2 = 12 blue cubes."))

    d.problem(f"Practice {set_num}.1", "Maya built this brick (4 cubes wide, 4 cubes tall, 3 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did she use?",
              fig_brick(4, 4, 3), "right", [2, 4, 6, 8, 12])
    key.append((f"{set_num}.1", "B", "Inside is (4-2) x (4-2) x (3-2) = 2 x 2 x 1 = 4."))

    d.problem(f"Practice {set_num}.2", "Leo built this brick (6 cubes wide, 3 cubes tall, 4 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did he use?",
              fig_brick(6, 3, 4), "right", [4, 6, 8, 12, 16])
    key.append((f"{set_num}.2", "C", "Inside is (6-2) x (3-2) x (4-2) = 4 x 1 x 2 = 8."))

    d.problem(f"Practice {set_num}.3", "Anna built this brick (5 cubes wide, 3 cubes tall, 3 cubes deep). The outside "
              "is completely red and the cubes inside are blue. How many <b>red</b> cubes did she use?",
              fig_brick(5, 3, 3), "right", [30, 36, 39, 42, 45])
    key.append((f"{set_num}.3", "D", "Total = 5 x 3 x 3 = 45. Inside (blue) = 3 x 1 x 1 = 3. Red = 45 - 3 = 42."))


def q_2003_12(d, key, set_num=5, include_orig=True):
    d.heading(f"Set {set_num} - Folding a house", "Based on 2003, Problem 12")
    tip = ("<i>(The dark parts at the top of the picture are the roof. The shape in the middle is the floor.)</i>")
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


def q_2003_14(d, key, set_num=6, include_orig=True):
    d.heading(f"Set {set_num} - Area of a letter on squared paper", "Based on 2003, Problem 14")
    q = "If the side of each little square is 1 cm, what is the area of the letter %s (in square cm)?"
    if include_orig:
        N = [[(1, 0), (2, 0), (2, 6), (1, 6)], [(5, 0), (6, 0), (6, 6), (5, 6)], [(2, 6), (3, 6), (5, 0), (4, 0)]]
        assert letter_area(N) == 18
        d.problem("Original 2003 #14.", q % "N", fig_letter(7, 6, N), "right", [14, 15, 16, 17, 18])
        key.append(("2003 #14", "E", "Each side bar is 6. The slanted part is a parallelogram 1 wide and 6 tall = 6 (cut-off triangles fit together). 6+6+6 = 18."))

    Z = [[(1, 6), (6, 6), (6, 7), (1, 7)], [(1, 0), (6, 0), (6, 1), (1, 1)], [(4, 6), (6, 6), (3, 1), (1, 1)]]
    assert letter_area(Z) == 20
    d.problem(f"Practice {set_num}.1", q % "Z", fig_letter(7, 7, Z, 14), "right", [16, 18, 20, 22, 24])
    key.append((f"{set_num}.1", "C", "Top bar 5 + bottom bar 5 + slanted part (2 wide, 5 tall) 10 = 20."))

    V = [[(1, 5), (3, 5), (4, 2), (5, 5), (7, 5), (5, 0), (3, 0)]]
    assert letter_area(V) == 17
    d.problem(f"Practice {set_num}.2", q % "V", fig_letter(8, 5, V), "right", [15, 16, 17, 18, 20])
    key.append((f"{set_num}.2", "C", "Without the notch the shape is a 2 x 5 rectangle (10) plus two side triangles (each half of 2 x 5 = 5), so 20. The white triangle notch at the top is half of 2 x 3 = 3. 20 - 3 = 17."))

    M = [[(1, 0), (2, 0), (2, 5), (1, 5)], [(8, 0), (9, 0), (9, 5), (8, 5)],
         [(2, 5), (5, 2), (8, 5), (8, 3), (5, 0), (2, 3)]]
    assert letter_area(M) == 22
    d.problem(f"Practice {set_num}.3", q % "M", fig_letter(10, 5, M, 14), "right", [18, 20, 22, 24, 26])
    key.append((f"{set_num}.3", "C", "Two side bars: 5 + 5 = 10. The middle V is two slanted strips, each 3 across and 2 tall = 6. 10 + 6 + 6 = 22."))


# ------------------------------------------------- 2003 #18: Covering empty area in grid with 2 pieces
def fig_grid_black_white(grid_matrix, s=12):
    """Draw a grid of squares where 1=black, 0=white."""
    nr = len(grid_matrix)
    nc = len(grid_matrix[0])
    w = nc * s
    h = nr * s

    def draw(c, x, y):
        top = y + h
        c.setLineWidth(0.8)
        for r in range(nr):
            for col in range(nc):
                cx = x + col * s
                cy = top - (r + 1) * s
                if grid_matrix[r][col] == 1:
                    c.setFillColor(colors.black)
                    c.rect(cx, cy, s, s, stroke=1, fill=1)
                else:
                    c.setFillColor(colors.white)
                    c.rect(cx, cy, s, s, stroke=1, fill=1)

    return w, h, draw


def fig_polyomino_numbered(cells, num, s=11):
    """Draw a polyomino piece with a label number above or inside."""
    rs = [p[0] for p in cells]
    cs = [p[1] for p in cells]
    min_r, min_c = min(rs), min(cs)
    norm = {(r - min_r, c - min_c) for r, c in cells}
    nr = max(r for r, _ in norm) + 1
    nc = max(c for _, c in norm) + 1
    w = nc * s
    label_h = 13
    h = nr * s + label_h

    def draw(c, x, y):
        # Draw number label
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(x + w / 2, y + h - 10, f"Piece {num}")

        top = y + nr * s
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.Color(0.82, 0.82, 0.82))
        for r, col in norm:
            cx = x + col * s
            cy = top - (r + 1) * s
            c.rect(cx, cy, s, s, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_cover_two_pieces(empty_size, piece_sizes, opts, correct_idx):
    pair_sums = []
    for pair_str in opts:
        p1, p2 = [int(v) - 1 for v in pair_str.split("+")]
        pair_sums.append(piece_sizes[p1] + piece_sizes[p2])
    assert pair_sums[correct_idx] == empty_size, f"Expected {empty_size}, got {pair_sums[correct_idx]}"
    matches = [i for i, s in enumerate(pair_sums) if s == empty_size]
    assert matches == [correct_idx], f"Multiple matches: {matches}"


def q_2003_18(d, key, set_num=6, include_orig=True):
    d.heading(f"Set {set_num} - Covering an empty shape with two pieces", "Based on 2003, Problem 18")

    # Original 2003 #18: 7x7 grid with 15 empty cells.
    # Pieces: 1 (9), 2 (10), 3 (7), 4 (8).
    # Options: 1+3 (16), 2+4 (18), 2+3 (17), 1+4 (17), 3+4 (15) -> E
    empty_0 = 15
    pcs_sizes_0 = [9, 10, 7, 8]
    opts0 = ["1 and 3", "2 and 4", "2 and 3", "1 and 4", "3 and 4"]
    check_cover_two_pieces(empty_0, pcs_sizes_0, ["1+3", "2+4", "2+3", "1+4", "3+4"], 4)

    # 7x7 grid matrix: 1=black, 0=white (empty). Exactly 15 zeros.
    grid0_m = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid0_m) == 15

    # 4 pieces:
    p1_cells = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    p2_cells = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1)]
    p3_cells = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)]
    p4_cells = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]

    if include_orig:
        fig0 = hstack([
            fig_grid_black_white(grid0_m, s=12),
            hstack([
                fig_polyomino_numbered(p1_cells, 1, s=10),
                fig_polyomino_numbered(p2_cells, 2, s=10),
                fig_polyomino_numbered(p3_cells, 3, s=10),
                fig_polyomino_numbered(p4_cells, 4, s=10),
            ], gap=12),
        ], gap=18)
        d.problem(
            "Original 2003 #18.",
            "The picture shows a 7 × 7 square with some cells black and the rest white. We want to cover "
            "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
            "Which two pieces should we choose?",
            fig0,
            "below",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2003 #18",
            "E",
            "Counting the white cells in the 7 × 7 grid gives 15 empty cells. "
            "The pieces contain: Piece 1 = 9 squares, Piece 2 = 10 squares, Piece 3 = 7 squares, Piece 4 = 8 squares. "
            "Only Piece 3 and Piece 4 together have 7 + 8 = 15 squares to cover the white area.",
        ))

    # Practice .1: 6x6 grid, 14 empty cells. Pieces: 1(6), 2(8), 3(9), 4(7). Answer: A (1 and 2, 6+8=14)
    opts1 = ["1 and 2", "1 and 3", "2 and 4", "3 and 4", "2 and 3"]
    check_cover_two_pieces(14, [6, 8, 9, 7], ["1+2", "1+3", "2+4", "3+4", "2+3"], 0)
    grid1_m = [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid1_m) == 14
    p1_1 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    p1_2 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    p1_3 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    p1_4 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)]
    fig1 = hstack([
        fig_grid_black_white(grid1_m, s=12),
        hstack([
            fig_polyomino_numbered(p1_1, 1, s=10),
            fig_polyomino_numbered(p1_2, 2, s=10),
            fig_polyomino_numbered(p1_3, 3, s=10),
            fig_polyomino_numbered(p1_4, 4, s=10),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.1",
        "The picture shows a 6 × 6 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig1,
        "below",
        opts1,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "A",
        "Counting the white cells gives 14 empty cells. The pieces have 6, 8, 9, and 7 squares. "
        "Only Piece 1 and Piece 2 have 6 + 8 = 14 squares.",
    ))

    # Practice .2: 6x6 grid, 13 empty cells. Pieces: 1(5), 2(7), 3(8), 4(9). Answer: C (1 and 3, 5+8=13)
    opts2 = ["1 and 2", "2 and 3", "1 and 3", "2 and 4", "3 and 4"]
    check_cover_two_pieces(13, [5, 7, 8, 9], ["1+2", "2+3", "1+3", "2+4", "3+4"], 2)
    grid2_m = [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
    ]
    assert sum(row.count(0) for row in grid2_m) == 13
    p2_1 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    p2_2 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)]
    p2_3 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    p2_4 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    fig2 = hstack([
        fig_grid_black_white(grid2_m, s=12),
        hstack([
            fig_polyomino_numbered(p2_1, 1, s=10),
            fig_polyomino_numbered(p2_2, 2, s=10),
            fig_polyomino_numbered(p2_3, 3, s=10),
            fig_polyomino_numbered(p2_4, 4, s=10),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.2",
        "The picture shows a 6 × 6 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig2,
        "below",
        opts2,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "C",
        "Counting the white cells gives 13 empty cells. The pieces have 5, 7, 8, and 9 squares. "
        "Only Piece 1 and Piece 3 have 5 + 8 = 13 squares.",
    ))

    # Practice .3: 5x5 grid, 11 empty cells. Pieces: 1(4), 2(5), 3(6), 4(8). Answer: D (2 and 3, 5+6=11)
    opts3 = ["1 and 2", "1 and 4", "2 and 4", "2 and 3", "3 and 4"]
    check_cover_two_pieces(11, [4, 5, 6, 8], ["1+2", "1+4", "2+4", "2+3", "3+4"], 3)
    grid3_m = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
    ]
    assert sum(row.count(0) for row in grid3_m) == 11
    p3_1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    p3_2 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    p3_3 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    p3_4 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    fig3 = hstack([
        fig_grid_black_white(grid3_m, s=13),
        hstack([
            fig_polyomino_numbered(p3_1, 1, s=11),
            fig_polyomino_numbered(p3_2, 2, s=11),
            fig_polyomino_numbered(p3_3, 3, s=11),
            fig_polyomino_numbered(p3_4, 4, s=11),
        ], gap=12),
    ], gap=18)
    d.problem(
        f"Practice {set_num}.3",
        "The picture shows a 5 × 5 square with some cells black and the rest white. We want to cover "
        "the white area completely without overlaps using two of the numbered pieces (1, 2, 3, 4). "
        "Which two pieces should we choose?",
        fig3,
        "below",
        opts3,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "D",
        "Counting the white cells gives 11 empty cells. The pieces have 4, 5, 6, and 8 squares. "
        "Only Piece 2 and Piece 3 have 5 + 6 = 11 squares.",
    ))


# ------------------------------------------------- 2007 #1: Forking roads
def valid_fork_groups(forks):
    """Given a list of forks (e.g. [(1, 2), (3, 4), (5, 6)]), return all valid tuples picking 1 per fork."""
    res = [()]
    for branch in forks:
        res = [prev + (item,) for prev in res for item in branch]
    return set(res)


def check_fork_road(forks, option_tuples, answer_idx):
    valid = valid_fork_groups(forks)
    good = [i for i, opt in enumerate(option_tuples) if tuple(opt) in valid]
    assert good == [answer_idx], (forks, good, answer_idx)


def fig_fork_road(forks):
    """Draw a walker on the left and a sequence of road forks with labels."""
    n = len(forks)
    seg_w = 88
    lead_w = 24
    walker_w = 24
    W = walker_w + lead_w + n * seg_w
    H = 54

    def draw(c, x, y):
        cy = y + H / 2
        c.setLineWidth(1.2)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.black)

        # Draw little walker on the left
        wx = x + 10
        c.circle(wx, cy + 11, 3.2, stroke=1, fill=0)  # head
        c.line(wx, cy + 7.8, wx, cy + 2)               # neck/torso
        c.line(wx - 6, cy + 5, wx + 6, cy + 8)         # arms
        p = c.beginPath()                              # skirt/dress
        p.moveTo(wx, cy + 2)
        p.lineTo(wx - 5, cy - 6)
        p.lineTo(wx + 5, cy - 6)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.line(wx - 2.5, cy - 6, wx - 2.5, cy - 12)    # left leg
        c.line(wx + 2.5, cy - 6, wx + 2.5, cy - 12)    # right leg

        # Road parameters
        rh = 5.5   # half-width of main road
        bh = 13.0  # vertical offset of top/bottom branch centerlines
        rx = x + walker_w

        # Initial straight road segment
        c.line(rx, cy + rh, rx + lead_w, cy + rh)
        c.line(rx, cy - rh, rx + lead_w, cy - rh)
        cx = rx + lead_w

        for branch in forks:
            # Outer boundary curves (top and bottom of road)
            f_len = 66
            s_len = seg_w - f_len
            mid = cx + f_len / 2
            end = cx + f_len

            # Top outer & inner walls of upper branch, bottom outer & inner walls of lower branch
            for sign in (+1, -1):
                # Outer wall: from cy + sign*rh up to cy + sign*(bh + 4.5) and back
                p_out = c.beginPath()
                p_out.moveTo(cx, cy + sign * rh)
                p_out.curveTo(cx + 16, cy + sign * rh, mid - 14, cy + sign * (bh + 4.5), mid, cy + sign * (bh + 4.5))
                p_out.curveTo(mid + 14, cy + sign * (bh + 4.5), end - 16, cy + sign * rh, end, cy + sign * rh)
                c.drawPath(p_out, stroke=1, fill=0)

                # Inner island wall: from (cx + 7, cy) to (mid, cy + sign*(bh - 4.5)) to (end - 7, cy)
                p_in = c.beginPath()
                p_in.moveTo(cx + 7, cy)
                p_in.curveTo(cx + 18, cy + sign * 2, mid - 12, cy + sign * (bh - 4.5), mid, cy + sign * (bh - 4.5))
                p_in.curveTo(mid + 12, cy + sign * (bh - 4.5), end - 18, cy + sign * 2, end - 7, cy)
                c.drawPath(p_in, stroke=1, fill=0)

            # White label boxes and bold labels at top (branch[0]) and bottom (branch[1])
            for idx_b, sign in ((0, +1), (1, -1)):
                ly = cy + sign * bh
                c.setFillColor(colors.white)
                c.rect(mid - 5.5, ly - 5.5, 11, 11, stroke=0, fill=1)
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(mid, ly - 3.5, str(branch[idx_b]))

            # Straight connector to next fork
            c.line(end, cy + rh, end + s_len, cy + rh)
            c.line(end, cy - rh, end + s_len, cy - rh)
            cx = end + s_len

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return W, H, draw


def q_2007_1(d, key, set_num=1, include_orig=True):
    d.heading(f"Set {set_num} - Choosing paths along a road", "Based on 2007, Problem 1")

    # Original 2007 #1
    if include_orig:
        forks = [(1, 2), (3, 4), (5, 6)]
        opts = [(1, 2, 4), (2, 3, 4), (2, 3, 5), (1, 5, 6), (1, 2, 5)]
        check_fork_road(forks, opts, 2)
        d.problem(
            "Original 2007 #1.",
            "Zita walked from the left to the right and wrote the numbers she saw along the roads in her "
            "notepad. Which of the following groups of numbers could be the numbers written by Zita?",
            fig_fork_road(forks),
            "below",
            [f"{a}, {b} and {c}" for a, b, c in opts],
            choice_cols=3,
        )
        key.append((
            "2007 #1",
            "C",
            "At the 1st fork Zita picks 1 or 2; at the 2nd fork 3 or 4; at the 3rd fork 5 or 6. Only (2, 3 and 5) has one from each fork.",
        ))

    # Practice .1
    forks1 = [(1, 2), (3, 4), (5, 6)]
    opts1 = [(1, 2, 3), (1, 4, 6), (2, 3, 4), (1, 5, 6), (3, 4, 5)]
    check_fork_road(forks1, opts1, 1)
    d.problem(
        f"Practice {set_num}.1",
        "Leo walked from the left to the right along the roads and wrote down the three numbers he passed. "
        "Which group of numbers could Leo have written?",
        fig_fork_road(forks1),
        "below",
        [f"{a}, {b} and {c}" for a, b, c in opts1],
        choice_cols=3,
    )
    key.append((
        f"{set_num}.1",
        "B",
        "Leo must pick one from (1, 2), one from (3, 4), and one from (5, 6). Only (1, 4 and 6) picks one from each fork.",
    ))

    # Practice .2 (letters on the forks)
    forks2 = [("A", "B"), ("C", "D"), ("E", "F")]
    opts2 = [("A", "B", "E"), ("B", "C", "D"), ("A", "E", "F"), ("B", "D", "E"), ("C", "D", "F")]
    check_fork_road(forks2, opts2, 3)
    d.problem(
        f"Practice {set_num}.2",
        "Mia walked from left to right and wrote down the letters she passed along her path. "
        "Which three letters could Mia have written?",
        fig_fork_road(forks2),
        "below",
        [f"{a}, {b} and {c}" for a, b, c in opts2],
        choice_cols=3,
    )
    key.append((
        f"{set_num}.2",
        "D",
        "Mia picks A or B first, then C or D, then E or F. Only (B, D and E) has one letter from each fork.",
    ))

    # Practice .3 (twist: sum of the numbers along the road)
    forks3 = [(2, 5), (3, 6), (4, 8)]
    valid_sums = {a + b + c for a, b, c in valid_fork_groups(forks3)}  # {9, 13, 12, 16, 15, 19}
    sum_choices = [10, 11, 14, 16, 20]
    good_sums = [i for i, s in enumerate(sum_choices) if s in valid_sums]
    assert good_sums == [3], (valid_sums, good_sums)
    d.problem(
        f"Practice {set_num}.3",
        "Sam walked from left to right and <b>added up</b> the three numbers he passed along his road. "
        "Which of the following could be Sam's total?",
        fig_fork_road(forks3),
        "below",
        sum_choices,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "D",
        "Possible sums are 2+3+4=9, 2+6+4=12, 5+3+4=12, 2+3+8=13, 5+6+4=15, 2+6+8=16, 5+3+8=16, 5+6+8=19. From the choices, only 16 is possible (for example 2 + 6 + 8 = 16).",
    ))



# ------------------------------------------------- 2007 #8: Fitting piece to form a rectangle
def poly_cells_from_grid(grid):
    cells = set()
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == 1:
                cells.add((r, c))
    return cells


def get_poly_rotations(cells):
    rots = []
    current = cells
    for _ in range(4):
        min_r = min(r for r, c in current)
        min_c = min(c for r, c in current)
        norm = frozenset((r - min_r, c - min_c) for r, c in current)
        if norm not in rots:
            rots.append(norm)
        current = set((c, -r) for r, c in current)
    return rots


def can_form_rect(given_cells, cand_cells):
    for rot in get_poly_rotations(cand_cells):
        for dr in range(-8, 9):
            for dc in range(-8, 9):
                trans = set((r + dr, c + dc) for r, c in rot)
                if not (given_cells & trans):
                    union = given_cells | trans
                    min_r = min(r for r, c in union)
                    max_r = max(r for r, c in union)
                    min_c = min(c for r, c in union)
                    max_c = max(c for r, c in union)
                    h = max_r - min_r + 1
                    w = max_c - min_c + 1
                    if len(union) == h * w:
                        return True
    return False


def check_fit_rectangle(given_grid, opt_grids, correct_idx):
    g_cells = poly_cells_from_grid(given_grid)
    results = [can_form_rect(g_cells, poly_cells_from_grid(opt)) for opt in opt_grids]
    assert results[correct_idx] is True, f"Correct choice {correct_idx} failed to form rectangle!"
    matches = [i for i, r in enumerate(results) if r]
    assert matches == [correct_idx], f"Expected unique match at {correct_idx}, got {matches}"


def fig_poly_grid(grid, s=11, label=None):
    """Draw a polyomino defined by binary 2D grid."""
    nr = len(grid)
    nc = len(grid[0])
    w = nc * s
    label_h = 13 if label else 0
    h = nr * s + label_h

    def draw(c, x, y):
        if label:
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawCentredString(x + w / 2, y + h - 10, label)

        top = y + nr * s
        c.setLineWidth(0.9)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.Color(0.85, 0.85, 0.85))
        for r in range(nr):
            for col in range(nc):
                if grid[r][col] == 1:
                    cx = x + col * s
                    cy = top - (r + 1) * s
                    c.rect(cx, cy, s, s, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def q_2007_8(d, key, set_num=7, include_orig=True):
    d.heading(f"Set {set_num} - Joining pieces to form a rectangle", "Based on 2007, Problem 8")

    # Original 2007 #8:
    # Given shape: column heights [5, 2, 1] (8 cells)
    # Piece B: column heights [5, 4, 1] (10 cells). Rotated 180 -> forms 6x3 rectangle (18 cells).
    g0 = [[1, 1, 1], [1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]
    opts0 = [
        [[1, 1, 1], [1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]],
        [[1, 1, 1], [1, 1, 0], [1, 1, 0], [1, 1, 0], [1, 0, 0]],
        [[1, 1], [1, 1], [1, 1], [1, 1], [0, 1]],
        [[1, 1, 1], [0, 1, 1], [0, 0, 1]],
        [[1, 1, 1], [0, 1, 1], [0, 1, 1], [0, 0, 1]],
    ]
    check_fit_rectangle(g0, opts0, 1)

    if include_orig:
        fig0 = vstack([
            fig_poly_grid(g0, s=12, label="Given piece"),
            option_row([fig_poly_grid(opt, s=12) for opt in opts0], gap=16),
        ], gap=12)
        d.problem(
            "Original 2007 #8.",
            "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
            fig0,
            "below",
        )
        key.append((
            "2007 #8",
            "B",
            "The given shape has column heights 5, 2, and 1 (8 squares in total). Shape B has column heights "
            "5, 4, and 1 (10 squares in total). Turning shape B upside-down gives heights 1, 4, and 5. "
            "Fitting them together gives column heights (5+1=6, 2+4=6, 1+5=6), forming a solid 6 × 3 rectangle.",
        ))

    # Practice .1: given heights [4, 1] (5 cells). Joined with [4, 1] rotated 180 to form 5x2 rectangle. Answer: A
    g1 = [[1, 1], [1, 0], [1, 0], [1, 0]]
    opts1 = [
        [[1, 1], [1, 0], [1, 0], [1, 0]],
        [[1, 1], [1, 1], [1, 0]],
        [[1, 1, 1], [1, 1, 0]],
        [[1, 1], [1, 1]],
        [[1, 1], [1, 0], [1, 0]],
    ]
    check_fit_rectangle(g1, opts1, 0)
    fig1 = vstack([
        fig_poly_grid(g1, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts1], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.1",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
        fig1,
        "below",
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The given shape has column heights 4 and 1 (5 squares). Shape A is identical; turned upside-down "
        "it has column heights 1 and 4. Joining them gives columns of height 4+1=5 each, creating a 5 × 2 rectangle.",
    ))

    # Practice .2: given col heights [3, 1, 1] (5 cells). Joined with 2x2 square (4 cells) to form 3x3 square! Answer: B
    g2 = [[1, 1, 1], [1, 0, 0], [1, 0, 0]]
    opts2 = [
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1, 1, 1]],
        [[1, 1], [0, 1], [0, 1]],
    ]
    check_fit_rectangle(g2, opts2, 1)
    fig2 = vstack([
        fig_poly_grid(g2, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts2], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.2",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid square (or rectangle) without gaps or overlaps?",
        fig2,
        "below",
    )
    key.append((
        f"{set_num}.2",
        "B",
        "The given shape has 5 squares forming a corner inside a 3 × 3 boundary. "
        "A 2 × 2 square (shape B, 4 squares) fits into the empty corner to complete a solid 3 × 3 square.",
    ))

    # Practice .3: given col heights [3, 2, 1] (6 cells). Joined with [3, 2, 1] rotated 180 to form 4x3 rectangle. Answer: C
    g3 = [[1, 1, 1], [1, 1, 0], [1, 0, 0]]
    opts3 = [
        [[1, 1], [1, 1], [1, 1]],
        [[1, 1, 1], [1, 1, 1]],
        [[1, 1, 1], [1, 1, 0], [1, 0, 0]],
        [[1, 1, 1, 1], [1, 1, 0, 0]],
        [[1, 1, 1], [1, 1, 0], [0, 1, 0]],
    ]
    check_fit_rectangle(g3, opts3, 2)
    fig3 = vstack([
        fig_poly_grid(g3, s=12, label="Given piece"),
        option_row([fig_poly_grid(opt, s=12) for opt in opts3], gap=16),
    ], gap=12)
    d.problem(
        f"Practice {set_num}.3",
        "Which of the shapes (A through E) can be joined together with the given shape to form a solid rectangle without gaps or overlaps?",
        fig3,
        "below",
    )
    key.append((
        f"{set_num}.3",
        "C",
        "The given staircase shape has column heights 3, 2, and 1 (6 squares). "
        "Shape C is the same staircase; turned upside-down it has column heights 1, 2, and 3. "
        "Joined together, every column has height 4, forming a solid 4 × 3 rectangle of 12 squares.",
    ))


# ------------------------------------------------- Set 8: 2007 #14 Aquarium & 3D cubes
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


# ------------------------------------------------- Set 9: 2007 #10 Mini-Sudoku (3x3 Latin Square)
def fig_mini_sudoku(grid, s=26):
    w = 3 * s + 8
    h = 3 * s + 8

    def draw(c, x, y):
        ox = x + 4
        oy = y + 4

        # Draw cells
        for r in range(3):
            for col in range(3):
                cy = oy + (2 - r) * s
                cx = ox + col * s

                val = grid[r][col]
                if val in ("A", "B"):
                    c.setFillColor(colors.Color(0.9, 0.9, 0.9))
                    c.rect(cx, cy, s, s, fill=1, stroke=0)

                # Draw cell borders
                c.setStrokeColor(colors.black)
                c.setLineWidth(1.0)
                c.rect(cx, cy, s, s, fill=0, stroke=1)

                # Draw text
                if val is not None:
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(cx + s / 2, cy + s / 2 - 5, str(val))

        # Outer thick border
        c.setLineWidth(2.0)
        c.setStrokeColor(colors.black)
        c.rect(ox, oy, 3 * s, 3 * s, fill=0, stroke=1)

        # Always reset canvas colors
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


LATIN_3X3 = []
for _r0 in itertools.permutations([1, 2, 3]):
    for _r1 in itertools.permutations([1, 2, 3]):
        for _r2 in itertools.permutations([1, 2, 3]):
            _b = [_r0, _r1, _r2]
            if all(len(set(_b[r][c] for r in range(3))) == 3 for c in range(3)):
                LATIN_3X3.append(_b)


def check_mini_sudoku(grid, choices, answer_idx, question_type="single_cell"):
    fixed = {}
    positions = {}
    for r in range(3):
        for c in range(3):
            v = grid[r][c]
            if v in ("1", "2", "3"):
                fixed[(r, c)] = int(v)
            elif v is not None:
                positions[v] = (r, c)

    matching = [b for b in LATIN_3X3 if all(b[r][c] == val for (r, c), val in fixed.items())]
    assert len(matching) > 0, "No valid mini-sudoku solution for this board!"

    if question_type == "single_cell":
        qr, qc = positions["?"]
        vals = sorted(list(set(b[qr][qc] for b in matching)))
        if vals == [1]:
            expected = "only 1"
        elif vals == [2]:
            expected = "only 2"
        elif vals == [3]:
            expected = "only 3"
        elif vals == [1, 2]:
            expected = "1 or 2"
        elif vals == [2, 3]:
            expected = "2 or 3"
        elif vals == [1, 3]:
            expected = "1 or 3"
        elif vals == [1, 2, 3]:
            expected = "1, 2 or 3"
        else:
            raise ValueError(f"Unexpected values: {vals}")

        assert choices[answer_idx] == expected, f"Expected {expected}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if ch == expected]
        assert matches == [answer_idx], f"Multiple or no choices match {expected}: {matches}"

    elif question_type == "sum_cells":
        ar, ac = positions["A"]
        br, bc = positions["B"]
        sums = set(b[ar][ac] + b[br][bc] for b in matching)
        assert len(sums) == 1, f"Multiple possible sums: {sums}"
        val = sums.pop()
        assert choices[answer_idx] == val, f"Expected {val}, got {choices[answer_idx]}"
        matches = [i for i, ch in enumerate(choices) if ch == val]
        assert matches == [answer_idx], f"Multiple or no choices match {val}: {matches}"


def q_2007_10(d, key, set_num=1, include_orig=True):
    d.heading(
        f"Problem {set_num}: 2007 #10 - Mini-Sudoku",
        "Arranging numbers 1, 2, and 3 in a 3×3 square (Latin square logic)",
    )

    # Original 2007 #10
    if include_orig:
        G0 = [
            ["1", "?", None],
            ["2", "1", None],
            [None, None, None],
        ]
        opts0 = ["only 1", "only 2", "only 3", "2 or 3", "1, 2 or 3"]
        check_mini_sudoku(G0, opts0, 2)
        d.problem(
            "2007 #10",
            "The square in the figure is a <i>mini-sudoku</i>: the numbers 1, 2, and 3 must be "
            "written in the cells so that each of them appears in each row and in each column. "
            "Harry started to fill in the square. Which number should he write in the cell "
            "that is marked by a question mark (?) ?",
            fig_mini_sudoku(G0),
            "right",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2007 #10",
            "C",
            "In a 3 × 3 mini-sudoku, each row and column must contain the numbers 1, 2, and 3 exactly once. "
            "The middle row already has 2 and 1, so its third cell must be 3. The first column has 1 and 2, "
            "so its bottom cell must be 3. Now look at the top row: the first cell is 1, so the question mark "
            "and top-right cell must be 2 and 3. But column 3 already has 3 in the middle row, so the top-right "
            "cell cannot be 3 (it must be 2). Therefore, the question mark cell must be 3 (only 3).",
        ))

    # Practice .1 (Answer: A) only 1)
    G1 = [
        ["?", "2", None],
        ["2", "3", None],
        [None, None, None],
    ]
    opts1 = ["only 1", "only 2", "only 3", "1 or 2", "1, 2 or 3"]
    check_mini_sudoku(G1, opts1, 0)
    d.problem(
        f"Practice {set_num}.1",
        "The square in the figure is a <i>mini-sudoku</i>: each row and each column must contain "
        "the numbers 1, 2, and 3 exactly once. Leo started to fill in the square as shown. "
        "Which number should he write in the cell marked by a question mark (?) ?",
        fig_mini_sudoku(G1),
        "right",
        opts1,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.1",
        "A",
        "The middle row has 2 and 3, so its third cell must be 1. The middle column has 2 and 3, "
        "so its bottom cell must be 1. In the top row, the middle cell is 2, so the remaining two cells "
        "(the question mark and the top-right cell) must be 1 and 3. If the question mark were 3, "
        "the top-right cell would be 1, but column 3 already has 1 in the middle row! "
        "Thus, the question mark cannot be 3. It must be 1 (only 1).",
    ))

    # Practice .2 (Answer: D) 2 or 3)
    G2 = [
        ["1", "?", None],
        ["2", None, None],
        [None, None, None],
    ]
    opts2 = ["only 1", "only 2", "only 3", "2 or 3", "1, 2 or 3"]
    check_mini_sudoku(G2, opts2, 3)
    d.problem(
        f"Practice {set_num}.2",
        "Maya started filling in the 3×3 mini-sudoku square using the numbers 1, 2, and 3. "
        "Each number must appear once in every row and once in every column. "
        "Which number(s) could Maya write in the cell marked by a question mark (?) ?",
        fig_mini_sudoku(G2),
        "right",
        opts2,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.2",
        "D",
        "Column 1 already has 1 and 2, so its bottom cell must be 3. Row 1 has 1 in the first cell, "
        "so the remaining cells in the top row must be 2 and 3 in some order. Both completions are valid: "
        "if ? is 2, the board can be completed with rows [1, 2, 3], [2, 3, 1], [3, 1, 2]; "
        "if ? is 3, the board can be completed with rows [1, 3, 2], [2, 1, 3], [3, 2, 1]. "
        "Therefore, Maya can write 2 or 3.",
    ))

    # Practice .3 (Twist: Sum of two marked cells A and B; Answer: B) 6)
    G3 = [
        ["1", "A", None],
        ["3", "2", None],
        [None, None, "B"],
    ]
    opts3 = [3, 6, 4, 5, 7]
    check_mini_sudoku(G3, opts3, 1, question_type="sum_cells")
    d.problem(
        f"Practice {set_num}.3",
        "Lucas filled in the mini-sudoku square with numbers 1, 2, and 3 so that each number appears "
        "in each row and in each column. Two cells are marked with letters A and B (see picture). "
        "What is the sum of the numbers in cells A and B?",
        fig_mini_sudoku(G3),
        "right",
        opts3,
        choice_cols=5,
    )
    key.append((
        f"{set_num}.3",
        "B",
        "The middle row has 3 and 2, so its third cell must be 1. The first column has 1 and 3, "
        "so its bottom cell must be 2. In the third column, the middle cell is 1, so the other two cells "
        "(top-right and bottom-right B) must be 2 and 3. Since the bottom row already has 2 in the first column, "
        "cell B cannot be 2; B must be 3 (making the top-right cell 2). Now in the top row, the numbers are "
        "1, A, and 2, so cell A must be 3. Therefore, the sum of the numbers in cells A and B is 3 + 3 = 6.",
    ))


# ------------------------------------------------- Set 10: 2002 #10 Digit occurrences in house numbers
def fig_house_street(first_num, second_num, last_num, target_digit):
    """Draw a compact row of three little houses showing the numbering range first_num, second_num, ..., last_num."""
    w = 136
    h = 46

    def draw_house(c, hx, hy, label):
        bw, bh = 28, 22
        roof_h = 12
        # House body
        c.setFillColor(colors.Color(0.93, 0.93, 0.93))
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.1)
        c.rect(hx, hy, bw, bh, stroke=1, fill=1)
        # Roof triangle
        p = c.beginPath()
        p.moveTo(hx - 3, hy + bh)
        p.lineTo(hx + bw / 2, hy + bh + roof_h)
        p.lineTo(hx + bw + 3, hy + bh)
        p.close()
        c.setFillColor(colors.Color(0.78, 0.78, 0.78))
        c.drawPath(p, stroke=1, fill=1)
        # Number plaque inside house
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(hx + bw / 2, hy + 7, str(label))

    def draw(c, x, y):
        by = y + 6
        draw_house(c, x + 4, by, first_num)
        draw_house(c, x + 40, by, second_num)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 83, by + 9, "...")
        draw_house(c, x + 98, by, last_num)
        # Ground line
        c.setLineWidth(0.9)
        c.setStrokeColor(colors.black)
        c.line(x, by, x + w - 4, by)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_digit_occurrences(start_num, end_num, digit, choices, answer_idx, mode="occurrences"):
    d_str = str(digit)
    if mode == "occurrences":
        val = sum(str(n).count(d_str) for n in range(start_num, end_num + 1))
    elif mode == "houses_with_digit":
        val = sum(1 for n in range(start_num, end_num + 1) if d_str in str(n))
    else:
        raise ValueError(f"Unknown mode: {mode}")
    assert choices[answer_idx] == val, f"Expected {val} at index {answer_idx}, got {choices[answer_idx]}"
    matches = [i for i, ch in enumerate(choices) if ch == val]
    assert matches == [answer_idx], f"Expected unique match at {answer_idx}, got {matches}"


def q_2002_10(d, key, set_num=1, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #10 - Digit Occurrences in House Numbers",
        "Counting how many times a digit appears across a sequential range of numbers",
    )

    if include_orig:
        opts0 = [2, 4, 8, 16, 32]
        check_digit_occurrences(1, 24, 2, opts0, 2)
        d.problem(
            "2002 #10",
            "Joseph lives on a short street where the houses are numbered sequentially from 1 to 24. "
            "How many times does the digit 2 occur in the numbers of those houses?",
            fig_house_street(1, 2, 24, 2),
            "right",
            opts0,
            choice_cols=5,
        )
        key.append((
            "2002 #10",
            "C",
            "List the house numbers from 1 to 24 that contain the digit 2: "
            "2, 12, 20, 21, 22, 23, and 24. Notice that house number 22 contains two 2s! "
            "Counting every digit 2 gives 1 + 1 + 1 + 1 + 2 + 1 + 1 = 8 times.",
        ))

    practices = [
        # Practice .1 (Answer: A) 10)
        (
            1, 35, 3, [10, 8, 9, 11, 12], 0, "occurrences",
            "Sophia lives on Maple Street where the houses are numbered sequentially from 1 to 35. "
            "How many times does the digit 3 occur in the numbers of those houses?",
            "In the ones place, the digit 3 appears in 3, 13, 23, and 33 (4 times). "
            "In the tens place, the digit 3 appears in 30, 31, 32, 33, 34, and 35 (6 times). "
            "In total, the digit 3 occurs 4 + 6 = 10 times (counting both 3s in 33).",
        ),
        # Practice .2 (Answer: B) 7)
        (
            1, 42, 4, [6, 7, 8, 9, 14], 1, "occurrences",
            "A puzzle booklet has its pages numbered sequentially from 1 to 42. "
            "How many times does the digit 4 occur in the page numbers?",
            "In the ones place, the digit 4 appears in 4, 14, 24, and 34 (4 times). "
            "In the tens place, the digit 4 appears in 40, 41, and 42 (3 times). "
            "In total, the digit 4 occurs 4 + 3 = 7 times.",
        ),
        # Practice .3 (Answer: D) 13)
        (
            1, 29, 1, [11, 12, 14, 13, 15], 3, "occurrences",
            "The lockers in a school hallway are numbered sequentially from 1 to 29. "
            "How many times does the digit 1 occur in the numbers of those lockers?",
            "In the ones place, the digit 1 appears in 1, 11, and 21 (3 times). "
            "In the tens place, the digit 1 appears in all ten numbers from 10 to 19 (10 times). "
            "In total, the digit 1 occurs 3 + 10 = 13 times (with 11 contributing two 1s).",
        ),
        # Practice .4 (Answer: E) 12)
        (
            10, 30, 2, [9, 10, 11, 13, 12], 4, "occurrences",
            "The seats in a theater row are numbered sequentially from 10 to 30. "
            "How many times does the digit 2 occur in the numbers of those seats?",
            "Between 10 and 30, the digit 2 appears in the ones place in 12 and 22 (2 times), "
            "and in the tens place in every number from 20 to 29 (10 times). "
            "In total, the digit 2 occurs 2 + 10 = 12 times.",
        ),
        # Practice .5 (Answer: A) 12)
        (
            1, 55, 5, [12, 10, 11, 13, 15], 0, "occurrences",
            "Noah paints house numbers on all the doors along Oak Avenue, numbered sequentially from 1 to 55. "
            "How many times does Noah paint the digit 5?",
            "In the ones place, the digit 5 appears in 5, 15, 25, 35, 45, and 55 (6 times). "
            "In the tens place, the digit 5 appears in 50, 51, 52, 53, 54, and 55 (6 times). "
            "Altogether, Noah paints the digit 5 a total of 6 + 6 = 12 times.",
        ),
    ]

    for idx, (s_num, e_num, dig, opts, ans_idx, mode, text, expl) in enumerate(practices[:num_practice], start=1):
        check_digit_occurrences(s_num, e_num, dig, opts, ans_idx, mode=mode)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_house_street(s_num, s_num + 1, e_num, dig),
            "right",
            opts,
            choice_cols=5,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set 11: 2002 #11 Cracked Clock Face
def fig_cracked_clock(cracks, R=33):
    """Draw a clock face (1..12) with cracks specified as lists of (r_frac, clock_pos) points."""
    pad = 4
    w = 2 * R + 2 * pad
    h = 2 * R + 2 * pad

    def draw(c, x, y):
        cx = x + pad + R
        cy = y + pad + R

        def pt(r_frac, clock_pos):
            ang = math.radians(90.0 - clock_pos * 30.0)
            return cx + r_frac * R * math.cos(ang), cy + r_frac * R * math.sin(ang)

        # Outer clock circle
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.2)
        c.circle(cx, cy, R, stroke=1, fill=1)

        # Clock numbers 1..12
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 7.8)
        r_num = 0.78
        for hr in range(1, 13):
            px, py = pt(r_num, hr)
            c.drawCentredString(px, py - 2.8, str(hr))

        # Crack lines
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.95)

        def bezier_ctrl(crack):
            (r1, p1), (rm, pm), (r2, p2) = crack
            x1, y1 = pt(r1, p1)
            xm, ym = pt(rm, pm)
            x2, y2 = pt(r2, p2)
            ix1, iy1 = pt(0.46 if r1 >= 0.95 else r1, p1)
            ix2, iy2 = pt(0.46 if r2 >= 0.95 else r2, p2)
            cx1 = 0.62 * ix1 + 0.38 * xm
            cy1 = 0.62 * iy1 + 0.38 * ym
            cx2 = 0.62 * ix2 + 0.38 * xm
            cy2 = 0.62 * iy2 + 0.38 * ym
            return (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)

        def eval_bezier(bpts, t):
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = bpts
            u = 1.0 - t
            bx = (u ** 3) * x0 + 3 * (u ** 2) * t * x1 + 3 * u * (t ** 2) * x2 + (t ** 3) * x3
            by = (u ** 3) * y0 + 3 * (u ** 2) * t * y1 + 3 * u * (t ** 2) * y2 + (t ** 3) * y3
            return bx, by

        drawn_beziers = []
        for crack in cracks:
            if isinstance(crack[0], str) and crack[0] == "branch":
                _, parent_idx, t_val, (r2, p2) = crack
                bx, by = eval_bezier(drawn_beziers[parent_idx], t_val)
                x2, y2 = pt(r2, p2)
                c.line(bx, by, x2, y2)
            elif len(crack) == 2:
                (r1, p1), (r2, p2) = crack
                c.line(*pt(r1, p1), *pt(r2, p2))
                drawn_beziers.append(None)
            elif len(crack) == 3:
                bpts = bezier_ctrl(crack)
                drawn_beziers.append(bpts)
                (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = bpts
                path = c.beginPath()
                path.moveTo(x1, y1)
                path.curveTo(cx1, cy1, cx2, cy2, x2, y2)
                c.drawPath(path, stroke=1, fill=0)
            else:
                pts = [pt(rf, cp) for rf, cp in crack]
                path = c.beginPath()
                path.moveTo(*pts[0])
                for qx, qy in pts[1:]:
                    path.lineTo(qx, qy)
                c.drawPath(path, stroke=1, fill=0)
                drawn_beziers.append(None)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_cracked_clock(options_parts, expected_sums, answer_idx):
    """Verify each option partitions 1..12 and only answer_idx has piece sums matching expected_sums."""
    full_clock = list(range(1, 13))
    target_sorted = sorted(expected_sums)
    assert sum(target_sorted) == 78, f"Target sums {target_sorted} do not add to 78"
    matching = []
    for idx, parts in enumerate(options_parts):
        flat = sorted(x for p in parts for x in p)
        assert flat == full_clock, f"Option {idx} does not partition 1..12: {parts}"
        sums = sorted(sum(p) for p in parts)
        if sums == target_sorted:
            matching.append(idx)
    assert matching == [answer_idx], f"Expected unique match at {answer_idx} for sums {target_sorted}, got {matching}"


def q_2002_11(d, key, set_num=2, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #11 - Cracked Clock Face",
        "Partitioning the clock face (sum 1 + 2 + ... + 12 = 78) into pieces with given sum properties",
    )

    # Original 2002 #11: 4 pieces with consecutive sums (18, 19, 20, 21) -> Answer: C
    if include_orig:
        parts0 = [
            [[9, 10], [7, 8], [11, 5, 6], [12, 1, 2, 3, 4]],        # A: sums 19, 15, 22, 22
            [[11, 12], [7, 8, 9], [6], [10, 1, 2, 3, 4, 5]],        # B: sums 23, 24, 6, 25
            [[12, 1, 2, 3], [9, 10], [11, 4, 5], [6, 7, 8]],        # C: sums 18, 19, 20, 21
            [[10, 11], [9, 12, 1], [7, 8, 2, 3], [4, 5, 6]],        # D: sums 21, 22, 20, 15
            [[8, 9, 10, 11], [12, 1, 2, 3], [4, 5, 6, 7]],          # E: only 3 pieces (38, 18, 22)
        ]
        cracks0 = [
            # A: two cracks from top-left to bottom, short crack on left between 8 and 9
            [[(1.0, 10.55), (0.35, 8.5), (1.0, 6.45)], [(1.0, 11.45), (0.15, 8.0), (1.0, 4.55)], ("branch", 0, 0.52, (1.0, 8.5))],
            # B: top loop around 11,12; diagonal from 9.5 to 5.5; branch to 6.5
            [[(1.0, 10.5), (0.28, 11.5), (1.0, 0.5)], [(1.0, 9.5), (0.35, 7.2), (1.0, 5.5)], ("branch", 1, 0.62, (1.0, 6.5))],
            # C: 11.5 to 3.5; 10.5 to 5.5; branch from 8.5 to middle crack
            [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
            # D: loop around 10,11; diagonal 1.5 to 8.5; curve 3.5 to 6.5
            [[(1.0, 11.5), (0.28, 10.5), (1.0, 9.5)], [(1.0, 1.5), (0.05, 5.0), (1.0, 8.5)], [(1.0, 3.5), (0.32, 5.0), (1.0, 6.5)]],
            # E: 11.5 to 7.5; branch to 3.5
            [[(1.0, 11.5), (0.2, 9.5), (1.0, 7.5)], ("branch", 0, 0.5, (1.0, 3.5))],
        ]
        check_cracked_clock(parts0, [18, 19, 20, 21], 2)
        fig0 = option_row([fig_cracked_clock(cr) for cr in cracks0], gap=12)
        d.problem(
            "2002 #11",
            "The face of a clock is cracked into 4 pieces. The sums of the numbers within the parts are consecutive "
            "numbers. Provided there is only one possible way to crack it, the face would look like:",
            fig0,
            "below",
        )
        key.append((
            "2002 #11",
            "C",
            "The sum of all numbers on a clock face is 1 + 2 + ... + 12 = 78. Four consecutive numbers that add up "
            "to 78 must be 18, 19, 20, and 21 (since 18 + 19 + 20 + 21 = 78). In clock C, the four pieces contain "
            "{12, 1, 2, 3} = 18, {9, 10} = 19, {11, 4, 5} = 20, and {6, 7, 8} = 21.",
        ))

    practices = [
        # Practice .1: 3 pieces with equal sums (26, 26, 26) -> Answer: A
        (
            [
                [[11, 12, 1, 2], [9, 10, 3, 4], [5, 6, 7, 8]],          # A: 26, 26, 26
                [[12, 1, 2, 3], [10, 11, 4, 5], [6, 7, 8, 9]],          # B: 18, 30, 30
                [[10, 11, 12, 1], [8, 9, 2, 3], [4, 5, 6, 7]],          # C: 34, 22, 22
                [[11, 12, 1], [9, 10, 2, 3], [4, 5, 6, 7, 8]],          # D: 24, 24, 30
                [[11, 12, 1, 2], [10, 3, 4], [5, 6, 7, 8, 9]],          # E: 26, 17, 35
            ],
            [
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 4.5)]],
                [[(1.0, 11.5), (0.25, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.25, 7.5), (1.0, 5.5)]],
                [[(1.0, 9.5), (0.25, 11.5), (1.0, 1.5)], [(1.0, 7.5), (0.25, 5.5), (1.0, 3.5)]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 1.5)], [(1.0, 8.5), (0.25, 6.0), (1.0, 3.5)]],
                [[(1.0, 10.5), (0.25, 12.0), (1.0, 2.5)], [(1.0, 9.5), (0.25, 7.0), (1.0, 4.5)]],
            ],
            [26, 26, 26],
            0,
            "The face of a clock is cracked into 3 pieces so that the sums of the numbers on all 3 pieces are equal. "
            "Which clock face shows how it was cracked?",
            "Since the numbers 1 through 12 add up to 78, each of the 3 equal pieces must have a sum of 78 ÷ 3 = 26. "
            "In clock A, the top piece has 11 + 12 + 1 + 2 = 26, the middle piece has 9 + 10 + 3 + 4 = 26, "
            "and the bottom piece has 5 + 6 + 7 + 8 = 26.",
        ),
        # Practice .2: 3 pieces with consecutive sums (25, 26, 27) -> Answer: B
        (
            [
                [[11, 12, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10]],          # A: 26, 18, 34
                [[11, 12, 1, 2], [3, 4, 5, 6, 7], [8, 9, 10]],          # B: 26, 25, 27
                [[12, 1, 2, 3], [4, 5, 6, 7, 8], [9, 10, 11]],          # C: 18, 30, 30
                [[10, 11, 12], [1, 2, 3, 4, 5, 6], [7, 8, 9]],          # D: 33, 21, 24
                [[11, 12, 1], [2, 3, 4, 5, 6, 7], [8, 9, 10]],          # E: 24, 27, 27
            ],
            [
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
                [[(1.0, 9.5), (0.0, 0.0)], [(1.0, 0.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 1.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
            ],
            [25, 26, 27],
            1,
            "The face of a clock is cracked into 3 pieces meeting at the center. The sums of the numbers within the 3 parts "
            "are consecutive numbers. Which clock face shows how it was cracked?",
            "Three consecutive numbers that add up to 78 are 25, 26, and 27 (25 + 26 + 27 = 78). "
            "In clock B, the three pieces are {3, 4, 5, 6, 7} = 25, {11, 12, 1, 2} = 26, and {8, 9, 10} = 27.",
        ),
        # Practice .3: 2 pieces with equal sums (39, 39) -> Answer: D
        (
            [
                [[12, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11]],            # A: 27, 51
                [[11, 12, 1, 2, 3, 4], [5, 6, 7, 8, 9, 10]],            # B: 33, 45
                [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],            # C: 21, 57
                [[10, 11, 12, 1, 2, 3], [4, 5, 6, 7, 8, 9]],            # D: 39, 39
                [[9, 10, 11, 12, 1, 2], [3, 4, 5, 6, 7, 8]],            # E: 45, 33
            ],
            [
                [[(1.0, 11.5), (0.1, 2.5), (1.0, 5.5)]],
                [[(1.0, 10.5), (0.1, 1.5), (1.0, 4.5)]],
                [[(1.0, 0.5), (0.1, 3.5), (1.0, 6.5)]],
                [[(1.0, 9.5), (0.1, 12.5), (1.0, 3.5)]],
                [[(1.0, 8.5), (0.1, 11.5), (1.0, 2.5)]],
            ],
            [39, 39],
            3,
            "A clock face is cracked into 2 pieces by a single crack so that the sum of the numbers on one piece "
            "equals the sum of the numbers on the other piece. Which clock face shows this crack?",
            "Half of the total clock sum is 78 ÷ 2 = 39. In clock D, the crack goes between 9 and 10 on the left "
            "and between 3 and 4 on the right, giving {10, 11, 12, 1, 2, 3} = 39 and {4, 5, 6, 7, 8, 9} = 39.",
        ),
        # Practice .4: 4 pieces where two pieces sum to 18 and two pieces sum to 21 -> Answer: E
        (
            [
                [[12, 1, 2, 3], [11, 4, 5], [9, 10], [6, 7, 8]],        # A: 18, 20, 19, 21
                [[12, 1, 2], [11, 3, 4], [9, 10, 5], [6, 7, 8]],        # B: 15, 18, 24, 21
                [[11, 12, 1, 2], [10, 3, 4], [8, 9], [5, 6, 7]],        # C: 26, 17, 17, 18
                [[12, 1, 2, 3], [10, 11], [7, 8, 9], [4, 5, 6]],        # D: 18, 21, 24, 15
                [[12, 1, 2, 3], [10, 11], [8, 9, 4], [5, 6, 7]],        # E: 18, 21, 21, 18
            ],
            [
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 10.5), (0.28, 8.0), (1.0, 5.5)], ("branch", 1, 0.45, (1.0, 8.5))],
                [[(1.0, 11.5), (0.22, 1.0), (1.0, 2.5)], [(1.0, 10.5), (0.28, 7.5), (1.0, 4.5)], ("branch", 1, 0.50, (1.0, 8.5))],
                [[(1.0, 10.5), (0.22, 12.5), (1.0, 2.5)], [(1.0, 9.5), (0.28, 7.0), (1.0, 4.5)], ("branch", 1, 0.50, (1.0, 7.5))],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 9.5), (0.28, 6.5), (1.0, 3.5)], ("branch", 1, 0.52, (1.0, 6.5))],
                [[(1.0, 11.5), (0.22, 1.5), (1.0, 3.5)], [(1.0, 7.5), (0.28, 6.0), (1.0, 4.5)], ("branch", 0, 0.45, (1.0, 9.5))],
            ],
            [18, 18, 21, 21],
            4,
            "The face of a clock is cracked into 4 pieces so that two of the pieces each have a sum of 18, "
            "and the other two pieces each have a sum of 21. Which clock face shows this?",
            "In clock E, the top-right piece has {12, 1, 2, 3} = 18, the bottom piece has {5, 6, 7} = 18, "
            "the top-left piece has {10, 11} = 21, and the middle piece has {8, 9, 4} = 21.",
        ),
        # Practice .5: 4 pieces meeting at center with sums 15, 18, 21, 24 (increasing by 3) -> Answer: C
        (
            [
                [[12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],        # A: 15, 12, 21, 30
                [[11, 12, 1], [2, 3, 4], [5, 6, 7], [8, 9, 10]],        # B: 24, 9, 18, 27
                [[12, 1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]],        # C: 18, 15, 24, 21
                [[12, 1, 2, 3], [4, 5, 6, 7], [8, 9], [10, 11]],        # D: 18, 22, 17, 21
                [[11, 12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10]],        # E: 26, 12, 21, 19
            ],
            [
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 5.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 1.5), (0.0, 0.0)], [(1.0, 4.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 6.5), (0.0, 0.0)], [(1.0, 9.5), (0.0, 0.0)]],
                [[(1.0, 11.5), (0.0, 0.0)], [(1.0, 3.5), (0.0, 0.0)], [(1.0, 7.5), (0.0, 0.0)], [(1.0, 9.5), (0.0, 0.0)]],
                [[(1.0, 10.5), (0.0, 0.0)], [(1.0, 2.5), (0.0, 0.0)], [(1.0, 5.5), (0.0, 0.0)], [(1.0, 8.5), (0.0, 0.0)]],
            ],
            [15, 18, 21, 24],
            2,
            "The face of a clock is cracked into 4 wedge-shaped pieces meeting at the center. "
            "When ordered from smallest to largest, the sums of the pieces increase by 3 each time (15, 18, 21, and 24). "
            "Which clock face shows how it was cracked?",
            "In clock C, the four wedges are {4, 5, 6} = 15, {12, 1, 2, 3} = 18, {10, 11} = 21, and {7, 8, 9} = 24. "
            "Sorted in order, the sums are 15, 18, 21, and 24.",
        ),
    ]

    for idx, (p_list, cr_list, exp_sums, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_cracked_clock(p_list, exp_sums, ans_idx)
        fig = option_row([fig_cracked_clock(cr) for cr in cr_list], gap=12)
        d.problem(f"Practice {set_num}.{idx}", text, fig, "below")
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set 12: 2002 #12 Kangaroo Zigzag Run
def fig_zigzag_race(names, paths, grid_cols=13, grid_rows=10, s=10.5):
    """Draw the dashed grid and thick orthogonal paths for 3 kangaroos."""
    pad_x = 12
    label_h = 15
    top_ext = 1  # paths stick 1 unit above top dashed line (to y = grid_rows + 1)
    w = grid_cols * s + 2 * pad_x
    h = (grid_rows + top_ext) * s + label_h + 6

    def draw(c, x, y):
        ox = x + pad_x
        oy = y + label_h

        # 1. Dashed grid lines: x in 0..grid_cols, y in 0..grid_rows
        c.setLineWidth(0.6)
        c.setStrokeColor(colors.Color(0.35, 0.35, 0.35))
        c.setDash(1.5, 1.5)
        for gx in range(grid_cols + 1):
            px = ox + gx * s
            c.line(px, oy, px, oy + grid_rows * s)
        for gy in range(grid_rows + 1):
            py = oy + gy * s
            c.line(ox, py, ox + grid_cols * s, py)
        c.setDash([])

        # 2. Thick solid zigzag paths
        c.setStrokeColor(colors.black)
        c.setLineWidth(2.2)
        c.setLineCap(1)
        c.setLineJoin(1)
        for path in paths:
            p = c.beginPath()
            x0, y0 = path[0]
            p.moveTo(ox + x0 * s, oy + y0 * s)
            for px, py in path[1:]:
                p.lineTo(ox + px * s, oy + py * s)
            c.drawPath(p, stroke=1, fill=0)
        c.setLineCap(0)
        c.setLineJoin(0)

        # 3. Runner names centered beneath each starting x-coordinate
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8.5)
        for name, path in zip(names, paths):
            sx = ox + path[0][0] * s
            c.drawCentredString(sx, y + 3, name)

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def path_length_and_cells(path, grid_cols=13, grid_rows=10):
    assert path[0][1] == 0, f"Path must start at y=0, got {path[0]}"
    assert path[-1][1] == grid_rows + 1, f"Path must end at y={grid_rows + 1}, got {path[-1]}"
    total = 0
    used_vertices = {path[0]}
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert 0 <= x1 <= grid_cols and 0 <= x2 <= grid_cols, f"x out of bounds: {(x1, x2)}"
        assert 0 <= y1 <= grid_rows + 1 and 0 <= y2 <= grid_rows + 1, f"y out of bounds: {(y1, y2)}"
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        assert (dx == 0) ^ (dy == 0), f"Non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}"
        step_x = 0 if x2 == x1 else (1 if x2 > x1 else -1)
        step_y = 0 if y2 == y1 else (1 if y2 > y1 else -1)
        steps = dx + dy
        for k in range(1, steps + 1):
            v = (x1 + k * step_x, y1 + k * step_y)
            assert v not in used_vertices, f"Self-intersecting path at {v}"
            used_vertices.add(v)
        total += steps
    return total, used_vertices


def check_zigzag_race(paths, expected_lengths, answer_idx):
    all_vertices = set()
    lengths = []
    for p in paths:
        L, verts = path_length_and_cells(p)
        assert not (all_vertices & verts), f"Paths overlap at {all_vertices & verts}"
        all_vertices |= verts
        lengths.append(L)
    assert lengths == list(expected_lengths), f"Expected path lengths {expected_lengths}, got {lengths}"
    assert 0 <= answer_idx < 5


def q_2002_12(d, key, set_num=3, include_orig=True, num_practice=5):
    d.heading(
        f"Problem {set_num}: 2002 #12 - Kangaroo Zigzag Run",
        "Comparing total grid-segment lengths of zigzag paths",
    )

    # Original 2002 #12: Mary = 21, Norbert = 21, Oscar = 19 -> Answer: E
    if include_orig:
        paths0 = [
            # Mary: 11 vertical + (2+3+1+1+1+2)=10 horizontal = 21
            [(2, 0), (2, 3), (4, 3), (4, 5), (1, 5), (1, 6), (0, 6), (0, 7), (1, 7), (1, 8), (0, 8), (0, 10), (2, 10), (2, 11)],
            # Norbert: 11 vertical + (1+2+1+1+1+2+1+1)=10 horizontal = 21
            [(6, 0), (6, 1), (7, 1), (7, 2), (5, 2), (5, 3), (6, 3), (6, 4), (5, 4), (5, 5), (6, 5), (6, 6), (8, 6), (8, 8), (7, 8), (7, 9), (6, 9), (6, 11)],
            # Oscar: 11 vertical + (1+1+1+1+1+1+1+1)=8 horizontal = 19
            [(11, 0), (11, 1), (12, 1), (12, 2), (13, 2), (13, 3), (12, 3), (12, 4), (11, 4), (11, 5), (10, 5), (10, 6), (9, 6), (9, 7), (10, 7), (10, 8), (11, 8), (11, 11)],
        ]
        check_zigzag_race(paths0, [21, 21, 19], 4)
        opts0 = [
            "Mary and Oscar arrive at the same time",
            "Norbert is first",
            "Oscar is last",
            "They all arrive at the same time",
            "Mary and Norbert arrive at the same time",
        ]
        d.problem(
            "2002 #12",
            "During a zigzag run the kangaroos Mary, Norbert, and Oscar have to jump as drawn in the picture. "
            "Suppose they jump at the same speed. Which statement is true?",
            fig_zigzag_race(["Mary", "Norbert", "Oscar"], paths0),
            "right",
            opts0,
            choice_cols=1,
        )
        key.append((
            "2002 #12",
            "E",
            "All three kangaroos move upward by the exact same vertical distance (11 grid units) without ever going down. "
            "Counting their horizontal side-to-side steps: Mary makes 2 + 3 + 1 + 1 + 1 + 2 = 10 horizontal steps (total 21), "
            "Norbert makes 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 = 10 horizontal steps (total 21), and Oscar makes "
            "1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 = 8 horizontal steps (total 19). Oscar finishes first (19 steps), "
            "while Mary and Norbert arrive at the same time (21 steps each).",
        ))

    practices = [
        # Practice .1: Anna = 19, Ben = 21, Clara = 21 -> Answer: A (Anna is first)
        (
            ["Anna", "Ben", "Clara"],
            [
                # Anna: 11 vertical + (2+2+1+1+1+1)=8 horizontal = 19
                [(2, 0), (2, 2), (0, 2), (0, 5), (2, 5), (2, 7), (3, 7), (3, 8), (2, 8), (2, 9), (1, 9), (1, 10), (2, 10), (2, 11)],
                # Ben: 11 vertical + (2+3+2+1+2)=10 horizontal = 21
                [(6, 0), (6, 2), (8, 2), (8, 4), (5, 4), (5, 6), (7, 6), (7, 8), (8, 8), (8, 10), (6, 10), (6, 11)],
                # Clara: 11 vertical + (2+2+2+1+1+2)=10 horizontal = 21
                [(11, 0), (11, 2), (13, 2), (13, 4), (11, 4), (11, 6), (9, 6), (9, 8), (10, 8), (10, 9), (9, 9), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 21, 21],
            [
                "Anna is first",
                "Ben is first",
                "Clara is first",
                "Anna is last",
                "They all arrive at the same time",
            ],
            0,
            1,
            "During a zigzag run the kangaroos Anna, Ben, and Clara jump along the paths drawn in the picture "
            "at the same speed. Which statement is true?",
            "Each kangaroo travels 11 units upward. Counting horizontal steps: Anna takes 2 + 2 + 1 + 1 + 1 + 1 = 8 "
            "horizontal steps (total 19), Ben takes 2 + 3 + 2 + 1 + 2 = 10 horizontal steps (total 21), and Clara takes "
            "2 + 2 + 2 + 1 + 1 + 2 = 10 horizontal steps (total 21). Since 19 is the shortest path, Anna finishes first.",
        ),
        # Practice .2: Dan = 19, Eva = 23, Finn = 19 -> Answer: B (Dan and Finn arrive at the same time)
        (
            ["Dan", "Eva", "Finn"],
            [
                # Dan: 11 vertical + (2+3+2+1)=8 horizontal = 19
                [(2, 0), (2, 3), (0, 3), (0, 6), (3, 6), (3, 9), (1, 9), (1, 10), (2, 10), (2, 11)],
                # Eva: 11 vertical + (2+3+3+2+2)=12 horizontal = 23
                [(6, 0), (6, 2), (8, 2), (8, 4), (5, 4), (5, 7), (8, 7), (8, 9), (6, 9), (6, 10), (8, 10), (8, 11)],
                # Finn: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(11, 0), (11, 2), (13, 2), (13, 5), (11, 5), (11, 8), (9, 8), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 23, 19],
            [
                "Eva is first",
                "Dan and Finn arrive at the same time",
                "Finn is last",
                "Dan and Eva arrive at the same time",
                "They all arrive at the same time",
            ],
            1,
            1,
            "The kangaroos Dan, Eva, and Finn jump along the zigzag paths shown at the same speed. "
            "Which statement is true?",
            "All three paths go 11 units upward. Counting horizontal steps: Dan takes 2 + 3 + 2 + 1 = 8 horizontal steps "
            "(total 19), Eva takes 2 + 3 + 3 + 2 + 2 = 12 horizontal steps (total 23), and Finn takes 2 + 2 + 2 + 2 = 8 "
            "horizontal steps (total 19). Therefore, Dan and Finn arrive at the same time.",
        ),
        # Practice .3: Leo = 19, Mia = 19, Noah = 19 -> Answer: C (They all arrive at the same time)
        (
            ["Leo", "Mia", "Noah"],
            [
                # Leo: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(2, 0), (2, 2), (0, 2), (0, 5), (2, 5), (2, 7), (0, 7), (0, 9), (2, 9), (2, 11)],
                # Mia: 11 vertical + (1+2+2+2+1)=8 horizontal = 19
                [(6, 0), (6, 2), (5, 2), (5, 4), (7, 4), (7, 6), (5, 6), (5, 9), (7, 9), (7, 10), (6, 10), (6, 11)],
                # Noah: 11 vertical + (2+3+1+2)=8 horizontal = 19
                [(11, 0), (11, 3), (13, 3), (13, 6), (10, 6), (10, 8), (9, 8), (9, 10), (11, 10), (11, 11)],
            ],
            [19, 19, 19],
            [
                "Leo is first",
                "Mia is last",
                "They all arrive at the same time",
                "Only Leo and Mia arrive at the same time",
                "Noah is first",
            ],
            2,
            1,
            "Leo, Mia, and Noah jump from the bottom to the top of the grid along the drawn paths at the same speed. "
            "Which statement is true?",
            "Every kangaroo moves 11 units upward. Counting horizontal steps: Leo takes 2 + 2 + 2 + 2 = 8 horizontal steps "
            "(total 19), Mia takes 1 + 2 + 2 + 2 + 1 = 8 horizontal steps (total 19), and Noah takes 2 + 3 + 1 + 2 = 8 "
            "horizontal steps (total 19). Since all three travel 19 grid segments, they all arrive at the same time.",
        ),
        # Practice .4: Max = 17, Nina = 19, Otto = 21 -> Answer: D (Otto is last)
        (
            ["Max", "Nina", "Otto"],
            [
                # Max: 11 vertical + (2+2+1+1)=6 horizontal = 17
                [(2, 0), (2, 3), (0, 3), (0, 6), (2, 6), (2, 8), (1, 8), (1, 10), (2, 10), (2, 11)],
                # Nina: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(6, 0), (6, 2), (8, 2), (8, 5), (6, 5), (6, 7), (4, 7), (4, 9), (6, 9), (6, 11)],
                # Otto: 11 vertical + (2+3+3+2)=10 horizontal = 21
                [(11, 0), (11, 2), (13, 2), (13, 5), (10, 5), (10, 8), (13, 8), (13, 10), (11, 10), (11, 11)],
            ],
            [17, 19, 21],
            [
                "Max is last",
                "Nina is first",
                "Max and Nina arrive at the same time",
                "Otto is last",
                "Otto is first",
            ],
            3,
            1,
            "Max, Nina, and Otto jump along the paths drawn in the picture at the same speed. "
            "Which statement is true?",
            "All three paths have 11 vertical steps upward. Counting horizontal steps: Max takes 2 + 2 + 1 + 1 = 6 "
            "horizontal steps (total 17), Nina takes 2 + 2 + 2 + 2 = 8 horizontal steps (total 19), and Otto takes "
            "2 + 3 + 3 + 2 = 10 horizontal steps (total 21). Otto has the longest path (21 steps), so Otto is last.",
        ),
        # Practice .5: Ruby = 21, Sam = 17, Toby = 19 -> Shortest path length = 17 m (Answer: C)
        (
            ["Ruby", "Sam", "Toby"],
            [
                # Ruby: 11 vertical + (2+3+3+2)=10 horizontal = 21
                [(2, 0), (2, 2), (0, 2), (0, 5), (3, 5), (3, 8), (0, 8), (0, 10), (2, 10), (2, 11)],
                # Sam: 11 vertical + (1+2+2+1)=6 horizontal = 17
                [(6, 0), (6, 3), (7, 3), (7, 6), (5, 6), (5, 9), (7, 9), (7, 10), (6, 10), (6, 11)],
                # Toby: 11 vertical + (2+2+2+2)=8 horizontal = 19
                [(11, 0), (11, 2), (13, 2), (13, 5), (11, 5), (11, 7), (9, 7), (9, 9), (11, 9), (11, 11)],
            ],
            [21, 17, 19],
            ["15 m", "16 m", "17 m", "19 m", "21 m"],
            2,
            5,
            "Three kangaroos — Ruby, Sam, and Toby — jump from the bottom to the top along the paths shown on the grid, "
            "where each small grid square has a side of 1 m. What is the total length of the <b>shortest</b> path?",
            "Every kangaroo travels 11 m upward. Counting horizontal steps: Ruby travels 2 + 3 + 3 + 2 = 10 m horizontally "
            "(total 11 + 10 = 21 m), Sam travels 1 + 2 + 2 + 1 = 6 m horizontally (total 11 + 6 = 17 m), and Toby travels "
            "2 + 2 + 2 + 2 = 8 m horizontally (total 11 + 8 = 19 m). The shortest path is Sam's path at 17 m.",
        ),
    ]

    for idx, (names, paths, exp_lens, opts, ans_idx, cols, text, expl) in enumerate(practices[:num_practice], start=1):
        check_zigzag_race(paths, exp_lens, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_zigzag_race(names, paths),
            "right",
            opts,
            choice_cols=cols,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2002 #15 Flag Silhouette in the Wind
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


# ------------------------------------------------- Set: 2002 #18 Pet Logic Deduction
def check_logic_matching(people, items, valid_fn, choices_check_fn, expected_idx):
    valid_assignments = []
    for perm in itertools.permutations(items):
        assign = dict(zip(people, perm))
        if valid_fn(assign):
            valid_assignments.append(assign)
    assert len(valid_assignments) == 1, f"Expected unique valid assignment, got {len(valid_assignments)}: {valid_assignments}"
    sol = valid_assignments[0]
    matches = [i for i, fn in enumerate(choices_check_fn) if fn(sol)]
    assert matches == [expected_idx], f"Expected choice {expected_idx}, got {matches} for sol={sol}"


def q_2002_18(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Logic Deduction: Matching Pets & Items", "Based on 2002, Problem 18")

    # Original 2002 #18
    people0 = ["Julien", "Manon", "Nicolas", "Fabienne"]
    pets0 = ["cat", "dog", "parrot", "goldfish"]
    furry0 = {"cat", "dog"}
    four_legs0 = {"cat", "dog"}
    bird0 = {"parrot"}
    check_logic_matching(
        people0,
        pets0,
        lambda a: (a["Manon"] in furry0 and a["Fabienne"] in four_legs0 and a["Nicolas"] in bird0 and a["Manon"] != "cat"),
        [
            lambda a: a["Fabienne"] != "dog",      # A: "Fabienne has a dog" is NOT true
            lambda a: a["Nicolas"] != "parrot",    # B: "Nicolas has a parrot" is NOT true
            lambda a: a["Julien"] != "goldfish",   # C: "Julien has a goldfish" is NOT true
            lambda a: a["Fabienne"] != "cat",      # D: "Fabienne has a cat" is NOT true
            lambda a: a["Manon"] != "dog",         # E: "Manon has a dog" is NOT true
        ],
        0,
    )
    if include_orig:
        d.problem(
            "Original 2002 #18.",
            "Julien, Manon, Nicolas and Fabienne each have a different pet: a cat, a dog, a parrot and a goldfish. "
            "Manon has a furry animal, Fabienne owns a four-legged creature, Nicolas has a bird and Manon doesn't like cats. "
            "Which statement is <b>not</b> true?",
            choices=[
                "Fabienne has a dog",
                "Nicolas has a parrot",
                "Julien has a goldfish",
                "Fabienne has a cat",
                "Manon has a dog",
            ],
            choice_cols=3,
        )
        key.append((
            "2002 #18",
            "A",
            "Nicolas has the bird, so Nicolas has the parrot. Manon has a furry animal (cat or dog) and doesn't like cats, "
            "so Manon has the dog. Fabienne has a four-legged creature (cat or dog), which must be the cat. "
            "That leaves the goldfish for Julien. Therefore, 'Fabienne has a dog' (A) is NOT true.",
        ))

    practices = [
        # Practice .1: 4 kids (Anna, Ben, Clara, David), pets (rabbit, hamster, turtle, canary). Answer: C
        (
            ["Anna", "Ben", "Clara", "David"],
            ["rabbit", "hamster", "turtle", "canary"],
            lambda a: (
                a["Ben"] in {"rabbit", "hamster"}
                and a["Clara"] in {"rabbit", "hamster"}
                and a["David"] == "canary"
                and a["Ben"] != "hamster"
            ),
            [
                lambda a: a["Ben"] != "rabbit",
                lambda a: a["David"] != "canary",
                lambda a: a["Clara"] != "rabbit",  # False statement: "Clara has a rabbit"
                lambda a: a["Anna"] != "turtle",
                lambda a: a["Clara"] != "hamster",
            ],
            [
                "Ben has a rabbit",
                "David has a canary",
                "Clara has a rabbit",
                "Anna has a turtle",
                "Clara has a hamster",
            ],
            2,
            "Anna, Ben, Clara, and David each own a different pet: a rabbit, a hamster, a turtle, and a canary. "
            "Ben and Clara both own furry pets, David owns a bird, and Ben does not have the hamster. "
            "Which statement is <b>not</b> true?",
            "David has the bird (canary). The two furry pets are the rabbit and the hamster, belonging to Ben and Clara. "
            "Since Ben does not have the hamster, Ben has the rabbit and Clara has the hamster. "
            "That leaves the turtle for Anna. Thus, 'Clara has a rabbit' (C) is not true.",
        ),
        # Practice .2: 4 friends (Eva, Finn, Grace, Henry), instruments (violin, guitar, flute, drums). Answer: D
        (
            ["Eva", "Finn", "Grace", "Henry"],
            ["violin", "guitar", "flute", "drums"],
            lambda a: (
                a["Eva"] in {"violin", "guitar"}
                and a["Grace"] in {"violin", "guitar"}
                and a["Finn"] == "drums"
                and a["Eva"] != "violin"
            ),
            [
                lambda a: a["Eva"] != "guitar",
                lambda a: a["Finn"] != "drums",
                lambda a: a["Grace"] != "violin",
                lambda a: a["Henry"] != "guitar",  # False statement: "Henry plays the guitar"
                lambda a: a["Henry"] != "flute",
            ],
            [
                "Eva plays the guitar",
                "Finn plays the drums",
                "Grace plays the violin",
                "Henry plays the guitar",
                "Henry plays the flute",
            ],
            3,
            "Eva, Finn, Grace, and Henry each play a different instrument: a violin, a guitar, a flute, and drums. "
            "Eva and Grace play stringed instruments, Finn plays percussion (drums), and Eva does not play the violin. "
            "Which statement is <b>not</b> true?",
            "The stringed instruments are the violin and the guitar. Since Eva does not play the violin, Eva plays the guitar "
            "and Grace plays the violin. Finn plays the drums, leaving the flute for Henry. "
            "Therefore, 'Henry plays the guitar' (D) is not true.",
        ),
        # Practice .3: 4 kids (Leo, Mia, Noah, Olivia), snacks (apple, banana, cookie, pretzel). Ask what Olivia has -> E
        (
            ["Leo", "Mia", "Noah", "Olivia"],
            ["apple", "banana", "cookie", "pretzel"],
            lambda a: (
                a["Leo"] in {"apple", "banana"}
                and a["Mia"] in {"apple", "banana"}
                and a["Noah"] == "cookie"
                and a["Leo"] != "apple"
            ),
            [
                lambda a: a["Olivia"] == "apple",
                lambda a: a["Olivia"] == "banana",
                lambda a: a["Olivia"] == "cookie",
                lambda a: a["Leo"] == "apple",
                lambda a: a["Olivia"] == "pretzel",
            ],
            [
                "Olivia has the apple",
                "Olivia has the banana",
                "Olivia has the cookie",
                "Leo has the apple",
                "Olivia has the pretzel",
            ],
            4,
            "Leo, Mia, Noah, and Olivia each brought a different snack: an apple, a banana, a cookie, and a pretzel. "
            "Leo and Mia brought fruits, Noah brought the cookie, and Leo does not like apples. "
            "Which statement is <b>true</b>?",
            "Leo and Mia have the two fruits (apple and banana). Since Leo does not like apples, Leo has the banana and "
            "Mia has the apple. Noah has the cookie, which leaves the pretzel for Olivia. So statement E is true.",
        ),
        # Practice .4: 4 athletes (Sam, Tara, Uma, Vic), sports (soccer, tennis, swimming, cycling). Answer: B
        (
            ["Sam", "Tara", "Uma", "Vic"],
            ["soccer", "tennis", "swimming", "cycling"],
            lambda a: (
                a["Sam"] in {"soccer", "tennis"}
                and a["Uma"] in {"soccer", "tennis"}
                and a["Tara"] == "swimming"
                and a["Sam"] != "soccer"
            ),
            [
                lambda a: a["Sam"] != "tennis",
                lambda a: a["Uma"] != "tennis",  # False statement: "Uma plays tennis"
                lambda a: a["Tara"] != "swimming",
                lambda a: a["Vic"] != "cycling",
                lambda a: a["Uma"] != "soccer",
            ],
            [
                "Sam plays tennis",
                "Uma plays tennis",
                "Tara does swimming",
                "Vic does cycling",
                "Uma plays soccer",
            ],
            1,
            "Sam, Tara, Uma, and Vic each do a different sport: soccer, tennis, swimming, and cycling. "
            "Sam and Uma play sports with a ball, Tara is in the pool, and Sam does not play soccer. "
            "Which statement is <b>not</b> true?",
            "The two ball sports are soccer and tennis. Since Sam does not play soccer, Sam plays tennis and Uma plays soccer. "
            "Tara does swimming, leaving cycling for Vic. Thus, 'Uma plays tennis' (B) is not true.",
        ),
    ]

    for idx, (p_list, it_list, v_fn, c_fns, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_logic_matching(p_list, it_list, v_fn, c_fns, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2002 #20 Cube Tunnel to Pyramid
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


# ------------------------------------------------- Set: 2002 #21 Three Digit Cards & Four Operations
def can_reach_target_3cards(cards, target):
    """Return a string formula if the 3 cards can make `target` using +, -, *, / (exact division) and parentheses, else None."""
    ops = [
        ("+", lambda a, b: a + b),
        ("-", lambda a, b: a - b),
        ("×", lambda a, b: a * b),
        ("÷", lambda a, b: a // b if b != 0 and a % b == 0 else None),
    ]
    for x, y, z in itertools.permutations(cards):
        for s1, f1 in ops:
            for s2, f2 in ops:
                r1 = f1(x, y)
                if r1 is not None:
                    r2 = f2(r1, z)
                    if r2 == target:
                        return f"({x} {s1} {y}) {s2} {z} = {target}"
                r3 = f2(y, z)
                if r3 is not None:
                    r4 = f1(x, r3)
                    if r4 == target:
                        return f"{x} {s1} ({y} {s2} {z}) = {target}"
    return None


def check_cards_target(players_cards, target, expected_unsolvable_names):
    unsolvable = [name for name, cards in players_cards if can_reach_target_3cards(cards, target) is None]
    assert unsolvable == expected_unsolvable_names, (
        f"For target={target}, expected unsolvable={expected_unsolvable_names}, got {unsolvable}"
    )


def q_2002_21(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Making a Target Number with Three Digit Cards", "Based on 2002, Problem 21")

    # Original 2002 #21: Alex (7,2,4), Martha (6,5,1), Fred (8,3,9), target = 20 -> Martha cannot get 20 (B)
    p0 = [("Alex", (7, 2, 4)), ("Martha", (6, 5, 1)), ("Fred", (8, 3, 9))]
    check_cards_target(p0, 20, ["Martha"])
    if include_orig:
        d.problem(
            "Original 2002 #21.",
            "The digits from 1 to 9 are written on 9 cards. Alex has the digits 7, 2 and 4; Martha has the digits "
            "6, 5 and 1; and Fred has 8, 3 and 9. Each of them uses some of the four basic operations + (addition), "
            "- (subtraction), × (multiplication), ÷ (division), and each of his own cards exactly once. "
            "Who cannot obtain 20 as a result?",
            choices=["Alex", "Martha", "Fred", "All can get 20", "Alex and Martha"],
            choice_cols=3,
        )
        key.append((
            "2002 #21",
            "B",
            "Alex can make 20 with (7 - 2) × 4 = 20. Fred can make 20 with 8 + 3 + 9 = 20. "
            "With Martha's cards (6, 5, 1), no combination of +, -, ×, ÷ gives 20 (the closest results are "
            "6 × (5 - 1) = 24 and 5 × (6 - 1) = 25). So Martha cannot obtain 20.",
        ))

    practices = [
        # Practice .1: Target 18. Leo (9, 4, 2) -> (9-2)*? No, 9*4/2 = 18! Mia (7, 5, 1) -> cannot get 18! Noah (6, 8, 4) -> 6+8+4=18. Answer: B (Mia)
        (
            [("Leo", (9, 4, 2)), ("Mia", (7, 5, 1)), ("Noah", (6, 8, 4))],
            18,
            ["Mia"],
            ["Leo", "Mia", "Noah", "All can get 18", "Leo and Noah"],
            1,
            "Three friends each have 3 digit cards: Leo has 9, 4, and 2; Mia has 7, 5, and 1; and Noah has 6, 8, and 4. "
            "Using the operations +, -, ×, ÷ and each of their own three cards once, who <b>cannot</b> obtain <b>18</b> as a result?",
            "Leo can make 18 as (9 × 4) ÷ 2 = 18. Noah can make 18 as 6 + 8 + 4 = 18. "
            "Mia's cards (7, 5, 1) can make 13, 21, 28, 34, 35, 36, or 42, but never 18. So Mia cannot obtain 18.",
        ),
        # Practice .2: Target 15. Anna (8, 4, 1) -> cannot get 15! Ben (6, 3, 2) -> 6*3-? No: (6+2)*? Wait: 6*2+3 = 15! Clara (9, 5, 1) -> 9+5+1 = 15! Answer: A (Anna)
        (
            [("Anna", (8, 4, 1)), ("Ben", (6, 3, 2)), ("Clara", (9, 5, 1))],
            15,
            ["Anna"],
            ["Anna", "Ben", "Clara", "All can get 15", "Ben and Clara"],
            0,
            "Anna has cards 8, 4, and 1; Ben has cards 6, 3, and 2; and Clara has cards 9, 5, and 1. "
            "Each person uses +, -, ×, ÷ and all three of their own cards exactly once. Who <b>cannot</b> obtain <b>15</b>?",
            "Ben can get 15 with 6 × 2 + 3 = 15, and Clara can get 15 with 9 + 5 + 1 = 15. "
            "With Anna's cards (8, 4, 1), no combination of operations produces 15. So the answer is Anna.",
        ),
        # Practice .3: Target 24. Dan (8, 2, 1) -> 8*(2+1)=24. Eva (9, 7, 8) -> 9+7+8=24. Finn (5, 4, 2) -> cannot get 24! Answer: C (Finn)
        (
            [("Dan", (8, 2, 1)), ("Eva", (9, 7, 8)), ("Finn", (5, 4, 2))],
            24,
            ["Finn"],
            ["Dan", "Eva", "Finn", "All can get 24", "Dan and Eva"],
            2,
            "Dan has cards 8, 2, and 1; Eva has cards 9, 7, and 8; and Finn has cards 5, 4, and 2. "
            "Using +, -, ×, ÷ and each of their own three cards once, who <b>cannot</b> obtain <b>24</b>?",
            "Dan can get 24 with 8 × (2 + 1) = 24. Eva can get 24 with 9 + 7 + 8 = 24. "
            "Finn's cards (5, 4, 2) can make 5 × 4 + 2 = 22 or (5 + 2) × 4 = 28, but never 24. So Finn cannot obtain 24.",
        ),
        # Practice .4: Target 16. Ruby (8, 6, 4) -> 8*6/4 = 12, 8+6+4=18, (8-4)*6=24, (6-4)*8=16!
        # Sam (5, 3, 2) -> (5+3)*2 = 16! Toby (9, 4, 3) -> 9+4+3 = 16! All can get 16 -> Answer: D
        (
            [("Ruby", (8, 6, 4)), ("Sam", (5, 3, 2)), ("Toby", (9, 4, 3))],
            16,
            [],
            ["Ruby", "Sam", "Toby", "All can get 16", "Ruby and Sam"],
            3,
            "Ruby has cards 8, 6, and 4; Sam has cards 5, 3, and 2; and Toby has cards 9, 4, and 3. "
            "Using +, -, ×, ÷ and each of their three cards once, who <b>cannot</b> obtain <b>16</b>?",
            "Ruby can make 16 with 8 × (6 - 4) = 16. Sam can make 16 with (5 + 3) × 2 = 16. "
            "Toby can make 16 with 9 + 4 + 3 = 16. Therefore, all three of them can obtain 16!",
        ),
    ]

    for idx, (p_cards, target, exp_unsolv, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_cards_target(p_cards, target, exp_unsolv)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2002 #22 Seating Permutations with Fixed Spots
def check_seating_ways(n_total, n_fixed, choices, ans_idx):
    free = n_total - n_fixed
    ways = math.factorial(free)
    matches = [i for i, ch in enumerate(choices) if int(ch) == ways]
    assert matches == [ans_idx], f"Seating ways={ways}, choices={choices}, ans_idx={ans_idx}"


def q_2002_22(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Seating Arrangements with Fixed Seats", "Based on 2002, Problem 22")

    opts0 = ["3", "4", "6", "24", "25"]
    check_seating_ways(4, 1, opts0, 2)
    if include_orig:
        d.problem(
            "Original 2002 #22.",
            "Four friends go to a restaurant and sit down at a table. John always sits at the same spot on the table. "
            "In how many ways can the friends sit around the table?",
            choices=opts0,
        )
        key.append((
            "2002 #22",
            "C",
            "Since John always takes his fixed seat, only the other 3 friends change places among the remaining 3 seats. "
            "The first friend has 3 choices, the second has 2 choices, and the third has 1 choice, giving 3 × 2 × 1 = 6 ways.",
        ))

    practices = [
        # Practice .1: 5 friends, 2 always sit in their favorite chairs -> 3! = 6 ways (Answer: B)
        (
            5,
            2,
            ["3", "6", "12", "24", "120"],
            1,
            "Five friends sit on a bench with 5 seats at the park. Emma always sits on the far left seat, and Lucas "
            "always sits on the far right seat. In how many different ways can the 5 friends sit on the bench?",
            "Emma's and Lucas's seats are fixed, leaving 3 middle seats for the other 3 friends. "
            "Those 3 friends can be arranged in 3 × 2 × 1 = 6 different ways.",
        ),
        # Practice .2: 5 family members at a dinner table, Grandma always sits at the head -> 4! = 24 ways (Answer: D)
        (
            5,
            1,
            ["4", "12", "16", "24", "120"],
            3,
            "Five family members sit around a dinner table with 5 chairs. Grandma always sits in the armchair at the "
            "head of the table. In how many different ways can the family sit around the table?",
            "With Grandma's seat fixed, the remaining 4 family members can sit in the other 4 chairs in "
            "4 × 3 × 2 × 1 = 24 different ways.",
        ),
        # Practice .3: 4 astronauts in a 4-seat spacecraft, Commander and Pilot have fixed seats -> 2! = 2 ways (Answer: A)
        (
            4,
            2,
            ["2", "4", "6", "12", "24"],
            0,
            "Four astronauts board a spacecraft with 4 seats. The Commander must sit in Seat 1 and the Pilot must sit "
            "in Seat 2. In how many different ways can the 4 astronauts be seated?",
            "Seat 1 and Seat 2 are already fixed for the Commander and Pilot. The remaining 2 astronauts can sit in "
            "Seats 3 and 4 in 2 × 1 = 2 ways.",
        ),
        # Practice .4: 4 runners posing for a photo, nobody has a fixed spot -> 4! = 24 ways (Answer: E)
        (
            4,
            0,
            ["4", "8", "12", "16", "24"],
            4,
            "Four friends stand in a line of 4 spots to take a team photo, and anyone can stand in any spot. "
            "In how many different orders can the 4 friends stand in line?",
            "There are 4 choices for the first spot, 3 for the second, 2 for the third, and 1 for the fourth, "
            "giving 4 × 3 × 2 × 1 = 24 different orders.",
        ),
    ]

    for idx, (ntot, nfix, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_seating_ways(ntot, nfix, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2002 #24 Odometer with Distinct Digits
def next_distinct_digits_distance(start_num):
    n = start_num + 1
    while len(set(str(n))) != len(str(n)):
        n += 1
    return n - start_num, n


def check_odometer_distinct(start_num, choices, ans_idx):
    dist, _ = next_distinct_digits_distance(start_num)
    matches = [i for i, ch in enumerate(choices) if int(ch) == dist]
    assert matches == [ans_idx], f"Odometer start={start_num}, dist={dist}, choices={choices}, ans_idx={ans_idx}"


def q_2002_24(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Odometer with All Different Digits", "Based on 2002, Problem 24")

    opts0 = ["1", "21", "431", "12431", "13776"]
    check_odometer_distinct(187569, opts0, 1)
    if include_orig:
        d.problem(
            "Original 2002 #24.",
            "The odometer of my car indicates 187569. All the digits of this number are different. "
            "After how many more kilometres will this happen again?",
            choices=opts0,
        )
        key.append((
            "2002 #24",
            "B",
            "Starting from 187569, numbers 187570–187579 repeat the digit 7, and 187580–187589 repeat the digit 8. "
            "The very next number is 187590, whose digits (1, 8, 7, 5, 9, 0) are all different! "
            "That takes 187590 - 187569 = 21 km.",
        ))

    practices = [
        # Practice .1: Start = 264359. Next is 264370 (digits 2,6,4,3,7,0 all distinct!). Distance = 11 km (Answer: A)
        (
            264359,
            ["11", "21", "31", "41", "141"],
            0,
            "A car's odometer shows <b>264359</b>, where all six digits are different. "
            "After how many more kilometres will all six digits on the odometer be different again?",
            "From 264359, the numbers 264360 through 264369 all repeat the digit 6. "
            "The next number is 264370, which has digits 2, 6, 4, 3, 7, 0 — all different! "
            "That is 264370 - 264359 = 11 km later.",
        ),
        # Practice .2: Start = 398675.
        # 398676..398679: 398676(6), 398677(7), 398678(8), 398679(9)
        # 39868x(8), 39869x(9), 39870x: 398701 has digits 3,9,8,7,0,1!
        # Distance = 398701 - 398675 = 26 km (Answer: C)
        (
            398675,
            ["5", "15", "26", "35", "126"],
            2,
            "An odometer reads <b>398675</b>, and all of its digits are different. "
            "What is the smallest number of kilometres the car must travel until all six digits are different again?",
            "Checking numbers after 398675: 398676–398679 repeat 6, 7, 8, or 9; 398680–398689 repeat 8; "
            "and 398690–398699 repeat 9. At 398700 the 0 repeats, and then 398701 has all distinct digits (3, 9, 8, 7, 0, 1). "
            "The distance is 398701 - 398675 = 26 km.",
        ),
        # Practice .3: 4-digit bike counter reads 1987.
        # 1988..1989 (repeat 8,9), 1990..1999 (repeat 9), 2000..2011 (repeat 0 or 1), 2012 (repeat 2), 2013!
        # Distance = 2013 - 1987 = 26 km (Answer: D)
        (
            1987,
            ["3", "13", "16", "26", "36"],
            3,
            "A bicycle trip counter shows the 4-digit number <b>1987</b>, whose digits are all different. "
            "After how many more kilometres will the counter next show a number with all four digits different?",
            "Numbers 1988–1999 all repeat 8 or 9, and numbers 2000–2012 repeat 0, 1, or 2. "
            "The first number after 1987 with four different digits is 2013 (digits 2, 0, 1, 3). "
            "That happens after 2013 - 1987 = 26 km.",
        ),
        # Practice .4: Start = 476358. Next: 476359 (digits 4,7,6,3,5,9 all distinct!). Distance = 1 km (Answer: E)
        (
            476358,
            ["12", "11", "9", "2", "1"],
            4,
            "The odometer of a bus shows <b>476358</b>, where every digit is different. "
            "After how many more kilometres will all six digits be different again?",
            "Adding just 1 km gives 476359, whose digits (4, 7, 6, 3, 5, 9) are already all different! "
            "So it happens after just 1 km.",
        ),
    ]

    for idx, (s_num, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_odometer_distinct(s_num, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2003 #10 Metric Length Conversion (dm, cm, mm)
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


# ------------------------------------------------- Set: 2003 #16 Book Page Number Digits
def total_digits_for_pages(n_pages):
    return sum(len(str(p)) for p in range(1, n_pages + 1))


def check_pages_from_digits(total_digits, choices, ans_idx):
    matching_pages = [p for p in range(1, 500) if total_digits_for_pages(p) == total_digits]
    assert len(matching_pages) == 1, f"Invalid total_digits={total_digits}: matching_pages={matching_pages}"
    ans_pages = matching_pages[0]
    matches = [i for i, ch in enumerate(choices) if int(ch) == ans_pages]
    assert matches == [ans_idx], f"Book pages={ans_pages}, choices={choices}, ans_idx={ans_idx}"


def q_2003_16(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Counting Digits in Book Page Numbers", "Based on 2003, Problem 16")

    opts0 = ["12", "15", "22", "28", "35"]
    check_pages_from_digits(35, opts0, 2)
    if include_orig:
        d.problem(
            "Original 2003 #16.",
            "The number of digits used to write all the page numbers in a book is 35. "
            "How many pages is the book in total?",
            choices=opts0,
        )
        key.append((
            "2003 #16",
            "C",
            "Pages 1 through 9 use 9 single digits, leaving 35 - 9 = 26 digits for the two-digit pages. "
            "Since each two-digit page uses 2 digits, there are 26 ÷ 2 = 13 two-digit pages. "
            "In total, the book has 9 + 13 = 22 pages.",
        ))

    practices = [
        # Practice .1: 49 digits -> 9 + 2*(N-9) = 49 -> 2*(N-9)=40 -> N-9=20 -> N = 29 pages (Answer: D)
        (
            49,
            ["20", "24", "25", "29", "40"],
            3,
            "It takes exactly <b>49 digits</b> to print all the page numbers of a storybook (starting from page 1). "
            "How many pages are in the storybook?",
            "Pages 1 to 9 take 9 digits, leaving 49 - 9 = 40 digits. Each two-digit page takes 2 digits, "
            "which gives 40 ÷ 2 = 20 two-digit pages. Adding the 9 single-digit pages gives 9 + 20 = 29 pages.",
        ),
        # Practice .2: 63 digits -> 9 + 2*(N-9) = 63 -> 2*(N-9)=54 -> N-9=27 -> N = 36 pages (Answer: B)
        (
            63,
            ["31", "36", "38", "42", "54"],
            1,
            "All the pages of a puzzle booklet are numbered starting from 1. A total of <b>63 digits</b> are used "
            "for the page numbers. How many pages does the booklet have?",
            "Subtracting the 9 digits used for pages 1–9 leaves 63 - 9 = 54 digits. "
            "Those 54 digits form 54 ÷ 2 = 27 two-digit page numbers (pages 10 to 36). "
            "So the booklet has 9 + 27 = 36 pages.",
        ),
        # Practice .3: 27 digits -> 9 + 2*(N-9) = 27 -> 2*(N-9)=18 -> N-9=9 -> N = 18 pages (Answer: A)
        (
            27,
            ["18", "19", "21", "23", "27"],
            0,
            "Leo numbered all the pages of his comic notebook starting from page 1 and wrote <b>27 digits</b> in total. "
            "How many pages did he number?",
            "Pages 1 to 9 use 9 digits, leaving 27 - 9 = 18 digits for two-digit pages. "
            "That gives 18 ÷ 2 = 9 two-digit pages, so there are 9 + 9 = 18 pages in total.",
        ),
        # Practice .4: 85 digits -> 9 + 2*(N-9) = 85 -> 2*(N-9)=76 -> N-9=38 -> N = 47 pages (Answer: E)
        (
            85,
            ["38", "42", "44", "45", "47"],
            4,
            "A magazine uses <b>85 digits</b> to number all of its pages from page 1 to the last page. "
            "How many pages are in the magazine?",
            "Pages 1 to 9 use 9 digits, leaving 85 - 9 = 76 digits. Dividing by 2 digits per page gives "
            "76 ÷ 2 = 38 two-digit pages. In total, there are 9 + 38 = 47 pages.",
        ),
    ]

    for idx, (tot_d, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_pages_from_digits(tot_d, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2003 #17 Barcode of Wide & Narrow Black and White Bars
def fig_barcode():
    w, h = 88, 36

    def draw(c, x, y):
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        # Left group: wide, narrow, wide
        c.rect(x + 4, y + 4, 6, 28, stroke=0, fill=1)
        c.rect(x + 15, y + 4, 2.2, 28, stroke=0, fill=1)
        c.rect(x + 22, y + 4, 6, 28, stroke=0, fill=1)
        # Dots in middle
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 41, y + 16, ". . . . .")
        # Right group: narrow, wide, wide
        c.rect(x + 56, y + 4, 2.2, 28, stroke=0, fill=1)
        c.rect(x + 63, y + 4, 6, 28, stroke=0, fill=1)
        c.rect(x + 74, y + 4, 6, 28, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_barcode(total_bars, white_minus_wide, choices, ans_idx):
    assert total_bars % 2 == 1, "Total bars must be odd when starting and ending with black"
    n_black = (total_bars + 1) // 2
    n_white = (total_bars - 1) // 2
    n_wide = n_white - white_minus_wide
    n_narrow = n_black - n_wide
    assert n_wide > 0 and n_narrow > 0
    matches = [i for i, ch in enumerate(choices) if int(ch) == n_narrow]
    assert matches == [ans_idx], f"Barcode narrow={n_narrow}, choices={choices}, ans_idx={ans_idx}"


def q_2003_17(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Alternating Black & White Barcode", "Based on 2003, Problem 17")

    opts0 = ["1", "2", "3", "4", "5"]
    check_barcode(17, 3, opts0, 3)
    if include_orig:
        d.problem(
            "Original 2003 #17.",
            "A bar code is formed using 17 black and white bars (the first and last bars are black). "
            "The black bars are two types: wide and narrow. The number of white bars is 3 more than the number "
            "of wide black bars. The number of narrow black bars is:",
            fig_barcode(),
            "right",
            opts0,
        )
        key.append((
            "2003 #17",
            "D",
            "Since the 17 bars alternate black and white and both the first and last bars are black, there are "
            "9 black bars and 8 white bars. The number of white bars (8) is 3 more than the wide black bars, "
            "so there are 8 - 3 = 5 wide black bars. That leaves 9 - 5 = 4 narrow black bars.",
        ))

    practices = [
        # Practice .1: 21 total bars -> 11 black, 10 white. White is 4 more than wide black -> wide = 6, narrow = 11 - 6 = 5 (Answer: E)
        (
            21, 4,
            ["1", "2", "3", "4", "5"],
            4,
            "A bar code is made of 21 alternating black and white bars, starting and ending with a black bar. "
            "Each black bar is either wide or narrow. The number of white bars is 4 more than the number of wide "
            "black bars. How many narrow black bars are there?",
            "Out of 21 alternating bars starting and ending with black, there are 11 black bars and 10 white bars. "
            "Since 10 white bars is 4 more than the wide black bars, there are 10 - 4 = 6 wide black bars, "
            "leaving 11 - 6 = 5 narrow black bars.",
        ),
        # Practice .2: 19 total bars -> 10 black, 9 white. White is 2 more than wide black -> wide = 7, narrow = 10 - 7 = 3 (Answer: C)
        (
            19, 2,
            ["1", "2", "3", "4", "5"],
            2,
            "A label has a bar code of 19 alternating black and white bars (both the first and last bars are black). "
            "The number of white bars is 2 more than the number of wide black bars. "
            "How many narrow black bars are in the bar code?",
            "With 19 alternating bars beginning and ending with black, there are 10 black bars and 9 white bars. "
            "There are 9 - 2 = 7 wide black bars, so there are 10 - 7 = 3 narrow black bars.",
        ),
        # Practice .3: 15 total bars -> 8 black, 7 white. White is 1 more than wide black -> wide = 6, narrow = 8 - 6 = 2 (Answer: B)
        (
            15, 1,
            ["1", "2", "3", "4", "5"],
            1,
            "A ticket bar code has 15 alternating black and white bars, where the first and last bars are black. "
            "The number of white bars is 1 more than the number of wide black bars. "
            "How many narrow black bars are there?",
            "Among 15 alternating bars starting and ending with black, 8 are black and 7 are white. "
            "The number of wide black bars is 7 - 1 = 6, leaving 8 - 6 = 2 narrow black bars.",
        ),
        # Practice .4: 25 total bars -> 13 black, 12 white. White is 5 more than wide black -> wide = 7, narrow = 13 - 7 = 6 (Answer: D)
        (
            25, 5,
            ["3", "4", "5", "6", "7"],
            3,
            "A package bar code uses 25 alternating black and white bars (the first and last bars are black). "
            "The number of white bars is 5 more than the number of wide black bars. "
            "How many narrow black bars does the bar code have?",
            "Out of 25 alternating bars starting and ending with black, there are 13 black bars and 12 white bars. "
            "There are 12 - 5 = 7 wide black bars, which leaves 13 - 7 = 6 narrow black bars.",
        ),
    ]

    for idx, (t_bars, diff_w, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_barcode(t_bars, diff_w, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_barcode(),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #3 Common Letters in Words
def check_common_letters(w1, w2, choices, ans_idx):
    common = set(w1.upper()) & set(w2.upper())
    cnt = len(common)
    matches = [i for i, ch in enumerate(choices) if int(ch) == cnt]
    assert matches == [ans_idx], f"Common letters between {w1} and {w2}: {common} ({cnt}), choices={choices}, ans_idx={ans_idx}"


def q_2007_3(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Common Letters in Two Words", "Based on 2007, Problem 3")

    opts0 = ["1", "2", "3", "4", "5"]
    check_common_letters("KANGAROO", "PROBLEM", opts0, 1)
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

    practices = [
        # Practice .1: TRIANGLE and RECTANGLE -> {T, R, I, A, N, G, L, E} & {R, E, C, T, A, N, G, L} = {T, R, A, N, G, L, E} = 7 (Answer: D)
        (
            "TRIANGLE", "RECTANGLE",
            ["4", "5", "6", "7", "8"],
            3,
            "How many different letters do the words <b>TRIANGLE</b> and <b>RECTANGLE</b> have in common?",
            "The distinct letters of TRIANGLE are {T, R, I, A, N, G, L, E} and of RECTANGLE are {R, E, C, T, A, N, G, L}. "
            "They share the 7 letters T, R, A, N, G, L, and E.",
        ),
        # Practice .2: DOLPHIN and PENGUIN -> {D, O, L, P, H, I, N} & {P, E, N, G, U, I} = {P, I, N} = 3 (Answer: C)
        (
            "DOLPHIN", "PENGUIN",
            ["1", "2", "3", "4", "5"],
            2,
            "How many common letters do the words <b>DOLPHIN</b> and <b>PENGUIN</b> have?",
            "Checking each letter of DOLPHIN against PENGUIN: P, I, and N appear in both words. "
            "So they have 3 common letters.",
        ),
        # Practice .3: BALLOON and BANANA -> {B, A, L, O, N} & {B, A, N} = {B, A, N} = 3 (Answer: B)
        (
            "BALLOON", "BANANA",
            ["2", "3", "4", "5", "6"],
            1,
            "How many different letters appear in <b>both</b> the word <b>BALLOON</b> and the word <b>BANANA</b>?",
            "The distinct letters in BANANA are B, A, and N, and all three of them also appear in BALLOON. "
            "Counting distinct shared letters gives 3 common letters (B, A, and N).",
        ),
        # Practice .4: SUMMER and WINTER -> {S, U, M, E, R} & {W, I, N, T, E, R} = {E, R} = 2 (Answer: A)
        (
            "SUMMER", "WINTER",
            ["2", "3", "4", "5", "6"],
            0,
            "How many common letters do the words <b>SUMMER</b> and <b>WINTER</b> have?",
            "The letters in SUMMER are {S, U, M, E, R} and in WINTER are {W, I, N, T, E, R}. "
            "Only E and R appear in both words, giving 2 common letters.",
        ),
    ]

    for idx, (w1, w2, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_common_letters(w1, w2, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #4 Next Number with Same Digit Sum
def digit_sum(n):
    return sum(int(ch) for ch in str(n))


def next_same_digit_sum(start_n):
    target = digit_sum(start_n)
    n = start_n + 1
    while digit_sum(n) != target:
        n += 1
    return n


def check_same_digit_sum(start_n, choices, ans_idx):
    nxt = next_same_digit_sum(start_n)
    matches = [i for i, ch in enumerate(choices) if int(ch) == nxt]
    assert matches == [ans_idx], f"Next same digit sum after {start_n} is {nxt}, choices={choices}, ans_idx={ans_idx}"


def q_2007_4(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Next Number with the Same Sum of Digits", "Based on 2007, Problem 4")

    opts0 = ["2016", "2115", "2008", "7002", "2070"]
    check_same_digit_sum(2007, opts0, 0)
    if include_orig:
        d.problem(
            "Original 2007 #4.",
            "The numbers 34 and 142 have the same sum of their digits (3+4=7 and 1+4+2=7). "
            "What is the first number greater than 2007 such that the sum of its digits is the same as the sum "
            "of the digits of 2007?",
            choices=opts0,
        )
        key.append((
            "2007 #4",
            "A",
            "The sum of the digits of 2007 is 2 + 0 + 0 + 7 = 9. To find the smallest number greater than 2007 "
            "with digit sum 9, increase the tens digit from 0 to 1 and decrease the ones digit from 7 to 6, giving 2016 "
            "(2 + 0 + 1 + 6 = 9).",
        ))

    practices = [
        # Practice .1: Start = 2026 (sum = 10) -> next is 2035 (2+0+3+5 = 10) (Answer: C)
        (
            2026,
            ["2027", "2034", "2035", "2116", "2062"],
            2,
            "What is the smallest number greater than <b>2026</b> such that the sum of its digits is the same as "
            "the sum of the digits of 2026?",
            "The sum of the digits of 2026 is 2 + 0 + 2 + 6 = 10. Increasing the tens digit from 2 to 3 and "
            "decreasing the ones digit from 6 to 5 gives 2035, which is the first number after 2026 with digit sum 10.",
        ),
        # Practice .2: Start = 1408 (sum = 13) -> next is 1417 (1+4+1+7 = 13) (Answer: B)
        (
            1408,
            ["1409", "1417", "1426", "1507", "1480"],
            1,
            "What is the first number greater than <b>1408</b> whose digits add up to the same sum as the digits of 1408?",
            "The digits of 1408 add up to 1 + 4 + 0 + 8 = 13. The first number after 1408 with digit sum 13 is "
            "1417 (1 + 4 + 1 + 7 = 13).",
        ),
        # Practice .3: Start = 3059 (sum = 17) -> 3068 (3+0+6+8 = 17) (Answer: D)
        (
            3059,
            ["3060", "3067", "3069", "3068", "3158"],
            3,
            "What is the smallest number greater than <b>3059</b> that has the same sum of digits as 3059?",
            "The digit sum of 3059 is 3 + 0 + 5 + 9 = 17. Increasing the tens digit by 1 (from 5 to 6) and decreasing "
            "the ones digit by 1 (from 9 to 8) gives 3068, whose digits also sum to 3 + 0 + 6 + 8 = 17.",
        ),
        # Practice .4: Start = 4090 (sum = 13) -> 4091..4099 have sums 14..22; 4100..4108: 4108 has sum 4+1+0+8 = 13! (Answer: E)
        (
            4090,
            ["4099", "4100", "4190", "4180", "4108"],
            4,
            "What is the first number greater than <b>4090</b> such that the sum of its digits equals the sum of the digits of 4090?",
            "The sum of the digits of 4090 is 4 + 0 + 9 + 0 = 13. Every number from 4091 to 4099 has a digit sum larger "
            "than 13. Moving to the 4100s, we need the last two digits to sum to 13 - (4 + 1) = 8, which gives 4108.",
        ),
    ]

    for idx, (s_num, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_same_digit_sum(s_num, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #12 Calendar Birthday Offset
def check_birthday_offset(base_date_tuple, rel, years_diff, days_diff, choices_tuples, ans_idx):
    from datetime import date, timedelta
    y, m, day = base_date_tuple
    # Shift by years first, then days
    # rel == "older": base person is older than target -> target was born LATER (+years, +days)
    # rel == "younger": base person is younger than target -> target was born EARLIER (-years, -days)
    if rel == "older":
        mid = date(y + years_diff, m, day)
        res = mid + timedelta(days=days_diff)
    else:
        mid = date(y - years_diff, m, day)
        res = mid - timedelta(days=days_diff)
    res_tuple = (res.year, res.month, res.day)
    matches = [i for i, ct in enumerate(choices_tuples) if ct == res_tuple]
    assert matches == [ans_idx], f"Birthday offset got {res_tuple}, choices={choices_tuples}, ans_idx={ans_idx}"


def q_2007_12(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Calendar & Birthday Date Reasoning", "Based on 2007, Problem 12")

    # Original 2007 #12: Basil (born Jan 1, 2002) is older than Peter by 1 year and 1 day -> Peter born Jan 2, 2003 (A)
    c_tuples0 = [(2003, 1, 2), (2001, 1, 2), (2000, 12, 31), (2002, 12, 31), (2003, 12, 31)]
    opts0 = ["January 2, 2003", "January 2, 2001", "December 31, 2000", "December 31, 2002", "December 31, 2003"]
    check_birthday_offset((2002, 1, 1), "older", 1, 1, c_tuples0, 0)
    if include_orig:
        d.problem(
            "Original 2007 #12.",
            "Basil, who is older than Peter by one year and one day, was born on January 1, 2002. "
            "What is the date of Peter's birthday?",
            choices=opts0,
            choice_cols=3,
        )
        key.append((
            "2007 #12",
            "A",
            "Since Basil is older than Peter, Peter is younger and was born 1 year and 1 day AFTER Basil. "
            "One year after January 1, 2002 is January 1, 2003, and one day after that is January 2, 2003.",
        ))

    practices = [
        # Practice .1: Clara (born Jan 1, 2015) is YOUNGER than Leo by 1 year and 1 day -> Leo born 1 yr 1 day BEFORE Jan 1, 2015 = Dec 31, 2013 (Answer: C)
        (
            (2015, 1, 1), "younger", 1, 1,
            [(2016, 1, 2), (2014, 1, 2), (2013, 12, 31), (2014, 12, 31), (2016, 12, 31)],
            ["January 2, 2016", "January 2, 2014", "December 31, 2013", "December 31, 2014", "December 31, 2016"],
            2,
            "Clara, who is <b>younger</b> than Leo by one year and one day, was born on January 1, 2015. "
            "What is the date of Leo's birthday?",
            "Because Clara is younger than Leo, Leo is older and was born 1 year and 1 day BEFORE Clara. "
            "One year before January 1, 2015 is January 1, 2014, and one day before that is December 31, 2013.",
        ),
        # Practice .2: Max (born Dec 31, 2010) is OLDER than Nina by 1 year and 2 days -> Nina born 1 yr 2 days AFTER Dec 31, 2010 = Jan 2, 2012 (Answer: B)
        (
            (2010, 12, 31), "older", 1, 2,
            [(2011, 1, 2), (2012, 1, 2), (2009, 12, 29), (2011, 12, 29), (2012, 1, 1)],
            ["January 2, 2011", "January 2, 2012", "December 29, 2009", "December 29, 2011", "January 1, 2012"],
            1,
            "Max, who is <b>older</b> than Nina by one year and two days, was born on December 31, 2010. "
            "What is the date of Nina's birthday?",
            "Since Max is older than Nina, Nina was born 1 year and 2 days AFTER December 31, 2010. "
            "One year later is December 31, 2011, and two days after that is January 2, 2012.",
        ),
        # Practice .3: Sophia (born May 1, 2014) is YOUNGER than Ethan by 2 years and 1 day -> Ethan born 2 yrs 1 day BEFORE May 1, 2014 = April 30, 2012 (Answer: D)
        (
            (2014, 5, 1), "younger", 2, 1,
            [(2016, 5, 2), (2012, 5, 2), (2012, 4, 31) if False else (2016, 4, 30), (2012, 4, 30), (2013, 4, 30)],
            ["May 2, 2016", "May 2, 2012", "April 30, 2016", "April 30, 2012", "April 30, 2013"],
            3,
            "Sophia, who is <b>younger</b> than Ethan by two years and one day, was born on May 1, 2014. "
            "What is the date of Ethan's birthday?",
            "Since Sophia is younger than Ethan, Ethan was born 2 years and 1 day BEFORE May 1, 2014. "
            "Two years before May 1, 2014 is May 1, 2012, and one day before May 1, 2012 is April 30, 2012.",
        ),
        # Practice .4: Lucas (born Jan 1, 2018) is OLDER than Maya by 2 years and 3 days -> Maya born Jan 4, 2020 (Answer: E)
        (
            (2018, 1, 1), "older", 2, 3,
            [(2015, 12, 29), (2016, 1, 4), (2019, 1, 4), (2020, 12, 29), (2020, 1, 4)],
            ["December 29, 2015", "January 4, 2016", "January 4, 2019", "December 29, 2020", "January 4, 2020"],
            4,
            "Lucas, who is <b>older</b> than Maya by two years and three days, was born on January 1, 2018. "
            "What is the date of Maya's birthday?",
            "Because Lucas is older, Maya was born 2 years and 3 days AFTER January 1, 2018. "
            "Two years after January 1, 2018 is January 1, 2020, and 3 days later is January 4, 2020.",
        ),
    ]

    for idx, (b_date, rel, yd, dd, c_tups, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_birthday_offset(b_date, rel, yd, dd, c_tups, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #17 Painted Cube Cut into Unit Cubes
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


# ------------------------------------------------- Set: 2007 #21 Growing Grid Pattern of Black & White Cells
def fig_bw_grid_pattern(grid_specs, s=8.5):
    """grid_specs: list of (N, is_black_fn, caption_str)."""
    gap = 14
    widths = [max(N * s, 54) for N, _, _ in grid_specs]
    w = sum(widths) + gap * (len(grid_specs) - 1)
    h = max(N * s for N, _, _ in grid_specs) + 16

    def draw(c, x, y):
        cx = x
        for (N, is_black_fn, cap), box_w in zip(grid_specs, widths):
            gw = N * s
            gx = cx + (box_w - gw) / 2
            gy = y + 14
            for r in range(N):
                for col in range(N):
                    if is_black_fn(r, col, N):
                        c.setFillColor(colors.Color(0.35, 0.35, 0.35))
                    else:
                        c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.setLineWidth(0.75)
                    c.rect(gx + col * s, gy + (N - 1 - r) * s, s, s, stroke=1, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawCentredString(cx + box_w / 2, gy - 10, cap)
            cx += box_w + gap
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

    return w, h, draw


def check_bw_pattern(step_fn, step_idx, choices, ans_idx):
    val = step_fn(step_idx)
    matches = [i for i, ch in enumerate(choices) if int(ch) == val]
    assert matches == [ans_idx], f"BW pattern step {step_idx} -> {val}, choices={choices}, ans_idx={ans_idx}"


def q_2007_21(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Growing Pattern of Black and White Grid Cells", "Based on 2007, Problem 21")

    # Original 2007 #21: step k (k=1,2,3...) has grid size (2k+1)x(2k+1) and k^2 black cells (at odd 0-indexed r,c)
    orig_black_fn = lambda r, c, N: (r % 2 == 1 and c % 2 == 1)
    orig_white_step = lambda k: (2 * k + 1) ** 2 - k ** 2
    assert [orig_white_step(1), orig_white_step(2), orig_white_step(3)] == [8, 21, 40]
    opts0 = ["50", "60", "65", "70", "75"]
    check_bw_pattern(orig_white_step, 4, opts0, 2)

    orig_specs = [
        (3, orig_black_fn, "8 white cells"),
        (5, orig_black_fn, "21 white cells"),
        (7, orig_black_fn, "40 white cells"),
    ]
    if include_orig:
        d.problem(
            "Original 2007 #21.",
            "The following three diagrams represent a pattern in the arrangement of the black and white cells. "
            "If the pattern continues, how many white cells will the next diagram have?",
            fig_bw_grid_pattern(orig_specs),
            "right",
            opts0,
        )
        key.append((
            "2007 #21",
            "C",
            "The grids are 3×3 (with 1×1 = 1 black cell), 5×5 (with 2×2 = 4 black cells), and 7×7 (with 3×3 = 9 black cells). "
            "The 4th diagram is a 9×9 grid (81 cells) with 4×4 = 16 black cells, leaving 81 - 16 = 65 white cells.",
        ))

    practices = [
        # Practice .1: Same diagram, ask for the 5th diagram (11x11 = 121 total - 5^2=25 black = 96 white cells) (Answer: D)
        (
            orig_specs,
            orig_white_step,
            5,
            ["75", "84", "90", "96", "105"],
            3,
            "The three diagrams show the first 3 steps of a pattern of black and white cells (with 8, 21, and 40 white cells). "
            "If the pattern continues, how many white cells will the <b>5th diagram</b> have?",
            "In step k, the grid is (2k + 1) × (2k + 1) and has k × k black cells. For the 5th diagram (k = 5), "
            "the grid is 11 × 11 = 121 cells with 5 × 5 = 25 black cells, leaving 121 - 25 = 96 white cells.",
        ),
        # Practice .2: Diagonal black cells on k+2 grid (k=1: 3x3 with 3 black on diagonal -> 6 white; k=2: 4x4 with 4 black -> 12 white; k=3: 5x5 with 5 black -> 20 white; next k=4: 6x6 - 6 = 30 white) (Answer: B)
        (
            [
                (3, lambda r, c, N: r == c, "6 white cells"),
                (4, lambda r, c, N: r == c, "12 white cells"),
                (5, lambda r, c, N: r == c, "20 white cells"),
            ],
            lambda k: (k + 2) ** 2 - (k + 2),
            4,
            ["24", "30", "32", "36", "42"],
            1,
            "The three diagrams show a pattern where the main diagonal is shaded grey (with 6, 12, and 20 white cells). "
            "How many white cells will the <b>next</b> diagram in the pattern have?",
            "The grids are 3×3 (9 - 3 = 6 white), 4×4 (16 - 4 = 12 white), and 5×5 (25 - 5 = 20 white). "
            "The next grid is 6×6 = 36 cells with 6 diagonal grey cells, giving 36 - 6 = 30 white cells.",
        ),
        # Practice .3: Border white, inner (k)x(k) black! Wait: let's do checkerboard corners or plus-cross!
        # Let's do: step k has (2k+1)x(2k+1) grid where the center row and center column are grey (a cross of 4k+1 grey cells),
        # leaving 4 * k^2 white cells!
        # k=1 (3x3): 4 white cells; k=2 (5x5): 16 white cells; k=3 (7x7): 36 white cells; k=4 (9x9): 64 white cells (Answer: E)
        (
            [
                (3, lambda r, c, N: r == N // 2 or c == N // 2, "4 white cells"),
                (5, lambda r, c, N: r == N // 2 or c == N // 2, "16 white cells"),
                (7, lambda r, c, N: r == N // 2 or c == N // 2, "36 white cells"),
            ],
            lambda k: 4 * (k ** 2),
            4,
            ["48", "52", "56", "60", "64"],
            4,
            "In the pattern shown, the middle row and middle column of each odd-sized square grid are shaded grey "
            "(leaving 4, 16, and 36 white cells in the first three diagrams). How many white cells will the <b>next</b> diagram have?",
            "In each diagram, the grey cross splits the white cells into 4 identical k × k corners: "
            "4 × 1² = 4, 4 × 2² = 16, and 4 × 3² = 36. In the 4th diagram (a 9 × 9 grid), there are 4 × 4² = 64 white cells.",
        ),
        # Practice .4: Original pattern, how many MORE white cells does the 4th diagram have than the 3rd diagram? 65 - 40 = 25 (Answer: A)
        (
            orig_specs,
            lambda k: orig_white_step(k) - orig_white_step(k - 1),
            4,
            ["25", "23", "21", "19", "16"],
            0,
            "Look at the three diagrams of black and white cells (with 8, 21, and 40 white cells). "
            "How many <b>more</b> white cells will the 4th diagram have than the 3rd diagram?",
            "The number of white cells increases by 21 - 8 = 13 from the 1st to the 2nd diagram, and by 40 - 21 = 19 "
            "from the 2nd to the 3rd diagram (6 more each step). The next increase is 19 + 6 = 25 more white cells "
            "(since the 4th diagram has 65 white cells and 65 - 40 = 25).",
        ),
    ]

    for idx, (specs, s_fn, s_idx, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_bw_pattern(s_fn, s_idx, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_bw_grid_pattern(specs),
            "right",
            opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #23 Total Digits from 1 to N
def check_digits_range(start_n, end_n, choices, ans_idx):
    tot = sum(len(str(x)) for x in range(start_n, end_n + 1))
    matches = [i for i, ch in enumerate(choices) if int(ch) == tot]
    assert matches == [ans_idx], f"Digits from {start_n} to {end_n} -> {tot}, choices={choices}, ans_idx={ans_idx}"


def q_2007_23(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Total Digits Written from 1 to N", "Based on 2007, Problem 23")

    opts0 = ["100", "150", "190", "192", "200"]
    check_digits_range(1, 100, opts0, 3)
    if include_orig:
        d.problem(
            "Original 2007 #23.",
            "How many digits are needed to write down all numbers from 1 to 100?",
            choices=opts0,
        )
        key.append((
            "2007 #23",
            "D",
            "Numbers 1 to 9 have 1 digit each (9 × 1 = 9 digits). Numbers 10 to 99 have 2 digits each "
            "(90 × 2 = 180 digits). The number 100 has 3 digits. In total, 9 + 180 + 3 = 192 digits are needed.",
        ))

    practices = [
        # Practice .1: 1 to 50 -> 9*1 + 41*2 = 9 + 82 = 91 digits (Answer: B)
        (
            1, 50,
            ["50", "91", "99", "100", "101"],
            1,
            "How many digits are needed to write down all whole numbers from <b>1 to 50</b>?",
            "The 9 one-digit numbers (1 to 9) use 9 × 1 = 9 digits. The 41 two-digit numbers (10 to 50) use "
            "41 × 2 = 82 digits. Altogether, 9 + 82 = 91 digits are needed.",
        ),
        # Practice .2: 1 to 120 -> 9*1 + 90*2 + 21*3 = 9 + 180 + 63 = 252 digits (Answer: C)
        (
            1, 120,
            ["240", "249", "252", "260", "360"],
            2,
            "How many digits are needed to write down all whole numbers from <b>1 to 120</b>?",
            "Numbers 1–9 use 9 × 1 = 9 digits; numbers 10–99 use 90 × 2 = 180 digits; and the 21 three-digit numbers "
            "from 100 to 120 use 21 × 3 = 63 digits. In total, 9 + 180 + 63 = 252 digits are needed.",
        ),
        # Practice .3: 1 to 80 -> 9*1 + 71*2 = 9 + 142 = 151 digits (Answer: A)
        (
            1, 80,
            ["151", "153", "160", "161", "169"],
            0,
            "A locker hallway has 80 lockers numbered from <b>1 to 80</b>. If each digit is a plastic sticker, "
            "how many digit stickers are needed in total?",
            "Lockers 1–9 need 9 × 1 = 9 stickers, and lockers 10–80 (71 lockers) need 71 × 2 = 142 stickers. "
            "That is 9 + 142 = 151 digit stickers in total.",
        ),
        # Practice .4: 10 to 100 -> 90*2 + 1*3 = 183 digits (Answer: E)
        (
            10, 100,
            ["180", "181", "182", "192", "183"],
            4,
            "How many digits are needed to write down all whole numbers from <b>10 to 100</b> (inclusive)?",
            "There are 90 two-digit numbers from 10 to 99, using 90 × 2 = 180 digits, plus the three-digit number 100, "
            "which uses 3 digits. That gives 180 + 3 = 183 digits.",
        ),
    ]

    for idx, (s_n, e_n, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
        check_digits_range(s_n, e_n, opts, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


# ------------------------------------------------- Set: 2007 #24 Twice-Folded Square Paper Cut
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


# Registry of dedicated per-question implementations.
# Every new (year, number) MUST be implemented as its own q_<year>_<num>(d, key, set_num) method!
QUESTIONS = {
    (2002, 1): q_2002_1,
    (2002, 4): q_2002_4,
    (2002, 6): q_2002_6,
    (2002, 7): q_2002_7,
    (2002, 9): q_2002_9,
    (2002, 10): q_2002_10,
    (2002, 11): q_2002_11,
    (2002, 12): q_2002_12,
    (2002, 15): q_2002_15,
    (2002, 18): q_2002_18,
    (2002, 20): q_2002_20,
    (2002, 21): q_2002_21,
    (2002, 22): q_2002_22,
    (2002, 24): q_2002_24,
    (2003, 9): q_2003_9,
    (2003, 10): q_2003_10,
    (2003, 12): q_2003_12,
    (2003, 14): q_2003_14,
    (2003, 16): q_2003_16,
    (2003, 17): q_2003_17,
    (2003, 18): q_2003_18,
    (2007, 1): q_2007_1,
    (2007, 3): q_2007_3,
    (2007, 4): q_2007_4,
    (2007, 8): q_2007_8,
    (2007, 10): q_2007_10,
    (2007, 12): q_2007_12,
    (2007, 14): q_2007_14,
    (2007, 17): q_2007_17,
    (2007, 21): q_2007_21,
    (2007, 23): q_2007_23,
    (2007, 24): q_2007_24,
}

NUM_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


class _ProblemCollector:
    """Duck-typed Doc collector to harvest custom practice variations from any q_<year>_<num> method."""

    def __init__(self):
        self.problems = []

    def heading(self, text, sub=None):
        pass

    def problem(self, label, text, fig=None, fig_pos="right", choices=None, choice_cols=5):
        self.problems.append((label, text, fig, fig_pos, choices, choice_cols))


def parse_question_pool(pool_path="question-pool.txt"):
    pool = []
    with open(pool_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            yr_str, nums_str = line.split(":", 1)
            yr = int(yr_str.strip())
            for part in nums_str.split(","):
                part = part.strip()
                if part:
                    q_id = (yr, int(part))
                    if q_id not in pool:
                        pool.append(q_id)
    return pool


def generate_exam(pool_path="question-pool.txt", out_pdf=None, num_questions=20, seed=None):
    import random
    import inspect

    if out_pdf is None:
        out_pdf = get_timestamp_filename()

    pool = parse_question_pool(pool_path)
    missing = [q for q in pool if q not in QUESTIONS]
    if missing:
        raise NotImplementedError(
            f"Questions {missing} in {pool_path} do not have dedicated methods yet! "
            "Inspect the source PDF(s) and implement q_<year>_<num> for each one."
        )

    rng = random.Random(seed)
    if len(pool) >= num_questions:
        selected_q_ids = rng.sample(pool, num_questions)
    else:
        selected_q_ids = list(pool)
        while len(selected_q_ids) < num_questions:
            selected_q_ids.append(rng.choice(pool))
        rng.shuffle(selected_q_ids)

    d = Doc(out_pdf)
    c = d.c
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(PW / 2, PH - 68, "Math Kangaroo Practice Exam - Grades 3-4")
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(
        PW / 2,
        PH - 86,
        f"{num_questions} Randomly Selected Practice Questions (Similar to Contest Problems — Never Originals)",
    )
    c.setLineWidth(0.9)
    c.line(ML, PH - 96, PW - MR, PH - 96)
    d.y = PH - 112

    exam_key = []
    used_variations = {}

    for q_idx, q_id in enumerate(selected_q_ids, start=1):
        fn = QUESTIONS[q_id]
        collector = _ProblemCollector()
        temp_key = []
        sig = inspect.signature(fn)
        if "num_practice" in sig.parameters:
            fn(collector, temp_key, set_num=q_idx, include_orig=False, num_practice=5)
        else:
            fn(collector, temp_key, set_num=q_idx, include_orig=False)

        assert len(collector.problems) == len(temp_key) and len(collector.problems) > 0
        avail = [i for i in range(len(collector.problems)) if i not in used_variations.get(q_id, set())]
        if not avail:
            avail = list(range(len(collector.problems)))
        chosen_var = rng.choice(avail)
        used_variations.setdefault(q_id, set()).add(chosen_var)

        _, text, fig, fig_pos, choices, choice_cols = collector.problems[chosen_var]
        _, ans_letter, expl = temp_key[chosen_var]

        d.problem(
            f"Question {q_idx}.",
            text,
            fig=fig,
            fig_pos=fig_pos,
            choices=choices,
            choice_cols=choice_cols,
        )
        exam_key.append((f"Question {q_idx} (inspired by {q_id[0]} #{q_id[1]})", ans_letter, expl))

    append_answer_key(
        d,
        exam_key,
        title="Answer Key - 20-Question Practice Exam",
        subtitle=f"For {out_pdf} (Randomly sampled from {pool_path})",
    )
    d.save()
    print("wrote", out_pdf)
    return out_pdf, selected_q_ids


def generate_set(selected_questions, out_pdf, subtitle, include_orig=True, out_key_pdf=None, num_practice=3):
    missing = [q for q in selected_questions if q not in QUESTIONS]
    if missing:
        raise NotImplementedError(
            f"Questions {missing} do not have dedicated methods yet! "
            "Inspect the source PDF(s) and implement q_<year>_<num>(d, key, set_num) for each one."
        )
    d = Doc(out_pdf)
    c = d.c
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PW / 2, PH - 70, "Math Kangaroo Practice - Grades 3-4")
    c.setFont("Helvetica", 11)
    c.drawCentredString(PW / 2, PH - 90, subtitle)
    nw = NUM_WORDS.get(num_practice, str(num_practice))
    note = (
        f"Each original problem is followed by {nw} similar practice problems."
        if include_orig
        else f"{nw.capitalize()} practice problems per selected problem."
    )
    c.drawCentredString(PW / 2, PH - 105, note)
    d.y = PH - 130
    key = []

    import inspect
    for idx, q_id in enumerate(selected_questions, start=1):
        fn = QUESTIONS[q_id]
        sig = inspect.signature(fn)
        if "num_practice" in sig.parameters:
            fn(d, key, set_num=idx, include_orig=include_orig, num_practice=num_practice)
        else:
            fn(d, key, set_num=idx, include_orig=include_orig)

    # Append answer key on the last page(s)
    append_answer_key(d, key, subtitle=f"For {out_pdf} ({subtitle})")

    d.save()
    print("wrote", out_pdf)


def build(out_pdf=None):
    if out_pdf is None:
        out_pdf = get_timestamp_filename()
    selected = [(2002, 4), (2002, 7), (2002, 9), (2003, 9), (2003, 12), (2003, 14)]
    generate_set(
        selected,
        out_pdf,
        "Selected problems from 2002 (#4, #7, #9) and 2003 (#9, #12, #14)",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Math Kangaroo practice sets.")
    parser.add_argument(
        "--questions",
        nargs="+",
        default=None,
        help="List of questions in year:number format, e.g. 2007:14 or 2002:4 2003:9",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output filename or path (e.g. filename.pdf). If omitted, defaults to generated/YYYY-MM-DD-HH-MM-SS.pdf",
    )
    parser.add_argument(
        "--no-include-orig",
        action="store_true",
        help="Omit original contest problems, generating only practice problems.",
    )
    parser.add_argument(
        "--num-practice",
        type=int,
        default=3,
        help="Number of practice problems per original question (default: 3).",
    )
    parser.add_argument(
        "--random-exam",
        type=int,
        nargs="?",
        const=20,
        default=None,
        help="Generate a random N-question exam (default 20) from question-pool.txt using only similar practice problems.",
    )
    parser.add_argument(
        "--pool",
        default="question-pool.txt",
        help="Path to the question pool file (default: question-pool.txt).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible exam generation.",
    )
    args = parser.parse_args()

    if args.out:
        fname = args.out if args.out.endswith(".pdf") else f"{args.out}.pdf"
        out_pdf = ensure_gen_path(fname)
    else:
        out_pdf = get_timestamp_filename()

    include_orig = not args.no_include_orig

    if args.random_exam is not None:
        generate_exam(
            pool_path=args.pool,
            out_pdf=out_pdf,
            num_questions=args.random_exam,
            seed=args.seed,
        )
    elif args.questions:
        selected = []
        for q in args.questions:
            parts = q.replace("#", "").split(":")
            selected.append((int(parts[0]), int(parts[1])))
        desc = ", ".join(f"{y} #{n}" for y, n in selected)
        generate_set(
            selected,
            out_pdf,
            f"Practice set for {desc}",
            include_orig=include_orig,
            num_practice=args.num_practice,
        )
    else:
        build(out_pdf)



