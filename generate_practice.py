"""Generate Math Kangaroo practice sets and exams by loading per-question generators from question-generator/.

Usage:
  python generate_practice.py --random-exam 20
  python generate_practice.py --questions 2003:10 2007:5 --no-include-orig --num-practice 4
Requires: reportlab
"""
import os
import re
import sys
import math
import inspect
import argparse
import importlib.util

GEN_MODULE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question-generator")
if GEN_MODULE_DIR not in sys.path:
    sys.path.insert(0, GEN_MODULE_DIR)

from common import (
    GEN_DIR,
    OUT,
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
    NUM_WORDS,
    BODY,
    get_timestamp_filename,
    ensure_gen_path,
    Doc,
    option_row,
    hstack,
    vstack,
    append_answer_key,
    write_answer_key,
    _ProblemCollector,
    colors,
)

# Registry of dedicated per-question implementations loaded from question-generator/<year>-<num>.py
QUESTIONS = {}
QUESTION_MODELS = {}
QUESTION_MODULES = {}


def load_question_generators(gen_dir=GEN_MODULE_DIR):
    """Discover and load all question-generator/<year>-<num>.py modules."""
    pattern = re.compile(r"^(\d{4})-(\d+)\.py$")
    if not os.path.isdir(gen_dir):
        return
    for fname in sorted(os.listdir(gen_dir)):
        m = pattern.match(fname)
        if not m:
            continue
        year, num = int(m.group(1)), int(m.group(2))
        q_id = (year, num)
        fpath = os.path.join(gen_dir, fname)
        mod_name = f"qgen_{year}_{num}"
        spec = importlib.util.spec_from_file_location(mod_name, fpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        model_name = getattr(mod, "MODEL", None)
        assert isinstance(model_name, str) and model_name.strip(), (
            f"Generator file {fname} MUST define a non-empty MODEL string (e.g. MODEL = 'argon')."
        )
        fn = getattr(mod, "GENERATE", None) or getattr(mod, f"q_{year}_{num}", None)
        assert callable(fn), f"Generator file {fname} MUST define q_{year}_{num} / GENERATE."

        QUESTIONS[q_id] = fn
        QUESTION_MODELS[q_id] = model_name.strip()
        QUESTION_MODULES[q_id] = mod
        globals()[f"q_{year}_{num}"] = fn


load_question_generators()


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

    if out_pdf is None:
        out_pdf = get_timestamp_filename()

    pool = parse_question_pool(pool_path)
    missing = [q for q in pool if q not in QUESTIONS]
    if missing:
        raise NotImplementedError(
            f"Questions {missing} in {pool_path} do not have dedicated generator files in question-generator/ yet! "
            "Inspect the source PDF(s) and create question-generator/<year>-<num>.py for each one."
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
            f"Questions {missing} do not have dedicated generator files in question-generator/ yet! "
            "Inspect the source PDF(s) and create question-generator/<year>-<num>.py for each one."
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
