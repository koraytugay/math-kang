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
        self.need(60)
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


# Registry of dedicated per-question implementations.
# Every new (year, number) MUST be implemented as its own q_<year>_<num>(d, key, set_num) method!
QUESTIONS = {
    (2002, 1): q_2002_1,
    (2002, 4): q_2002_4,
    (2002, 6): q_2002_6,
    (2002, 7): q_2002_7,
    (2002, 9): q_2002_9,
    (2003, 9): q_2003_9,
    (2003, 12): q_2003_12,
    (2003, 14): q_2003_14,
    (2003, 18): q_2003_18,
    (2007, 1): q_2007_1,
    (2007, 8): q_2007_8,
    (2007, 10): q_2007_10,
    (2007, 14): q_2007_14,
}


def generate_set(selected_questions, out_pdf, subtitle, include_orig=True, out_key_pdf=None):
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
    note = (
        "Each original problem is followed by three similar practice problems."
        if include_orig
        else "Three practice problems per selected problem."
    )
    c.drawCentredString(PW / 2, PH - 105, note)
    d.y = PH - 130
    key = []

    for idx, q_id in enumerate(selected_questions, start=1):
        QUESTIONS[q_id](d, key, set_num=idx, include_orig=include_orig)

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
    args = parser.parse_args()

    if args.out:
        fname = args.out if args.out.endswith(".pdf") else f"{args.out}.pdf"
        out_pdf = ensure_gen_path(fname)
    else:
        out_pdf = get_timestamp_filename()

    include_orig = not args.no_include_orig

    if args.questions:
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
        )
    else:
        build(out_pdf)
