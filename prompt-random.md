Read `AGENT_GUIDE.md` and `question-pool.txt` in `/Users/kt/mathkang` and follow all rules in `AGENT_GUIDE.md`.

Generate a brand-new **20-question practice exam PDF** (with the Answer Key & Explanations on the final page(s)) randomly sampled from the questions listed in `question-pool.txt`.

### Exam Rules & Requirements

1. **Source Pool (`question-pool.txt`):**
   - Parse all `(year, question_number)` entries listed in `question-pool.txt`.
   - Randomly select from this pool to produce **20 exam questions total**:
     - If the pool has 20 or more questions, randomly pick 20 distinct `(year, number)` questions (1 similar problem per picked question).
     - If the pool has fewer than 20 questions, distribute the 20 exam questions randomly across the pool (e.g., picking all pool questions and sampling additional distinct practice variations so all 20 exam questions are unique).
2. **Similar Questions Only — Never the Originals:**
   - **Never include the original contest questions** on the exam (`include_orig=False`).
   - Every question on the exam must be a custom-crafted **similar** problem with fresh numbers, stories, or diagram variations, while preserving the exact mathematical/visual concept and difficulty of the source question.
   - Each exam run should produce fresh variations (do not just repeat identical static numbers if a question is picked again across exams).
3. **Implement Any Missing Pool Questions Properly in `question-generator/`:**
   - Check `QUESTIONS_INDEX.md` and `question-generator/` for every selected `(year, number)` question.
   - For any question that does not yet have a dedicated `question-generator/<year>-<num>.py` file:
     - Extract text and render high-DPI crops from `<year>.pdf` into your scratch directory and visually inspect the original question.
     - Solve the original problem and create a dedicated generator file `question-generator/<year>-<num>.py` with `# Model: <model-name>`, `MODEL = "<model-name>"`, bespoke ReportLab figures, and **exact** programmatic solver assertions (`assert` that only one choice `A`–`E` is valid).
     - **Never use weak proxy assertions** (such as checking only square counts instead of actual 2D geometric polyomino tiling). The solver must operate directly on the figure's geometric/combinatorial data structures and verify that the correct choice geometrically/logically works and no other choice works.
     - Update `QUESTIONS_INDEX.md` and `AGENT_GUIDE.md` with the newly implemented question generator and model name.
4. **Output Format & Verification:**
   - Save the generated exam PDF to `generated/YYYY-MM-DD-HH-MM-SS.pdf` using the current timestamp (never overwrite previous PDFs in `generated/`).
   - Number the exam questions cleanly from **1 to 20** (you may note the source inspiration in the subtitle or answer key, e.g., inspired by `2002 #11`).
   - Place the **Answer Key & Kid-Friendly Explanations on the final page(s)** of the same PDF (starting on a fresh new page at the end; never create a separate answer key file).
   - Render all pages of the generated PDF to PNGs in your scratch directory and visually inspect every page to verify figure layout, colors, and text.
   - Commit and push all updated/created files (`generate_practice.py`, `QUESTIONS_INDEX.md`, `AGENT_GUIDE.md`, and the new `generated/*.pdf`).
