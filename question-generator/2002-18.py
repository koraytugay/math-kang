# Model: argon
"""Math Kangaroo 2002, Problem #18 - Question Generator."""
import os
import sys
import math
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
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
    BODY,
    NUM_WORDS,
    Doc,
    option_row,
    hstack,
    vstack,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
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


def q_2002_18(d, key, set_num=1, include_orig=True, num_practice=3):
    d.heading(f"Set {set_num} - Logic Deduction: Matching Pets & Items", "Based on 2002, Problem 18")

    # Original 2002 #18
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
            lambda a: a["Fabienne"] != "dog",      # A: "Fabienne has a dog" is NOT true
            lambda a: a["Nicolas"] != "parrot",    # B: "Nicolas has a parrot" is NOT true
            lambda a: a["Julien"] != "goldfish",   # C: "Julien has a goldfish" is NOT true
            lambda a: a["Fabienne"] != "cat",      # D: "Fabienne has a cat" is NOT true
            lambda a: a["Manon"] != "dog",         # E: "Manon has a dog" is NOT true
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

    practices = [
        # Practice .1: 4 kids (Anna, Ben, Clara, David), pets (rabbit, hamster, turtle, canary). Answer: C
        (
            ["Anna", "Ben", "Clara", "David"],
            ["rabbit", "hamster", "turtle", "canary"],
            lambda a: (
                a["Ben"] in {"rabbit", "hamster"}
                and a["Clara"] in {"rabbit", "hamster"}
                and a["David"] == "canary"
                and a["Ben"] != "hamster"
            ),
            [
                lambda a: a["Ben"] != "rabbit",
                lambda a: a["David"] != "canary",
                lambda a: a["Clara"] != "rabbit",  # False statement: "Clara has a rabbit"
                lambda a: a["Anna"] != "turtle",
                lambda a: a["Clara"] != "hamster",
            ],
            [
                "Ben has a rabbit",
                "David has a canary",
                "Clara has a rabbit",
                "Anna has a turtle",
                "Clara has a hamster",
            ],
            2,
            "Anna, Ben, Clara, and David each own a different pet: a rabbit, a hamster, a turtle, and a canary. "
            "Ben and Clara both own furry pets, David owns a bird, and Ben does not have the hamster. "
            "Which statement is <b>not</b> true?",
            "David has the bird (canary). The two furry pets are the rabbit and the hamster, belonging to Ben and Clara. "
            "Since Ben does not have the hamster, Ben has the rabbit and Clara has the hamster. "
            "That leaves the turtle for Anna. Thus, 'Clara has a rabbit' (C) is not true.",
        ),
        # Practice .2: 4 friends (Eva, Finn, Grace, Henry), instruments (violin, guitar, flute, drums). Answer: D
        (
            ["Eva", "Finn", "Grace", "Henry"],
            ["violin", "guitar", "flute", "drums"],
            lambda a: (
                a["Eva"] in {"violin", "guitar"}
                and a["Grace"] in {"violin", "guitar"}
                and a["Finn"] == "drums"
                and a["Eva"] != "violin"
            ),
            [
                lambda a: a["Eva"] != "guitar",
                lambda a: a["Finn"] != "drums",
                lambda a: a["Grace"] != "violin",
                lambda a: a["Henry"] != "guitar",  # False statement: "Henry plays the guitar"
                lambda a: a["Henry"] != "flute",
            ],
            [
                "Eva plays the guitar",
                "Finn plays the drums",
                "Grace plays the violin",
                "Henry plays the guitar",
                "Henry plays the flute",
            ],
            3,
            "Eva, Finn, Grace, and Henry each play a different instrument: a violin, a guitar, a flute, and drums. "
            "Eva and Grace play stringed instruments, Finn plays percussion (drums), and Eva does not play the violin. "
            "Which statement is <b>not</b> true?",
            "The stringed instruments are the violin and the guitar. Since Eva does not play the violin, Eva plays the guitar "
            "and Grace plays the violin. Finn plays the drums, leaving the flute for Henry. "
            "Therefore, 'Henry plays the guitar' (D) is not true.",
        ),
        # Practice .3: 4 kids (Leo, Mia, Noah, Olivia), snacks (apple, banana, cookie, pretzel). Ask what Olivia has -> E
        (
            ["Leo", "Mia", "Noah", "Olivia"],
            ["apple", "banana", "cookie", "pretzel"],
            lambda a: (
                a["Leo"] in {"apple", "banana"}
                and a["Mia"] in {"apple", "banana"}
                and a["Noah"] == "cookie"
                and a["Leo"] != "apple"
            ),
            [
                lambda a: a["Olivia"] == "apple",
                lambda a: a["Olivia"] == "banana",
                lambda a: a["Olivia"] == "cookie",
                lambda a: a["Leo"] == "apple",
                lambda a: a["Olivia"] == "pretzel",
            ],
            [
                "Olivia has the apple",
                "Olivia has the banana",
                "Olivia has the cookie",
                "Leo has the apple",
                "Olivia has the pretzel",
            ],
            4,
            "Leo, Mia, Noah, and Olivia each brought a different snack: an apple, a banana, a cookie, and a pretzel. "
            "Leo and Mia brought fruits, Noah brought the cookie, and Leo does not like apples. "
            "Which statement is <b>true</b>?",
            "Leo and Mia have the two fruits (apple and banana). Since Leo does not like apples, Leo has the banana and "
            "Mia has the apple. Noah has the cookie, which leaves the pretzel for Olivia. So statement E is true.",
        ),
        # Practice .4: 4 athletes (Sam, Tara, Uma, Vic), sports (soccer, tennis, swimming, cycling). Answer: B
        (
            ["Sam", "Tara", "Uma", "Vic"],
            ["soccer", "tennis", "swimming", "cycling"],
            lambda a: (
                a["Sam"] in {"soccer", "tennis"}
                and a["Uma"] in {"soccer", "tennis"}
                and a["Tara"] == "swimming"
                and a["Sam"] != "soccer"
            ),
            [
                lambda a: a["Sam"] != "tennis",
                lambda a: a["Uma"] != "tennis",  # False statement: "Uma plays tennis"
                lambda a: a["Tara"] != "swimming",
                lambda a: a["Vic"] != "cycling",
                lambda a: a["Uma"] != "soccer",
            ],
            [
                "Sam plays tennis",
                "Uma plays tennis",
                "Tara does swimming",
                "Vic does cycling",
                "Uma plays soccer",
            ],
            1,
            "Sam, Tara, Uma, and Vic each do a different sport: soccer, tennis, swimming, and cycling. "
            "Sam and Uma play sports with a ball, Tara is in the pool, and Sam does not play soccer. "
            "Which statement is <b>not</b> true?",
            "The two ball sports are soccer and tennis. Since Sam does not play soccer, Sam plays tennis and Uma plays soccer. "
            "Tara does swimming, leaving cycling for Vic. Thus, 'Uma plays tennis' (B) is not true.",
        ),
    ]

    for idx, (p_list, it_list, v_fn, c_fns, opts, ans_idx, text, expl) in enumerate(practices[:num_practice], start=1):
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
    import inspect
    collector = _ProblemCollector()
    key = []
    sig = inspect.signature(GENERATE)
    if "num_practice" in sig.parameters:
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5)
    else:
        GENERATE(collector, key, set_num=1, include_orig=True)
    assert len(collector.problems) == len(key)
    print(f"Verified {QUESTION_ID} (model={MODEL}): {len(collector.problems)} problems generated.")
