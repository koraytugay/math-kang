"""Generate Math Kangaroo practice sets (originals + similar new problems).

Usage:  python generate_practice.py   ->  writes practice_2002_2003.pdf and practice_2002_2003_answers.pdf
Requires: reportlab
"""
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

OUT = "practice_2002_2003.pdf"
OUT_KEY = "practice_2002_2003_answers.pdf"
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
            c.setFont("Helvetica-Bold", 11)
            c.drawString(cx, y + h - 11, LETTERS[k] + ")")
            fn(c, cx + 16, y + (h - label_h - ih) / 2)
            cx += iw + 16 + gap
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
def write_answer_key(path, title, subtitle, key):
    kd = Doc(path)
    kc = kd.c
    kc.setFont("Helvetica-Bold", 18)
    kc.drawCentredString(PW / 2, PH - 70, title)
    if subtitle:
        kc.setFont("Helvetica", 11)
        kc.drawCentredString(PW / 2, PH - 90, subtitle)
        kd.y = PH - 115
    else:
        kd.y = PH - 95
    kd.heading("Answer key & explanations")
    for lab, ans, why in key:
        p = Paragraph("<b>%s:&nbsp; %s</b>&nbsp;&nbsp;&nbsp;%s" % (lab, ans, why), BODY)
        _, ph = p.wrap(TW, 1000)
        kd.need(ph + 8)
        p.drawOn(kd.c, ML, kd.y - ph)
        kd.y -= ph + 8
    kd.save()
    print("wrote", path)


def build():
    d = Doc(OUT)
    c = d.c
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PW / 2, PH - 70, "Math Kangaroo Practice - Grades 3-4")
    c.setFont("Helvetica", 11)
    c.drawCentredString(PW / 2, PH - 90, "Selected problems from 2002 (#4, #7, #9) and 2003 (#9, #12, #14)")
    c.drawCentredString(PW / 2, PH - 105, "Each original problem is followed by three similar practice problems.")
    d.y = PH - 130
    key = []  # (label, answer letter, explanation)

    # ---------------- Set 1 ------------------------------------------------
    d.heading("Set 1 - Cutting a square into pieces", "Based on 2002, Problem 4")
    orig = ["AABD", "ABBD", "CCBF", "EFFF"]
    opts = [[(0, 0)], [(0, 0), (0, 1)], [(0, 0), (0, 1), (1, 1)],
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)], [(0, 0), (1, 0), (2, 0), (2, 1)]]
    d.problem("Original 2002 #4.", "The square was cut along the lines. Which of the shapes below was "
              "<b>not</b> obtained this way?", cut_problem(orig, opts, 3), "below")
    key.append(("2002 #4", "D", "The pieces are: 1 small square, 2 dominoes, an L of 3, a T of 4 and an L of 4. There is no U-shaped piece."))

    g = ["AAAB", "CDAB", "CDDD", "CEEF"]
    o = [[(0, 0)], [(0, 0), (0, 1), (0, 2), (1, 1)], [(0, 0), (0, 1), (0, 2)],
         [(0, 0), (1, 0), (2, 0), (0, 1)], [(0, 0), (1, 0)]]
    d.problem("Practice 1.1", "The square was cut along the lines. Which of the shapes below was "
              "<b>not</b> obtained this way?", cut_problem(g, o, 1), "below")
    key.append(("1.1", "B", "Pieces: two L-shapes of 4, a straight 3, two dominoes, one small square. No T-shape."))

    g = ["AABBB", "ACCBE", "ACDDE", "FCDEE", "FFDGG"]
    o = [[(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1)], [(0, 1), (0, 2), (1, 0), (1, 1)],
         [(0, 1), (1, 0), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)]]
    d.problem("Practice 1.2", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 2), "below")
    key.append(("1.2", "C", "Pieces: four L-shapes of 4, one T, one L of 3, one domino. There is no zig-zag (S) piece."))

    g = ["AAABB", "ACCCB", "DDCEB", "DFFEE", "DFGGG"]
    o = [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 0), (2, 0)],
         [(0, 0), (0, 1), (1, 0), (2, 0)], [(0, 0), (0, 1), (1, 0), (1, 1)]]
    d.problem("Practice 1.3", "This square was cut along the lines. Which shape was <b>not</b> obtained?",
              cut_problem(g, o, 4), "below")
    key.append(("1.3", "E", "Pieces: three L-shapes of 4, one T, two L-shapes of 3, one straight 3. No 2x2 square."))

    # ---------------- Set 2 ------------------------------------------------
    d.heading("Set 2 - Pieces of a skyline", "Based on 2002, Problem 7")
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
    d.problem("Practice 2.1", "Here is the skyline of a town. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.48), "below")
    key.append(("2.1", "A", "In the skyline there is a flat part between the wall and the pointed roof. Piece A has the roof sitting straight on the wall."))

    sky = [("H", 50), ("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -15), ("H", 20),
           ("V", 15), ("H", 25), ("V", -50), ("H", 40), ("A", 50), ("H", 40), ("D", 35, 50), ("H", 40),
           ("D", 35, -50), ("H", 40)]
    pcs = [[("V", -30), ("H", 40), ("A", 50), ("H", 20)],
           [("A", 50), ("H", 40), ("D", 35, 50), ("H", 20)],
           [("H", 20), ("D", 35, -50), ("H", 40)],
           [("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50), ("H", 20)],
           [("V", 50), ("H", 25), ("V", -15), ("H", 20), ("V", 15), ("H", 25), ("V", -50)]]
    d.problem("Practice 2.2", "Here is the skyline of a castle. Which piece <b>cannot</b> belong to it?",
              skyline_problem(sky, pcs, 0.42), "below")
    key.append(("2.2", "E", "The castle wall has TWO notches at the top. Piece E shows a whole tower top with only one notch."))

    sky = [("H", 50), ("A", 30), ("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40), ("V", -60), ("H", 40),
           ("A", 60), ("H", 25), ("V", 90), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 50)]
    pcs = [[("A", 60), ("H", 25), ("V", 60)],
           [("H", 25), ("V", 60), ("D", 25, 40), ("D", 25, -40)],
           [("V", 50), ("H", 25), ("V", -35), ("H", 25), ("V", -55), ("H", 20)],
           [("A", 30), ("H", 25), ("V", -40)],
           [("V", -40), ("H", 40), ("A", 60)]]
    d.problem("Practice 2.3", "Here is a skyline with a small arch, a tower and a dome. Which piece "
              "<b>cannot</b> belong to it?", skyline_problem(sky, pcs, 0.45), "below")
    key.append(("2.3", "D", "After each arch the line goes flat and then UP. Piece D goes down after the arch."))

    # ---------------- Set 3 ------------------------------------------------
    d.heading("Set 3 - Balance scales", "Based on 2002, Problem 9")
    d.problem("Original 2002 #9.", "On one plate of a balance there are 6 oranges (small circles) and on the "
              "other there are melons (big circles). When we put one more melon, exactly like the others, on the "
              "orange plate, the balance is level. The weight of one melon is the same as:",
              fig_balance([4] * 6, [9, 9], 1), "right",
              ["2 oranges", "3 oranges", "4 oranges", "5 oranges", "6 oranges"], 3)
    key.append(("2002 #9", "E", "6 oranges + 1 melon = 2 melons. Take one melon off each side: 6 oranges = 1 melon."))

    d.problem("Practice 3.1", "On one plate there are 8 plums (small circles) and on the other 3 lemons "
              "(gray circles). When we put one more lemon on the plum plate, the balance is level. "
              "One lemon weighs the same as:",
              fig_balance([4] * 8, [7, 7, 7], 1), "right",
              ["2 plums", "3 plums", "4 plums", "5 plums", "8 plums"], 3)
    key.append(("3.1", "C", "8 plums + 1 lemon = 3 lemons, so 8 plums = 2 lemons, so 1 lemon = 4 plums."))

    d.problem("Practice 3.2", "On one plate there are 10 cherries (small circles) and on the other 4 apples "
              "(gray circles). When we put 2 more apples on the cherry plate, the balance is level. "
              "One apple weighs the same as:",
              fig_balance([3.4] * 10, [7, 7, 7, 7], 1), "right",
              ["2 cherries", "3 cherries", "4 cherries", "5 cherries", "10 cherries"], 3)
    key.append(("3.2", "D", "10 cherries + 2 apples = 4 apples, so 10 cherries = 2 apples, so 1 apple = 5 cherries."))

    d.problem("Practice 3.3", "The balance is level. On the left plate there is 1 melon (big circle) and 3 "
              "oranges; on the right plate there are 9 oranges. How many oranges weigh the same as "
              "<b>2 melons</b>?",
              fig_balance([9, 4, 4, 4], [4] * 9, 0), "right", [6, 8, 9, 12, 18])
    key.append(("3.3", "D", "Take 3 oranges off each side: 1 melon = 6 oranges, so 2 melons = 12 oranges."))

    # ---------------- Set 4 ------------------------------------------------
    d.heading("Set 4 - Red outside, blue inside", "Based on 2003, Problem 9")
    d.problem("Original 2003 #9.", "Chris built the brick in the picture using red and blue cubes of the same "
              "size. The outside of the brick is completely red, but all cubes used inside are blue. "
              "How many blue cubes did Chris use?", fig_brick(5, 4, 4), "right", [12, 24, 36, 40, 48])
    key.append(("2003 #9", "A", "Brick is 5 x 4 x 4. Remove the outer layer: inside is 3 x 2 x 2 = 12 blue cubes."))

    d.problem("Practice 4.1", "Maya built this brick (4 cubes wide, 4 cubes tall, 3 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did she use?",
              fig_brick(4, 4, 3), "right", [2, 4, 6, 8, 12])
    key.append(("4.1", "B", "Inside is (4-2) x (4-2) x (3-2) = 2 x 2 x 1 = 4."))

    d.problem("Practice 4.2", "Leo built this brick (6 cubes wide, 3 cubes tall, 4 cubes deep). The outside "
              "is completely red and all the cubes inside are blue. How many blue cubes did he use?",
              fig_brick(6, 3, 4), "right", [4, 6, 8, 12, 16])
    key.append(("4.2", "C", "Inside is (6-2) x (3-2) x (4-2) = 4 x 1 x 2 = 8."))

    d.problem("Practice 4.3", "Anna built this brick (5 cubes wide, 3 cubes tall, 3 cubes deep). The outside "
              "is completely red and the cubes inside are blue. How many <b>red</b> cubes did she use?",
              fig_brick(5, 3, 3), "right", [30, 36, 39, 42, 45])
    key.append(("4.3", "D", "Total = 5 x 3 x 3 = 45. Inside (blue) = 3 x 1 x 1 = 3. Red = 45 - 3 = 42."))

    # ---------------- Set 5 ------------------------------------------------
    d.heading("Set 5 - Folding a house", "Based on 2003, Problem 12")
    tip = ("<i>(The dark parts at the top of the picture are the roof. The shape in the middle is the floor.)</i>")
    net = {"F": "door", "K": None, "L": None, "R": "dot"}
    opts = [("GL", None, "dot"), ("SL", "door", None), ("GL", "door", "dot"), ("SL", None, "dot"), ("GL", None, "door")]
    d.problem("Original 2003 #12.", "The picture has been drawn on paper and cut out to make a house. "
              "Which of the houses did it become? " + tip, house_problem(net, opts, 0), "below")
    key.append(("2003 #12", "A", "Stand in front of the door wall: the dot wall is on your LEFT. So from the back (no door), the dot is on the right of the plain end wall - house A."))

    net = {"F": None, "K": "door", "L": "dot", "R": None}
    opts = [("GL", "door", "dot"), ("SL", "door", None), ("SL", "door", "dot"), ("GL", None, None), ("SL", None, "dot")]
    d.problem("Practice 5.1", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 2), "below")
    key.append(("5.1", "C", "The door is on the end wall that has the roof attached. Facing that door, the dot wall is on your left."))

    net = {"F": "door", "K": "dot", "L": "win", "R": None}
    opts = [("GL", "dot", "win"), ("SL", "door", "win"), ("SL", "dot", None), ("GL", "door", "win"), ("GL", "door", None)]
    d.problem("Practice 5.2", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 3), "below")
    key.append(("5.2", "D", "Facing the door wall, the window wall is on your right and the plain wall on your left. Only D shows that."))

    net = {"F": "dot", "K": None, "L": "door", "R": "win"}
    opts = [("SL", "dot", "door"), ("GL", "dot", "door"), ("GL", None, "door"), ("SL", None, "win"), ("GL", "dot", "win")]
    d.problem("Practice 5.3", "This picture is cut out and folded to make a house. Which house does it become? " + tip,
              house_problem(net, opts, 1), "below")
    key.append(("5.3", "B", "Facing the dot end wall: the door wall is on your right, the window wall on your left. B shows the dot wall with the door wall to its right."))

    # ---------------- Set 6 ------------------------------------------------
    d.heading("Set 6 - Area of a letter on squared paper", "Based on 2003, Problem 14")
    q = "If the side of each little square is 1 cm, what is the area of the letter %s (in square cm)?"
    N = [[(1, 0), (2, 0), (2, 6), (1, 6)], [(5, 0), (6, 0), (6, 6), (5, 6)], [(2, 6), (3, 6), (5, 0), (4, 0)]]
    assert letter_area(N) == 18
    d.problem("Original 2003 #14.", q % "N", fig_letter(7, 6, N), "right", [14, 15, 16, 17, 18])
    key.append(("2003 #14", "E", "Each side bar is 6. The slanted part is a parallelogram 1 wide and 6 tall = 6 (cut-off triangles fit together). 6+6+6 = 18."))

    Z = [[(1, 6), (6, 6), (6, 7), (1, 7)], [(1, 0), (6, 0), (6, 1), (1, 1)], [(4, 6), (6, 6), (3, 1), (1, 1)]]
    assert letter_area(Z) == 20
    d.problem("Practice 6.1", q % "Z", fig_letter(7, 7, Z, 14), "right", [16, 18, 20, 22, 24])
    key.append(("6.1", "C", "Top bar 5 + bottom bar 5 + slanted part (2 wide, 5 tall) 10 = 20."))

    V = [[(1, 5), (3, 5), (4, 2), (5, 5), (7, 5), (5, 0), (3, 0)]]
    assert letter_area(V) == 17
    d.problem("Practice 6.2", q % "V", fig_letter(8, 5, V), "right", [15, 16, 17, 18, 20])
    key.append(("6.2", "C", "Without the notch the shape is a 2 x 5 rectangle (10) plus two side triangles (each half of 2 x 5 = 5), so 20. The white triangle notch at the top is half of 2 x 3 = 3. 20 - 3 = 17."))

    M = [[(1, 0), (2, 0), (2, 5), (1, 5)], [(8, 0), (9, 0), (9, 5), (8, 5)],
         [(2, 5), (5, 2), (8, 5), (8, 3), (5, 0), (2, 3)]]
    assert letter_area(M) == 22
    d.problem("Practice 6.3", q % "M", fig_letter(10, 5, M, 14), "right", [18, 20, 22, 24, 26])
    key.append(("6.3", "C", "Two side bars: 5 + 5 = 10. The middle V is two slanted strips, each 3 across and 2 tall = 6. 10 + 6 + 6 = 22."))

    d.save()
    print("wrote", OUT)

    # ---------------- separate answer key PDF ------------------------------
    write_answer_key(
        OUT_KEY,
        "Math Kangaroo Practice - Answer Key",
        "For practice_2002_2003.pdf (2002: #4, #7, #9  |  2003: #9, #12, #14)",
        key,
    )


if __name__ == "__main__":
    build()
