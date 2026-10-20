# Shared layout and figure composition utilities for Math Kangaroo question generators.
import os
import math
import itertools
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

GEN_DIR = "generated"
OUT = os.path.join(GEN_DIR, "practice_2002_2003.pdf")
PW, PH = letter
ML, MR, MT, MB = 54, 54, 60, 54
TW = PW - ML - MR
LETTERS = "ABCDE"
DARK = colors.Color(0.25, 0.25, 0.25)
GRAY = colors.Color(0.78, 0.78, 0.78)
NUM_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=11, leading=15)


def get_timestamp_filename():
    os.makedirs(GEN_DIR, exist_ok=True)
    return os.path.join(GEN_DIR, datetime.now().strftime("%Y-%m-%d-%H-%M-%S.pdf"))


def ensure_gen_path(path):
    os.makedirs(GEN_DIR, exist_ok=True)
    if not os.path.dirname(path):
        return os.path.join(GEN_DIR, path)
    return path


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


class _ProblemCollector:
    """Duck-typed Doc collector to harvest custom practice variations from any q_<year>_<num> method."""

    def __init__(self):
        self.problems = []

    def heading(self, text, sub=None):
        pass

    def problem(self, label, text, fig=None, fig_pos="right", choices=None, choice_cols=5):
        self.problems.append((label, text, fig, fig_pos, choices, choice_cols))
