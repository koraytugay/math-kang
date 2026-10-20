# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2002, Problem #18 - Question Generator."""
import os
import sys
import random
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2002, 18)


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


DOMAINS = [
    {
        "intro": "each own a different pet: a rabbit, a hamster, a turtle, and a canary",
        "items": ["rabbit", "hamster", "turtle", "canary"],
        "pair_group": {"rabbit", "hamster"},
        "pair_desc": "both own furry pets",
        "pair_explain": "the two furry pets (rabbit and hamster)",
        "single_item": "canary",
        "single_desc": "owns a bird",
        "single_explain": "the bird (canary)",
        "neg_tmpl": "{p} does not have the {it}",
        "stmt_tmpl": "{p} has a {it}",
    },
    {
        "intro": "each play a different instrument: a violin, a guitar, drums, and a flute",
        "items": ["violin", "guitar", "drums", "flute"],
        "pair_group": {"violin", "guitar"},
        "pair_desc": "both play stringed instruments",
        "pair_explain": "the two stringed instruments (violin and guitar)",
        "single_item": "drums",
        "single_desc": "plays percussion",
        "single_explain": "percussion (drums)",
        "neg_tmpl": "{p} does not play the {it}",
        "stmt_tmpl": "{p} plays the {it}",
    },
    {
        "intro": "each brought a different snack: an apple, a banana, a cookie, and a pretzel",
        "items": ["apple", "banana", "cookie", "pretzel"],
        "pair_group": {"apple", "banana"},
        "pair_desc": "both brought fruits",
        "pair_explain": "the two fruits (apple and banana)",
        "single_item": "cookie",
        "single_desc": "brought a sweet baked treat",
        "single_explain": "the sweet treat (cookie)",
        "neg_tmpl": "{p} does not like {it}s",
        "stmt_tmpl": "{p} brought the {it}",
    },
    {
        "intro": "each do a different sport: soccer, tennis, swimming, and cycling",
        "items": ["soccer", "tennis", "swimming", "cycling"],
        "pair_group": {"soccer", "tennis"},
        "pair_desc": "both play sports with a ball",
        "pair_explain": "the two ball sports (soccer and tennis)",
        "single_item": "swimming",
        "single_desc": "races in the pool",
        "single_explain": "swimming",
        "neg_tmpl": "{p} does not play {it}",
        "stmt_tmpl": "{p} does {it}",
    },
    {
        "intro": "each wear a different hat: a red cap, a blue cap, a sun visor, and a wool beanie",
        "items": ["red cap", "blue cap", "wool beanie", "sun visor"],
        "pair_group": {"red cap", "blue cap"},
        "pair_desc": "both wear baseball caps",
        "pair_explain": "the two baseball caps (red cap and blue cap)",
        "single_item": "wool beanie",
        "single_desc": "wears a warm winter hat",
        "single_explain": "the wool beanie",
        "neg_tmpl": "{p} does not wear the {it}",
        "stmt_tmpl": "{p} wears the {it}",
    },
]

NAME_QUADS = [
    ["Anna", "Ben", "Clara", "David"],
    ["Eva", "Finn", "Grace", "Henry"],
    ["Leo", "Mia", "Noah", "Olivia"],
    ["Sam", "Tara", "Uma", "Vic"],
    ["Iris", "Jack", "Kate", "Liam"],
    ["Maya", "Nora", "Owen", "Paul"],
]


def _generate_dynamic_logic_problem(rng, domain_idx=0):
    """Procedurally generate a 4-person logic deduction problem with verified unique solution."""
    dom = DOMAINS[domain_idx % len(DOMAINS)]
    people = list(rng.choice(NAME_QUADS))
    items = list(dom["items"])  # [pair0, pair1, single_item, leftover_item]
    pair0, pair1, single_it, leftover_it = items[0], items[1], items[2], items[3]
    pair_group = dom["pair_group"]

    # Shuffle role assignment among the 4 people
    roles = list(people)
    rng.shuffle(roles)
    p_pairA, p_pairB, p_single, p_leftover = roles[0], roles[1], roles[2], roles[3]

    # Pick which of {pair0, pair1} p_pairA avoids
    if rng.random() < 0.5:
        disliked_it, got_A, got_B = pair0, pair1, pair0
    else:
        disliked_it, got_A, got_B = pair1, pair0, pair1

    valid_fn = lambda a, pA=p_pairA, pB=p_pairB, pS=p_single, pg=pair_group, s_it=single_it, dis=disliked_it: (
        a[pA] in pg and a[pB] in pg and a[pS] == s_it and a[pA] != dis
    )

    true_map = {
        p_pairA: got_A,
        p_pairB: got_B,
        p_single: single_it,
        p_leftover: leftover_it,
    }

    ask_not_true = rng.random() < 0.7
    stmt_tmpl = dom["stmt_tmpl"]
    neg_clause = dom["neg_tmpl"].format(p=p_pairA, it=disliked_it)

    if ask_not_true:
        # 4 true statements + 1 false statement
        false_person = rng.choice([p_pairB, p_leftover, p_pairA])
        wrong_it = got_A if false_person == p_pairB else (got_B if false_person == p_leftover else disliked_it)
        cand_pairs = [
            (p_pairA, got_A, True),
            (p_pairB, got_B, True),
            (p_single, single_it, True),
            (p_leftover, leftover_it, True),
            (false_person, wrong_it, False),
        ]
        rng.shuffle(cand_pairs)
        opts = [stmt_tmpl.format(p=p, it=it) for p, it, _ in cand_pairs]
        c_fns = [
            (lambda a, p=p, it=it: a[p] != it)
            for p, it, _ in cand_pairs
        ]
        ans_idx = [i for i, (_, _, is_t) in enumerate(cand_pairs) if not is_t][0]
        q_end = "Which statement is <b>not</b> true?"
        false_stmt = opts[ans_idx]
        expl = (
            f"{p_single} has {dom['single_explain']}. {p_pairA} and {p_pairB} have {dom['pair_explain']}. "
            f"Since {neg_clause}, {p_pairA} has the {got_A} and {p_pairB} has the {got_B}. "
            f"That leaves the {leftover_it} for {p_leftover}. Thus, '{false_stmt}' ({LETTERS[ans_idx]}) is not true."
        )
    else:
        # 1 true statement (about p_leftover or p_pairB) + 4 false statements
        cand_pairs = [
            (p_leftover, leftover_it, True),
            (p_leftover, got_A, False),
            (p_leftover, got_B, False),
            (p_leftover, single_it, False),
            (p_pairA, disliked_it, False),
        ]
        rng.shuffle(cand_pairs)
        opts = [stmt_tmpl.format(p=p, it=it) for p, it, _ in cand_pairs]
        c_fns = [
            (lambda a, p=p, it=it: a[p] == it)
            for p, it, _ in cand_pairs
        ]
        ans_idx = [i for i, (_, _, is_t) in enumerate(cand_pairs) if is_t][0]
        q_end = "Which statement is <b>true</b>?"
        true_stmt = opts[ans_idx]
        expl = (
            f"{p_pairA} and {p_pairB} have {dom['pair_explain']}. Since {neg_clause}, {p_pairA} has the {got_A} "
            f"and {p_pairB} has the {got_B}. {p_single} has {dom['single_explain']}, which leaves the {leftover_it} "
            f"for {p_leftover}. Therefore, '{true_stmt}' ({LETTERS[ans_idx]}) is true."
        )

    text = (
        f"{people[0]}, {people[1]}, {people[2]}, and {people[3]} {dom['intro']}. "
        f"{p_pairA} and {p_pairB} {dom['pair_desc']}, {p_single} {dom['single_desc']}, and {neg_clause}. "
        f"{q_end}"
    )
    check_logic_matching(people, items, valid_fn, c_fns, ans_idx)
    return people, items, valid_fn, c_fns, opts, ans_idx, text, expl


def q_2002_18(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Logic Deduction: Matching Pets & Items", "Based on 2002, Problem 18")

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
            lambda a: a["Fabienne"] != "dog",
            lambda a: a["Nicolas"] != "parrot",
            lambda a: a["Julien"] != "goldfish",
            lambda a: a["Fabienne"] != "cat",
            lambda a: a["Manon"] != "dog",
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

    rng = random.Random(seed)
    dom_order = list(range(len(DOMAINS)))
    rng.shuffle(dom_order)
    for idx in range(1, num_practice + 1):
        p_list, it_list, v_fn, c_fns, opts, ans_idx, text, expl = _generate_dynamic_logic_problem(
            rng, domain_idx=dom_order[(idx - 1) % len(dom_order)]
        )
        check_logic_matching(p_list, it_list, v_fn, c_fns, ans_idx)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            choices=opts,
            choice_cols=3,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2002_18

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
