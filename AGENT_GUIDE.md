# Agent Guide: Math Kangaroo Practice-PDF Workflow

Read this entire file before doing anything.

---

## Core Rule: Every Question Gets Its Own Dedicated File in `question-generator/`

Math Kangaroo problems are unique. **We do NOT use generic question generators.**
Every single contest problem (`<year> #<number>`) must have **its own dedicated, self-contained Python generator file** in `question-generator/<year>-<number>.py` (for example, `question-generator/2003-10.py`), implemented from scratch the first time the user requests it.

- **Mandatory Model Attribution Rule:**
  Every generator file `question-generator/<year>-<number>.py` **must** declare which AI model was used to generate or update that generator, both as a top comment (`# Model: <model-name>`) and as a module-level constant (`MODEL = "<model-name>"`, e.g. `MODEL = "argon"`).
  - `generate_practice.py` programmatically asserts that every loaded generator file defines a non-empty `MODEL` string.
  - **Why this matters:** Stronger models are used to create, review, and mathematically verify the generator files in `question-generator/`, while lighter/faster models can later generate practice worksheets and random exams simply by running those verified generators without rewriting them.
- Each `question-generator/<year>-<number>.py` file is responsible for:
  1. Declaring `# Model: <model-name>`, `MODEL = "<model-name>"`, `QUESTION_ID = (<year>, <number>)`, and `GENERATE = q_<year>_<number>`.
  2. Redrawing that specific question's exact visual/diagram (if any) using custom ReportLab code tailored to that problem.
  3. Verifying the math/logic/geometry with an exact programmatic assertion/solver specific to that problem.
  4. Rendering the original problem and the requested number of custom-crafted similar practice problems.
- **Never** try to force-fit a new question into another question's file or a generic template.
  When the user asks for `2007 - 5`, you must inspect Question 5 of `2007.pdf` and create a brand-new,
  bespoke generator file `question-generator/2007-5.py` specifically for `2007 #5`.

---

## 1. What the user wants

The folder `/Users/kt/mathkang` holds past **Math Kangaroo** contest PDFs (`2002.pdf`, `2003.pdf`, `2007.pdf`,
and any new PDFs the user adds over time).

When the user specifies questions (via `PROMPT_TEMPLATE.md`, via `prompt-random.md` + `question-pool.txt`, or directly in chat, e.g.
`2002: 4, 7, 9` and `2003: 9, 12, 14`), you must:

1. Check `QUESTIONS_INDEX.md` and the `question-generator/` directory to see which of the requested `(year, number)` questions already have a dedicated `question-generator/<year>-<number>.py` file, and which ones are **new (not yet implemented)**.
2. For every **new** question:
   - Extract the text and render a high-DPI crop of that specific question from `<year>.pdf`.
   - Visually inspect the image carefully (count every grid line, cube, shape, etc.) and solve the original problem.
   - Create a **brand-new dedicated generator file `question-generator/<year>-<number>.py`** with `# Model: <model-name>`, `MODEL = "<model-name>"`, `QUESTION_ID = (<year>, <number>)`, bespoke drawing and exact answer-checking helper functions, and `q_<year>_<number>(d, key, set_num, include_orig=True, num_practice=...)` (`GENERATE = q_<year>_<number>`).
   - **Update `QUESTIONS_INDEX.md` and `AGENT_GUIDE.md`** so the new question generator file and its `MODEL` are listed in the index and guide.
3. Generate **a brand-new worksheet PDF for every request in the `generated/` folder**:
   - **Never amend or overwrite existing generated files.** Every time questions are requested, generate a completely new worksheet PDF.
   - **Keep the repository root clean:** All generated worksheet PDFs must be stored inside the `generated/` directory (e.g. `generated/YYYY-MM-DD-HH-MM-SS.pdf`).
   - Name each generated PDF using the current timestamp in the format `generated/YYYY-MM-DD-HH-MM-SS.pdf` (e.g. `generated/2026-10-19-12-14-56.pdf`), unless the user explicitly requested a custom filename.
   - The PDF contains the problems on the initial page(s), followed by the **Answer Key & Explanations on the final page(s)** (always starting on a fresh new page at the very end).
   - Do **NOT** generate a separate answer key file.
4. **Commit and push** all updated/created files (`generate_practice.py`, `QUESTIONS_INDEX.md`, `AGENT_GUIDE.md`, and the new `generated/*.pdf`).

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
- Design the requested number of practice problems (default 3, or 5 when `--num-practice 5` is requested) specifically around this question's exact concept:
  - Keep the exact same mathematical/visual mechanism, changing the numbers, shapes, or story.
  - Spread the correct answers across different letters (`A`–`E`).
  - Make wrong choices plausible and **assert in code** that there is **only one** valid answer.
  - The final practice variation in a set can include a fun small twist (e.g., asking for the complement).

### Step 4: Create a dedicated `question-generator/<year>-<num>.py` file
Create `question-generator/<year>-<num>.py` containing:
- `# Model: <model-name>` at line 1 and `MODEL = "<model-name>"` (e.g., `MODEL = "argon"`).
- `QUESTION_ID = (<year>, <num>)`
- Bespoke figure and exact solver helper functions (`fig_*`, `check_*`)
- `def q_<year>_<num>(d, key, set_num=1, include_orig=True, num_practice=3): ...`
- `GENERATE = q_<year>_<num>`
- A standalone `if __name__ == "__main__":` block so running `.venv/bin/python question-generator/<year>-<num>.py` directly executes and verifies all assertions for that question.

`generate_practice.py` automatically discovers and loads every `question-generator/<year>-<num>.py` file.

What `question-generator/common.py` provides for **page layout only**:
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

### Step 6: Update `QUESTIONS_INDEX.md` and `AGENT_GUIDE.md`, then commit & push
Whenever you implement one or more new questions:
1. Update **`QUESTIONS_INDEX.md`** (both the *Quick Summary by Year* table and the *Detailed Index by Year* table).
2. Update the table in Section 4 of **`AGENT_GUIDE.md`** below.
3. Stage, commit, and push all changes (`generate_practice.py`, `QUESTIONS_INDEX.md`, `AGENT_GUIDE.md`, and the new PDF in `generated/`).

---

## 4. Currently Implemented Question Generators (`question-generator/` & `QUESTIONS_INDEX.md`)

See **`QUESTIONS_INDEX.md`** for the full user-facing index (including quick summary of implemented vs. remaining question numbers per year).

The following 33 question generators are currently implemented in `question-generator/`:

| Question ID | Generator File | Model | Function | Description |
|---|---|---|---|---|
| `(2002, 1)` | `question-generator/2002-1.py` | `argon` (reviewed high effort, dynamic) | `q_2002_1` | Grid puzzle / picture tile — finding the missing square tile |
| `(2002, 4)` | `question-generator/2002-4.py` | `argon` (reviewed high effort, dynamic) | `q_2002_4` | 4×4 / 5×5 square cut along grid lines into polyomino pieces |
| `(2002, 6)` | `question-generator/2002-6.py` | `argon` (reviewed high effort, dynamic) | `q_2002_6` | Square and rectangle perimeters (perimeter difference) |
| `(2002, 7)` | `question-generator/2002-7.py` | `argon` (reviewed high effort, dynamic) | `q_2002_7` | Castle skyline contour — which piece cannot belong |
| `(2002, 9)` | `question-generator/2002-9.py` | `argon` (reviewed high effort, dynamic) | `q_2002_9` | Tilted/level two-pan balance scale with fruits |
| `(2002, 10)` | `question-generator/2002-10.py` | `argon` (reviewed high effort, dynamic) | `q_2002_10` | Digit occurrences in sequential house/page/locker numbers |
| `(2002, 11)` | `question-generator/2002-11.py` | `argon` (reviewed high effort, dynamic) | `q_2002_11` | Cracked clock face (1–12) partitioned into pieces with consecutive/target sums |
| `(2002, 12)` | `question-generator/2002-12.py` | `argon` (reviewed high effort, dynamic) | `q_2002_12` | Kangaroo zigzag run on a dashed grid — comparing path lengths |
| `(2002, 15)` | `question-generator/2002-15.py` | `argon` (reviewed high effort, dynamic) | `q_2002_15` | Rectangular flag silhouette in the wind — which silhouette is torn |
| `(2002, 18)` | `question-generator/2002-18.py` | `argon` (reviewed high effort, dynamic) | `q_2002_18` | Pet/item logic deduction — 1-to-1 matching of 4 people and 4 pets/items |
| `(2002, 20)` | `question-generator/2002-20.py` | `argon` (reviewed high effort, dynamic) | `q_2002_20` | 3D cube tunnel rearranged into a stepped pyramid — counting unused cubes |
| `(2002, 21)` | `question-generator/2002-21.py` | `argon` (reviewed high effort, dynamic) | `q_2002_21` | Three digit cards & four basic operations — reaching a target number |
| `(2002, 22)` | `question-generator/2002-22.py` | `argon` (reviewed high effort, dynamic) | `q_2002_22` | Seating permutations around a table/row with fixed seats |
| `(2002, 24)` | `question-generator/2002-24.py` | `argon` (reviewed high effort, dynamic) | `q_2002_24` | Odometer distance until all digits are distinct again |
| `(2003, 9)` | `question-generator/2003-9.py` | `argon` (reviewed high effort, dynamic) | `q_2003_9` | 3D W×H×D brick of cubes (red outside, blue inside) |
| `(2003, 10)` | `question-generator/2003-10.py` | `argon` (reviewed high effort, dynamic) | `q_2003_10` | Metric length conversion and addition (`m`, `dm`, `cm`, `mm`) |
| `(2003, 12)` | `question-generator/2003-12.py` | `argon` (reviewed high effort, dynamic) | `q_2003_12` | 2D paper net of a house folded into 3D isometric houses A–E |
| `(2003, 14)` | `question-generator/2003-14.py` | `argon` (reviewed high effort, dynamic) | `q_2003_14` | Area of block letters (N, Z, V, M) on a 1 cm square grid |
| `(2003, 16)` | `question-generator/2003-16.py` | `argon` (reviewed high effort, dynamic) | `q_2003_16` | Total pages in a book from total digits used for page numbers |
| `(2003, 17)` | `question-generator/2003-17.py` | `argon` (reviewed high effort, dynamic) | `q_2003_17` | Alternating black and white barcode — wide vs. narrow black bars |
| `(2003, 18)` | `question-generator/2003-18.py` | `argon` (reviewed high effort, dynamic) | `q_2003_18` | Covering an empty shape on a square grid using two polyomino pieces |
| `(2007, 1)` | `question-generator/2007-1.py` | `argon` (reviewed high effort, dynamic) | `q_2007_1` | Forking road diagram — choosing one number/letter per road split |
| `(2007, 3)` | `question-generator/2007-3.py` | `argon` (reviewed high effort, dynamic) | `q_2007_3` | Counting common letters shared by two words |
| `(2007, 4)` | `question-generator/2007-4.py` | `argon` | `q_2007_4` | Next number greater than $N$ with the same sum of digits |
| `(2007, 5)` | `question-generator/2007-5.py` | `argon` | `q_2007_5` | Number chain in the clouds — working backwards through arithmetic steps |
| `(2007, 8)` | `question-generator/2007-8.py` | `argon` | `q_2007_8` | Joining a piece with the given shape to form a solid rectangle |
| `(2007, 10)` | `question-generator/2007-10.py` | `argon` | `q_2007_10` | 3×3 mini-sudoku — placing numbers 1, 2, 3 in rows and columns |
| `(2007, 12)` | `question-generator/2007-12.py` | `argon` | `q_2007_12` | Calendar birthday date calculation given older/younger offset |
| `(2007, 14)` | `question-generator/2007-14.py` | `argon` | `q_2007_14` | 3D cube aquarium (3×3×3) — counting 1 dm cubes inside / missing to fill |
| `(2007, 17)` | `question-generator/2007-17.py` | `argon` | `q_2007_17` | Painted 3D cube cut into unit cubes — counting cubes with $k$ painted faces |
| `(2007, 21)` | `question-generator/2007-21.py` | `argon` | `q_2007_21` | Growing grid pattern of black and white cells — counting white cells |
| `(2007, 23)` | `question-generator/2007-23.py` | `argon` | `q_2007_23` | Total digits needed to write all numbers from $1$ to $N$ |
| `(2007, 24)` | `question-generator/2007-24.py` | `argon` | `q_2007_24` | Square paper folded twice and cut at a corner — unfolded paper design |

**Any other `(year, number)` requested by the user is NEW** — you must inspect the source PDF, create
a new dedicated `question-generator/<year>-<number>.py` file (including `# Model: <model>` and `MODEL = "<model>"`), and add it to both `QUESTIONS_INDEX.md` and the table above!

---

## 5. Hard Lessons from Previous Runs (Do Not Repeat)

1. **Always reset canvas colors:** In ReportLab, setting `c.setFillColor(colors.white)` or light gray stays active until changed.
   Every custom `draw(c, x, y)` function **must** end with `c.setFillColor(colors.black)` and
   `c.setStrokeColor(colors.black)` or subsequent text and problem headers will be drawn in the wrong color or invisible!
2. **Write a true, exact programmatic checker for every question (NEVER use weak proxy checks):**
   - Always write an `assert` / solver function that verifies the full math, combinatorics, and geometry of your question directly on the exact data structures passed to the figure renderer, and confirms that **strictly one** answer choice (`A`–`E`) is valid.
   - **Never write a weak proxy checker!** For example, in a 2D polyomino tiling/covering problem (`2003 #18`, `2007 #8`), checking only that the number of squares sums to the empty area (`5 + 6 == 11`) is a broken proxy check because the 2D shapes might not geometrically fit the region! Your solver must test actual 2D geometric placement (all translations/rotations/flips) directly on the grid matrix and polyomino cell coordinates. Similarly, for skyline/path matching (`2002 #7`), verify subpath matching on the actual token lists; for 3D nets (`2003 #12`, `2007 #24`), verify the 3D/unfolded adjacency directly.
3. **Avoid trivial degeneracies in practice variations:** When designing new numbers for a trick problem (e.g., odometer rollover `2002 #24`), make sure the variation preserves the core reasoning step of the original problem (e.g., requiring a digit rollover rather than a trivial `+1 km` step).
4. **Always record the model name in `question-generator/<year>-<num>.py`:** Every generator file in `question-generator/` must start with `# Model: <model-name>` and define `MODEL = "<model-name>"` (e.g., `MODEL = "argon"`). Never omit `MODEL`.
5. **Check figure scale and layout visually:** Always render output PDF pages to PNGs in `scratch/` and inspect them with `view_file`.
6. **Answer key is ALWAYS on the last page of the PDF:** Never generate a separate answer key PDF file. Always
   append the answer key starting on a fresh new page at the very end of the worksheet PDF.
7. **Always create a new timestamped file in `generated/`:** Never amend or overwrite previous worksheet PDFs. Every time questions are requested,
   generate a fresh PDF inside `generated/` named with the current timestamp `generated/YYYY-MM-DD-HH-MM-SS.pdf` to keep the root clean.
8. **Support `include_orig=False` (`--no-include-orig`) and `--num-practice`:** When the user sets `Include original problems: no`, pass `--no-include-orig`. Every `q_<year>_<num>` method must support `include_orig=True` and omit the contest problem from both the worksheet and the answer key when `include_orig=False`.
9. **Always keep `QUESTIONS_INDEX.md` and `AGENT_GUIDE.md` updated, and commit & push:** Whenever you implement a new question in `question-generator/<year>-<num>.py`, immediately update `QUESTIONS_INDEX.md` and `AGENT_GUIDE.md`, then `git add`, `git commit`, and `git push`.
