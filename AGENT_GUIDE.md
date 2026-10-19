# Agent Guide: Math Kangaroo Practice-PDF Workflow

Read this entire file before doing anything.

---

## Core Rule: Every Question Gets Its Own Dedicated Implementation

Math Kangaroo problems are unique. **We do NOT use generic question generators.**
Every single contest problem (`<year> #<number>`) must have **its own dedicated, custom-written method**
(`q_<year>_<number>`) implemented from scratch the first time the user requests it.

- Each question's method is responsible for:
  1. Redrawing that specific question's exact visual/diagram (if any) using custom ReportLab code tailored to that problem.
  2. Verifying the math/logic with a custom assertion/solver specific to that problem.
  3. Rendering the original problem and the requested number of custom-crafted similar practice problems.
- **Never** try to force-fit a new question into another question's helper or a generic template.
  When the user asks for `2007 - 5`, you must inspect Question 5 of `2007.pdf` and write a brand-new,
  bespoke implementation specifically for `2007 #5`.

---

## 1. What the user wants

The folder `/Users/kt/mathkang` holds past **Math Kangaroo** contest PDFs (`2002.pdf`, `2003.pdf`, `2007.pdf`,
and any new PDFs the user adds over time).

When the user specifies questions (via `PROMPT_TEMPLATE.md` or directly in chat, e.g.
`2002: 4, 7, 9` and `2003: 9, 12, 14`), you must:

1. Check which of the requested `(year, number)` questions already have a dedicated `q_<year>_<number>` method
   in `generate_practice.py`, and which ones are **new (not yet implemented)**.
2. For every **new** question:
   - Extract the text and render a high-DPI crop of that specific question from `<year>.pdf`.
   - Visually inspect the image carefully (count every grid line, cube, shape, etc.) and solve the original problem.
   - Write a **brand-new dedicated method `q_<year>_<number>(d, key)`** (plus its own bespoke drawing and
     answer-checking helper functions) specifically for that question.
3. Generate **a brand-new worksheet PDF for every request in the `generated/` folder**:
   - **Never amend or overwrite existing generated files.** Every time questions are requested, generate a completely new worksheet PDF.
   - **Keep the repository root clean:** All generated worksheet PDFs must be stored inside the `generated/` directory (e.g. `generated/YYYY-MM-DD-HH-MM-SS.pdf`).
   - Name each generated PDF using the current timestamp in the format `generated/YYYY-MM-DD-HH-MM-SS.pdf` (e.g. `generated/2026-10-19-12-14-56.pdf`), unless the user explicitly requested a custom filename.
   - The PDF contains the problems on the initial page(s), followed by the **Answer Key & Explanations on the final page(s)** (always starting on a fresh new page at the very end).
   - Do **NOT** generate a separate answer key file.

---

## 2. Environment setup (macOS)

The Mac does **not** have `pdftotext`, `pdflatex` or `pandoc`, and the file-viewer tool **cannot open PDFs
directly**. Use the Python virtualenv with PyMuPDF (`fitz`) and ReportLab:

```bash
cd /Users/kt/mathkang
python3 -m venv .venv            # skip if .venv already exists
.venv/bin/pip install -q pymupdf reportlab
```

Run everything with `.venv/bin/python`.

---

## 3. Step-by-step workflow for every new question `<year> #<num>`

### Step 1: Extract text and render page images for `<year>.pdf`
```python
import fitz  # PyMuPDF
d = fitz.open("2007.pdf")
for i, p in enumerate(d):
    print("--- page", i + 1); print(p.get_text())
    p.get_pixmap(dpi=120).save(f"scratch/2007_p{i+1}.png")
```
Save temporary images in your **artifact scratch directory**, not in `/Users/kt/mathkang`.
**Always view the rendered page image** using `view_file` — never rely on extracted text alone.

### Step 2: Zoom in on the specific question's figure
Page size is 612×792 pt. Crop and render at 300–500 DPI so you can see every detail:
```python
p.get_pixmap(dpi=400, clip=fitz.Rect(x0, y0, x1, y1)).save("scratch/q_2007_5.png")
```
View the cropped image. Count every grid cell, segment, cube, shading, or label.

### Step 3: Solve the original problem and design the practice variations
- There is **no official answer key** in the source PDFs. Solve the original problem carefully and double-check.
- Design the requested number of practice problems (default 3) specifically around this question's exact concept:
  - Keep the exact same mathematical/visual mechanism, changing the numbers, shapes, or story.
  - Spread the correct answers across different letters (`A`–`E`).
  - Make wrong choices plausible and **assert in code** that there is **only one** valid answer.
  - The final practice variation in a set can include a fun small twist (e.g., asking for the complement).

### Step 4: Implement a dedicated `q_<year>_<num>(d, key, set_num)` method
Write bespoke helper functions and a dedicated `q_<year>_<num>(d, key, set_num)` function in
`generate_practice.py` (and register it in `QUESTIONS[(year, num)]`).

What `generate_practice.py` provides for **page layout only**:
- `Doc(path)`: PDF page canvas with automatic page breaks and page-number footers.
  - `d.heading(title, subtitle)`
  - `d.problem(label, html_text, fig=None, fig_pos="right"|"below", choices=None, choice_cols=5)`
- `option_row(items, gap=18)`: places 5 `(w, h, draw_fn)` figures in a horizontal row labelled `A)`–`E)`.
- `vstack(figs, gap=12)` and `hstack(figs, gap=20)`: stack `(w, h, draw_fn)` figures vertically or horizontally.
- `append_answer_key(d, key, title, subtitle)`: appends the answer key and kid-friendly explanations starting on a fresh new page at the end of the document.

Every custom figure function you write for a question simply returns `(width_pt, height_pt, draw_fn(c, x, y))`,
where `(x, y)` is the bottom-left corner of the figure box on the ReportLab canvas `c`.

### Step 5: Build the PDF and inspect every page visually
Render every page of the generated worksheet PDF (including the problem pages and the final answer key page) to images in `scratch/` and view them:
```python
d = fitz.open(out_pdf)
for i, p in enumerate(d):
    p.get_pixmap(dpi=90).save(f"scratch/out_p{i+1}.png")
```
Verify:
1. All text and answer choices `A)`–`E)` are visible (nothing accidentally drawn in white).
2. The redrawn figures accurately match the original question and the new variations.
3. No watermarks ("DO NOT COPY" must never appear — never paste bitmap crops from the source PDF).
4. Problem pages contain **no answers**, and the final page(s) contain the full answer key with clear, kid-friendly explanations.

---

## 4. Currently Implemented Questions in `generate_practice.py`

Only the following 9 questions have been implemented so far:

| Question ID | Function in `generate_practice.py` | Description |
|---|---|---|
| `(2002, 4)` | `q_2002_4(d, key, set_num)` | 4×4 / 5×5 square cut along grid lines into polyomino pieces |
| `(2002, 7)` | `q_2002_7(d, key, set_num)` | Castle skyline contour — which piece cannot belong |
| `(2002, 9)` | `q_2002_9(d, key, set_num)` | Tilted/level two-pan balance scale with fruits |
| `(2003, 9)` | `q_2003_9(d, key, set_num)` | 3D W×H×D brick of cubes (red outside, blue inside) |
| `(2003, 12)` | `q_2003_12(d, key, set_num)` | 2D paper net of a house folded into 3D isometric houses A–E |
| `(2003, 14)` | `q_2003_14(d, key, set_num)` | Area of block letters (N, Z, V, M) on a 1 cm square grid |
| `(2007, 1)` | `q_2007_1(d, key, set_num)` | Forking road diagram — choosing one number/letter per road split |
| `(2007, 10)` | `q_2007_10(d, key, set_num)` | 3×3 mini-sudoku — placing numbers 1, 2, 3 in rows and columns |
| `(2007, 14)` | `q_2007_14(d, key, set_num)` | 3D cube aquarium (3×3×3) — counting 1 dm cubes inside / missing to fill |

**Any other `(year, number)` requested by the user is NEW** — you must inspect the source PDF and implement
a new dedicated `q_<year>_<number>(d, key, set_num)` function for it!

---

## 5. Hard Lessons from Run #1 (Do Not Repeat)

1. **Always reset canvas colors:** In ReportLab, setting `c.setFillColor(colors.white)` stays active until changed.
   Every custom `draw(c, x, y)` function **must** end with `c.setFillColor(colors.black)` and
   `c.setStrokeColor(colors.black)` or the next problem's text will be invisible!
2. **Write a programmatic checker for every question:** In Run #1, an option tuple for `2003 #12` had its arguments
   swapped, and `check_house` caught it immediately. Always write an `assert` that verifies the math/geometry of
   your question and its options.
3. **Check figure scale visually:** In Run #1, the house net was initially too small (`s=19`) to read the window/door
   markings clearly and had to be bumped to `s=27`. Always inspect the rendered PNGs of your output PDF.
4. **Answer key is ALWAYS on the last page of the PDF:** Never generate a separate answer key PDF file. Always
   append the answer key starting on a fresh new page at the very end of the worksheet PDF.
5. **Always create a new timestamped file in `generated/`:** Never amend or overwrite previous worksheet PDFs. Every time questions are requested,
   generate a fresh PDF inside `generated/` named with the current timestamp `generated/YYYY-MM-DD-HH-MM-SS.pdf` to keep the root clean.
