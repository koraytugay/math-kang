# Implemented Questions Index

This file tracks all Math Kangaroo contest questions that have a dedicated, custom-written implementation (`q_<year>_<num>`) in `generate_practice.py`.

> **Note for Agents:** Whenever you implement a new question `q_<year>_<num>` in `generate_practice.py`, you **must** update both the Quick Summary and the Year Tables in this file (`QUESTIONS_INDEX.md`).

---

## Quick Summary by Year

| Year | Implemented Question Numbers | Count | Remaining (out of 1–24) |
|---|---|---|---|
| **2002** | `1`, `4`, `6`, `7`, `9`, `10`, `11`, `12`, `15`, `18`, `20`, `21`, `22`, `24` | 14 / 24 | `2, 3, 5, 8, 13, 14, 16, 17, 19, 23` |
| **2003** | `9`, `10`, `12`, `14`, `16`, `17`, `18` | 7 / 24 | `1, 2, 3, 4, 5, 6, 7, 8, 11, 13, 15, 19, 20, 21, 22, 23, 24` |
| **2007** | `1`, `3`, `4`, `8`, `10`, `12`, `14`, `17`, `21`, `23`, `24` | 11 / 24 | `2, 5, 6, 7, 9, 11, 13, 15, 16, 18, 19, 20, 22` |

**Total Implemented Questions:** 32

---

## Detailed Index by Year

### 2002 (Grades 3–4)

| Question | CLI ID | Function in `generate_practice.py` | Practice Variations | Topic & Visual Description |
|---|---|---|---|---|
| **2002 #1** | `2002:1` | `q_2002_1` | 3 | **Missing Puzzle Tile** — Finding the missing square tile from a grid drawing |
| **2002 #4** | `2002:4` | `q_2002_4` | 3 | **Cutting a Square into Polyominoes** — Identifying which piece was not obtained |
| **2002 #6** | `2002:6` | `q_2002_6` | 3 | **Square & Rectangle Perimeters** — Comparing perimeter of square $ABCD$ and rectangle $AMTD$ |
| **2002 #7** | `2002:7` | `q_2002_7` | 3 | **Castle Skyline Contour** — Matching contour segments to a castle silhouette |
| **2002 #9** | `2002:9` | `q_2002_9` | 3 | **Two-Pan Balance Scale** — Finding the weight of one fruit from tilted/balanced scales |
| **2002 #10** | `2002:10` | `q_2002_10` | 5 | **Digit Occurrences** — Counting how many times a digit occurs in sequential house/page numbers |
| **2002 #11** | `2002:11` | `q_2002_11` | 5 | **Cracked Clock Face** — Partitioning clock face `1–12` (sum = 78) into pieces with consecutive/target sums |
| **2002 #12** | `2002:12` | `q_2002_12` | 5 | **Kangaroo Zigzag Run** — Comparing total grid-segment path lengths of 3 runners on a dashed grid |
| **2002 #15** | `2002:15` | `q_2002_15` | 4 | **Flag Silhouette in the Wind** — Identifying which flag silhouette is impossible unless torn from the pole |
| **2002 #18** | `2002:18` | `q_2002_18` | 4 | **Pet & Item Logic Deduction** — 1-to-1 matching of 4 people and 4 pets/items from logical clues |
| **2002 #20** | `2002:20` | `q_2002_20` | 4 | **3D Cube Tunnel to Pyramid** — Counting unit cubes in a 3D tunnel vs. a stepped pyramid |
| **2002 #21** | `2002:21` | `q_2002_21` | 4 | **Three Digit Cards & Four Operations** — Determining who cannot reach a target number using 3 cards once |
| **2002 #22** | `2002:22` | `q_2002_22` | 4 | **Seating Permutations with Fixed Spots** — Counting seating arrangements when some seats are fixed |
| **2002 #24** | `2002:24` | `q_2002_24` | 4 | **Odometer with Distinct Digits** — Finding distance until all digits on an odometer are distinct again |

---

### 2003 (Grades 3–4)

| Question | CLI ID | Function in `generate_practice.py` | Practice Variations | Topic & Visual Description |
|---|---|---|---|---|
| **2003 #9** | `2003:9` | `q_2003_9` | 3 | **3D Brick of Cubes** — Counting red (outer) vs. blue (inner) unit cubes in a $W \times H \times D$ cuboid |
| **2003 #10** | `2003:10` | `q_2003_10` | 4 | **Metric Length Conversion** — Converting and adding lengths in `m`, `dm`, `cm`, and `mm` |
| **2003 #12** | `2003:12` | `q_2003_12` | 3 | **Folding a 3D House Net** — Matching a 2D paper net of a house with windows/doors to 3D views A–E |
| **2003 #14** | `2003:14` | `q_2003_14` | 3 | **Area of Block Letters on a Grid** — Computing area of polygonal letters (`N`, `Z`, `V`, `M`) on a $1\text{ cm}$ grid |
| **2003 #16** | `2003:16` | `q_2003_16` | 4 | **Book Page Number Digits** — Finding total pages in a book from the total number of digits used |
| **2003 #17** | `2003:17` | `q_2003_17` | 4 | **Alternating Black & White Barcode** — Counting narrow vs. wide black bars in an alternating barcode |
| **2003 #18** | `2003:18` | `q_2003_18` | 3 | **Covering a Grid Shape with Polyominoes** — Selecting which two pieces cover a target grid region |

---

### 2007 (Grades 3–4)

| Question | CLI ID | Function in `generate_practice.py` | Practice Variations | Topic & Visual Description |
|---|---|---|---|---|
| **2007 #1** | `2007:1` | `q_2007_1` | 3 | **Forking Road Diagram** — Finding which combination of symbols/numbers can be collected along a branching path |
| **2007 #3** | `2007:3` | `q_2007_3` | 4 | **Common Letters in Words** — Counting distinct common letters shared by two words |
| **2007 #4** | `2007:4` | `q_2007_4` | 4 | **Next Number with Same Digit Sum** — Finding the smallest number greater than $N$ with the same digit sum |
| **2007 #8** | `2007:8` | `q_2007_8` | 3 | **Joining Polyominoes to Form a Rectangle** — Finding which piece joins with a given shape to make a solid rectangle |
| **2007 #10** | `2007:10` | `q_2007_10` | 3 | **3×3 Mini-Sudoku (Latin Square)** — Deductions with `1, 2, 3` appearing once per row and column |
| **2007 #12** | `2007:12` | `q_2007_12` | 4 | **Calendar Birthday Offset** — Finding a birthday date given an older/younger age difference in years and days |
| **2007 #14** | `2007:14` | `q_2007_14` | 3 | **3D Cube Aquarium** — Counting $1\text{ dm}$ cubes inside a $3 \times 3 \times 3$ aquarium and how many more fit |
| **2007 #17** | `2007:17` | `q_2007_17` | 4 | **Painted Cube Cut into Unit Cubes** — Counting unit cubes with $k$ painted faces in a painted 3D cube/block |
| **2007 #21** | `2007:21` | `q_2007_21` | 4 | **Growing Pattern of Black & White Grid Cells** — Counting white cells in the next step of a visual grid sequence |
| **2007 #23** | `2007:23` | `q_2007_23` | 4 | **Total Digits Written from 1 to N** — Counting total digits needed to write all whole numbers in a range |
| **2007 #24** | `2007:24` | `q_2007_24` | 4 | **Twice-Folded Square Paper Cut** — Identifying unfolded paper shapes after folding a square twice and snipping a corner |
