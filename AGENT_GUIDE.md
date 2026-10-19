# Agent Guide: Math Kangaroo Practice-PDF Workflow

Read this whole file before doing anything. It explains what the user wants, what to ask them, and
exactly how the previous agent did it (including the mistakes to avoid).

---

## 1. What the user wants

The folder `/Users/kt/mathkang` holds a growing collection of past **Math Kangaroo** contest PDFs
(e.g. `2002.pdf`, `2003.pdf`, `2007.pdf`, and any new PDFs the user adds over time). Always start by
listing all `.pdf` files in `/Users/kt/mathkang` (excluding generated `practice_*.pdf` files) so you know
which source papers are available.

The user names problems across any combination of PDFs, e.g. **"2002 - 4, 7, 9  2003 - 9, 12, 14"**.
For each named problem the agent must:

1. Reproduce the **original** problem (retyped, with the figure **redrawn** — never cropped/copied).
2. Write **similar new practice problems**: same idea and skill, same difficulty, different numbers, shapes or story.
3. Produce **two separate PDFs every time**:
   - **Questions worksheet PDF** (e.g. `practice_2002_2003.pdf`) — problems only, **never** include answers here.
   - **Answer key PDF** (e.g. `practice_2002_2003_answers.pdf`) — answer letters + short, kid-friendly explanations.

The first run produced `practice_2002_2003.pdf` (8 pages, 24 problems) and `practice_2002_2003_answers.pdf`
(2 pages) using `generate_practice.py`. **Use those files as the reference for quality and style.**

---

## 2. Questions to ask the user at the start

First, check `ls *.pdf` in `/Users/kt/mathkang` so you can mention the available source PDFs.
If the user hasn't specified what they want yet, ask these together in one short message (showing the defaults):

1. **Which problems?** File/year and problem numbers (e.g. `2007 - 3, 8, 15  2009 - 4, 11`).
2. **How many new practice problems per original?** (default **3**)
3. **Difficulty of the new problems?** Same as the original (default), a bit easier, or a bit harder / mixed.
4. **Output file names?** (default `practice_<years>.pdf` + `practice_<years>_answers.pdf`). **Never overwrite**
   an existing practice PDF unless the user explicitly asks to.
5. *(Optional)* Include the original problems at the start of each set? (default **yes**)

*(Note: Do **not** ask where the answer key goes — the answer key must **always** be in a separate PDF file.)*

If the user already gave the problem numbers, use all the defaults and start right away without asking.

---

## 3. Environment setup (macOS)

The Mac does **not** have `pdftotext`, `pdflatex` or `pandoc`, and the file-viewer tool **cannot open PDFs
directly**. Use a Python virtualenv with PyMuPDF (to read and render PDFs) and ReportLab (to write PDFs):

```bash
cd /Users/kt/mathkang
python3 -m venv .venv            # skip if .venv already exists
.venv/bin/pip install -q pymupdf reportlab
```

Then run everything with `.venv/bin/python`.

---

## 4. Step-by-step workflow

### Step 1: Extract the text and render the pages to images
For each source PDF requested by the user:
```python
import fitz  # PyMuPDF
d = fitz.open("2007.pdf")
for i, p in enumerate(d):
    print("--- page", i + 1); print(p.get_text())
    p.get_pixmap(dpi=110).save(f"scratch/2007_p{i+1}.png")
```
Save the images in your **artifact scratch directory**, not in the workspace. Then **look at the page
images**: many problems are picture-based, and the text alone is not enough.

### Step 2: Zoom into each figure
Page size is typically 612×792 pt. Image px → pt: `pt = px * 72 / dpi`. Crop and zoom like this:
```python
p.get_pixmap(dpi=400, clip=fitz.Rect(x0, y0, x1, y1)).save("scratch/zoom.png")
```
Zoom until you can count every grid line and cube and read every mark. The previous agent needed to
zoom to get the exact cut lines of a square, the brick size (5×4×4) and the letter-N grid.

### Step 3: Solve each original yourself
Most source PDFs have **no official answer key** attached. Solve each problem carefully, and work out the
logic of any 3D or folding problem step by step (see §7).

### Step 4: Design the new problems
Rules that worked well:
- Same skill as the original, but change the numbers, shapes or story (fruit, names, letters).
- Spread the correct answers over different letters (don't make every answer "B").
- Make the wrong choices believable (common mistakes) and make sure **exactly one** answer is correct.
- The last new problem in a set can have a small twist (e.g. "how many **red** cubes" instead of blue).
- Wording must suit the grade level of the paper.

### Step 5: Write a generator script and build both PDFs
**Don't edit or overwrite `generate_practice.py`.** It reproduces the first run and serves as the shared
helper library. Make a new script (e.g. `generate_2007.py`) that **imports the helpers**:
```python
from generate_practice import *   # Doc, write_answer_key, option_row, fig_* helpers, checkers
OUT = "practice_2007.pdf"
OUT_KEY = "practice_2007_answers.pdf"
```
Write your own `build()` modelled on the one in `generate_practice.py`:
1. Create `d = Doc(OUT)`, draw the title and sets, and call `d.save()`.
2. Call `write_answer_key(OUT_KEY, title, subtitle, key)` to generate the separate answer key PDF.
3. Add new `fig_*` drawing functions when a problem type is new.

### Step 6: Check both PDFs visually
Render every page of **both** output PDFs (`OUT` and `OUT_KEY`) and **look at each one**:
```python
for pdf_name, prefix in [(OUT, "out"), (OUT_KEY, "ans")]:
    d = fitz.open(pdf_name)
    for i, p in enumerate(d):
        p.get_pixmap(dpi=90).save(f"scratch/{prefix}_p{i+1}.png")
```
Check that all text and answer choices are visible, the figures match the questions, nothing is cut off,
the worksheet has **no** answers in it, and the separate answer key is complete and accurate.

### Step 7: Report to the user
Give clickable links to **both** the worksheet PDF and the answer key PDF, a short table (set / original /
new problems), the answers you worked out for the originals, and offer next steps.

---

## 5. How `generate_practice.py` works

**Layout (`Doc` class & `write_answer_key`)**
- `Doc(path)`: a US-Letter canvas with a page-number footer.
- `d.heading(title, subtitle)`: a section header with a horizontal line.
- `d.problem(label, html_text, fig=None, fig_pos="right"|"below", choices=None, choice_cols=5)`
  - `fig` is a tuple `(width, height, drawfn(canvas, x, y_bottom))`.
  - `choices` is a list of 5 strings or numbers, shown as `A) … E)`. Use `choice_cols=3` for long choices.
  - It adds a page break automatically when the problem doesn't fit.
- `option_row(items)`: draws picture choices in a row labelled A)–E).
- `vstack(figs)` / `hstack(figs)`: put figures in a column or a row.
- `write_answer_key(path, title, subtitle, key)`: writes the `(label, letter, explanation)` list into a
  standalone answer-key PDF.

**Figure helpers and checkers that already exist**

| Problem type | Helpers | Automatic check |
|---|---|---|
| Square cut into pieces / "which shape is not a piece" | `fig_partition(grid)`, `fig_poly(cells)`, `cut_problem(grid, options, answer_idx)` | `check_cut` compares shapes, allowing rotations and flips |
| Skyline / "which piece cannot belong" | `fig_tokens(tokens, scale)`, `skyline_problem(sky, pieces, scale)` | none (check by hand) |
| Balance scale | `fig_balance(left_radii, right_radii, tilt)` (radius < 6 = small white fruit, 6–8 = gray, ≥ 8 = dark big) | none |
| Brick of cubes | `fig_brick(W, H, D)` | none (interior = (W−2)(H−2)(D−2)) |
| House net / "which house" | `fig_net(net)`, `fig_house(opt)`, `house_problem(net, opts, answer_idx)` | `check_house` |
| Letter area on a grid | `fig_letter(gw, gh, polygons)`, `letter_area()` (shoelace formula) | `assert letter_area(...) == expected` |

**Data formats**
- **Partition grid:** a list of strings, one letter per piece, e.g. `["AABD","ABBD","CCBF","EFFF"]`.
  Option shapes are lists of `(row, col)` cells.
- **Skyline tokens:** `("H", dx)` flat line, `("V", dy)` vertical line (+ is up), `("D", dx, dy)` diagonal,
  `("A", w)` arch. Pieces are short token lists (you can shorten a first/last segment). The odd-one-out piece
  must be a sequence that never appears in the skyline. **Check this by hand.**
- **House net:** `{"F": mark, "K": mark, "L": mark, "R": mark}` with marks `None | "door" | "dot" | "win"`.
  F = front gable (below the floor), K = back gable (above the floor, the roof is attached to it),
  L / R = the side walls to the left and right of the floor.
- **House option:** `(layout, gable_mark, side_mark)`. `"GL"` = gable face on the left, side face on the right.
  `"SL"` = side face on the left, gable face on the right. **The order is ALWAYS (layout, GABLE, SIDE)**, even for `"SL"`.

**Always add an automatic check when you can.** If you build a new figure type, write a checker that
asserts exactly one correct answer (or assert the computed numeric answer). The checkers caught real
mistakes in the first run.

---

## 6. Mistakes from the first run (don't repeat them)

1. **Answer key must be a separate file:** Never append the answer key to the end of the questions PDF.
   Always output `<name>.pdf` (questions only) and `<name>_answers.pdf` (answer key).
2. **Invisible text:** a drawing function left `setFillColor(colors.white)` active, so the answer choices and
   the next heading came out white. **Every `fig_*` draw function must end with `c.setFillColor(colors.black)`.**
3. **Mixed-up tuple order:** the house options for `"SL"` were first written as (layout, side, gable).
   `check_house` caught it. Keep checks on.
4. **Figures too small:** the house net was too small to read at first (`s=19`, then raised to `s=27`).
   Check the size in the rendered pages.
5. **Watermark:** the source PDFs say **"DO NOT COPY"**. Don't paste cropped images of the originals into
   the output. **Redraw every figure** and retype the text, as the first run did.
6. **Unclear explanations:** answer-key explanations must be short and make sense to a 9-year-old. Re-read them.

---

## 7. Notes on solving the problem types

- **Folding a house (2003 #12):** the net shows the outside faces. Facing the **front gable F** from outside,
  net-**R** is on your **left** and net-**L** on your **right**. Facing the **back gable K**, L is on your left
  and R on your right. A door on a wall touches the floor edge in the net.
- **Brick of cubes:** hidden inside cubes = (W−2)(H−2)(D−2). Outside cubes = total − inside.
- **Slanted parts on a grid:** a slanted strip has area = width × height (the cut-off triangles fit together).
  Check every polygon with the shoelace formula.
- **Balance:** remove the same items from both sides (e.g. 6 oranges + 1 melon = 2 melons → 1 melon = 6 oranges).
- Answers the previous agent worked out (no official key available): 2002 #4 D, #7 C, #9 E;
  2003 #9 A, #12 A, #14 E.

---

## 8. File layout

```
/Users/kt/mathkang/
  2002.pdf, 2003.pdf, 2007.pdf, ...   # source papers (read-only; user adds more over time)
  generate_practice.py                # generator for run #1; also the helper library to import
  practice_2002_2003.pdf              # questions worksheet from run #1
  practice_2002_2003_answers.pdf      # separate answer key from run #1
  AGENT_GUIDE.md                      # this file
  .venv/                              # create if missing (see §3)
```
Put temporary images and test scripts in the agent's scratch/artifact directory, not here.
When you add a new reusable `fig_*` helper, consider adding it to `generate_practice.py` (without changing
its `build()` output) and documenting it in §5 of this guide.
