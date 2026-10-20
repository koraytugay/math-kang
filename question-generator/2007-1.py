# Model: argon
# Reviewed by argon on high effort (dynamic procedural generator)
"""Math Kangaroo 2007, Problem #1 - Question Generator."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    LETTERS,
    colors,
    _ProblemCollector,
)

MODEL = "argon"
REVIEWED_BY = "argon (high effort)"
DYNAMIC = True
QUESTION_ID = (2007, 1)


def valid_fork_groups(forks):
    """Given a list of forks (e.g. [(1, 2), (3, 4), (5, 6)]), return all valid tuples picking 1 per fork."""
    res = [()]
    for branch in forks:
        res = [prev + (item,) for prev in res for item in branch]
    return set(res)


def check_fork_road(forks, option_tuples, answer_idx, mode="valid"):
    valid = valid_fork_groups(forks)
    if mode == "valid":
        good = [i for i, opt in enumerate(option_tuples) if tuple(opt) in valid]
    else:
        good = [i for i, opt in enumerate(option_tuples) if tuple(opt) not in valid]
    assert good == [answer_idx], (forks, good, answer_idx, mode)


def fig_fork_road(forks):
    """Draw a walker on the left and a sequence of road forks with labels."""
    n = len(forks)
    seg_w = 88
    lead_w = 24
    walker_w = 24
    W = walker_w + lead_w + n * seg_w
    H = 54

    def draw(c, x, y):
        cy = y + H / 2
        c.setLineWidth(1.2)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.black)

        # Draw little walker on the left
        wx = x + 10
        c.circle(wx, cy + 11, 3.2, stroke=1, fill=0)  # head
        c.line(wx, cy + 7.8, wx, cy + 2)               # neck/torso
        c.line(wx - 6, cy + 5, wx + 6, cy + 8)         # arms
        p = c.beginPath()                              # skirt/dress
        p.moveTo(wx, cy + 2)
        p.lineTo(wx - 5, cy - 6)
        p.lineTo(wx + 5, cy - 6)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.line(wx - 2.5, cy - 6, wx - 2.5, cy - 12)    # left leg
        c.line(wx + 2.5, cy - 6, wx + 2.5, cy - 12)    # right leg

        # Road parameters
        rh = 5.5   # half-width of main road
        bh = 13.0  # vertical offset of top/bottom branch centerlines
        rx = x + walker_w

        # Initial straight road segment
        c.line(rx, cy + rh, rx + lead_w, cy + rh)
        c.line(rx, cy - rh, rx + lead_w, cy - rh)
        cx = rx + lead_w

        for branch in forks:
            f_len = 66
            s_len = seg_w - f_len
            mid = cx + f_len / 2
            end = cx + f_len

            for sign in (+1, -1):
                p_out = c.beginPath()
                p_out.moveTo(cx, cy + sign * rh)
                p_out.curveTo(cx + 16, cy + sign * rh, mid - 14, cy + sign * (bh + 4.5), mid, cy + sign * (bh + 4.5))
                p_out.curveTo(mid + 14, cy + sign * (bh + 4.5), end - 16, cy + sign * rh, end, cy + sign * rh)
                c.drawPath(p_out, stroke=1, fill=0)

                p_in = c.beginPath()
                p_in.moveTo(cx + 7, cy)
                p_in.curveTo(cx + 18, cy + sign * 2, mid - 12, cy + sign * (bh - 4.5), mid, cy + sign * (bh - 4.5))
                p_in.curveTo(mid + 12, cy + sign * (bh - 4.5), end - 18, cy + sign * 2, end - 7, cy)
                c.drawPath(p_in, stroke=1, fill=0)

            for idx_b, sign in ((0, +1), (1, -1)):
                ly = cy + sign * bh
                c.setFillColor(colors.white)
                c.rect(mid - 5.5, ly - 5.5, 11, 11, stroke=0, fill=1)
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(mid, ly - 3.5, str(branch[idx_b]))

            c.line(end, cy + rh, end + s_len, cy + rh)
            c.line(end, cy - rh, end + s_len, cy - rh)
            cx = end + s_len

        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)

    return W, H, draw


def _make_invalid_fork_triples(forks):
    """Build plausible invalid triples that pick both labels from one fork and one label from another."""
    (a1, b1), (a2, b2), (a3, b3) = forks
    return [
        (a1, b1, a2),
        (a1, b1, b3),
        (b1, a2, b2),
        (a1, a3, b3),
        (a2, b2, a3),
        (a2, b2, b3),
        (b1, a3, b3),
        (a1, b1, a3),
    ]


NAMES = ["Leo", "Mia", "Sam", "Nora", "Alex", "Clara", "Max", "Elena"]


def _generate_dynamic_fork_problem(rng, mode_idx=0):
    """Procedurally generate a road-fork problem across 4 modes."""
    actor = rng.choice(NAMES)
    m = mode_idx % 4

    if m == 0:
        # Mode 0: 3 forks with randomized numbers -> which group COULD be written?
        nums = rng.sample(range(1, 10), 6)
        forks = [(nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])]
        valid_list = sorted(list(valid_fork_groups(forks)))
        good_triple = rng.choice(valid_list)
        bad_cands = _make_invalid_fork_triples(forks)
        rng.shuffle(bad_cands)
        all_triples = bad_cands[:4] + [good_triple]
        rng.shuffle(all_triples)
        ans_idx = all_triples.index(good_triple)
        check_fork_road(forks, all_triples, ans_idx, mode="valid")
        opts = [f"{a}, {b} and {c}" for a, b, c in all_triples]
        text = (
            f"{actor} walked from the left to the right along the roads and wrote down the three numbers passed. "
            f"Which group of numbers could {actor} have written?"
        )
        expl = (
            f"{actor} must pick one number from {forks[0]}, one from {forks[1]}, and one from {forks[2]}. "
            f"Only ({good_triple[0]}, {good_triple[1]} and {good_triple[2]}) picks one from each fork."
        )
        return forks, opts, 3, ans_idx, text, expl

    elif m == 1:
        # Mode 1: 3 forks with letters -> which three letters COULD be written?
        pool = list("ABCDEFGHKLMNP")
        lets = rng.sample(pool, 6)
        forks = [(lets[0], lets[1]), (lets[2], lets[3]), (lets[4], lets[5])]
        valid_list = sorted(list(valid_fork_groups(forks)))
        good_triple = rng.choice(valid_list)
        bad_cands = _make_invalid_fork_triples(forks)
        rng.shuffle(bad_cands)
        all_triples = bad_cands[:4] + [good_triple]
        rng.shuffle(all_triples)
        ans_idx = all_triples.index(good_triple)
        check_fork_road(forks, all_triples, ans_idx, mode="valid")
        opts = [f"{a}, {b} and {c}" for a, b, c in all_triples]
        text = (
            f"{actor} walked from left to right and wrote down the letters passed along the path. "
            f"Which three letters could {actor} have written?"
        )
        expl = (
            f"{actor} picks one letter from ({forks[0][0]}, {forks[0][1]}), one from ({forks[1][0]}, {forks[1][1]}), "
            f"and one from ({forks[2][0]}, {forks[2][1]}). Only ({good_triple[0]}, {good_triple[1]} and {good_triple[2]}) "
            f"has one letter from each fork."
        )
        return forks, opts, 3, ans_idx, text, expl

    elif m == 2:
        # Mode 2: 3 forks with numbers -> which group CANNOT be written?
        nums = rng.sample(range(1, 10), 6)
        forks = [(nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])]
        valid_list = list(valid_fork_groups(forks))
        rng.shuffle(valid_list)
        bad_triple = rng.choice(_make_invalid_fork_triples(forks))
        all_triples = valid_list[:4] + [bad_triple]
        rng.shuffle(all_triples)
        ans_idx = all_triples.index(bad_triple)
        check_fork_road(forks, all_triples, ans_idx, mode="invalid")
        opts = [f"{a}, {b} and {c}" for a, b, c in all_triples]
        text = (
            f"{actor} walked from left to right along the road and wrote down the three numbers passed. "
            f"Which of the following groups of numbers could <b>not</b> have been written by {actor}?"
        )
        expl = (
            f"At each of the three forks {forks[0]}, {forks[1]}, and {forks[2]}, {actor} can only take one branch. "
            f"Group ({bad_triple[0]}, {bad_triple[1]} and {bad_triple[2]}) takes both branches of the same fork, "
            f"so it is impossible."
        )
        return forks, opts, 3, ans_idx, text, expl

    else:
        # Mode 3: Sum of the 3 numbers passed along the road
        for _ in range(300):
            nums = rng.sample(range(1, 10), 6)
            forks = [(nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])]
            triples = list(valid_fork_groups(forks))
            valid_sums = {a + b + c for a, b, c in triples}
            lo, hi = min(valid_sums), max(valid_sums)
            invalid_sums = [s for s in range(max(3, lo - 2), hi + 3) if s not in valid_sums]
            if len(invalid_sums) >= 4:
                good_triple = rng.choice(triples)
                good_sum = sum(good_triple)
                rng.shuffle(invalid_sums)
                sum_choices = sorted(invalid_sums[:4] + [good_sum])
                ans_idx = sum_choices.index(good_sum)
                assert [i for i, s in enumerate(sum_choices) if s in valid_sums] == [ans_idx]
                text = (
                    f"{actor} walked from left to right and <b>added up</b> the three numbers passed along the road. "
                    f"Which of the following could be {actor}'s total?"
                )
                sums_sorted_str = ", ".join(str(s) for s in sorted(valid_sums))
                expl = (
                    f"The possible sums from picking one number per fork are {{{sums_sorted_str}}}. "
                    f"Among the choices, only {good_sum} is possible (for example, "
                    f"{good_triple[0]} + {good_triple[1]} + {good_triple[2]} = {good_sum})."
                )
                return forks, [str(s) for s in sum_choices], 5, ans_idx, text, expl
        raise RuntimeError("Failed to generate fork sum problem")


def q_2007_1(d, key, set_num=1, include_orig=True, num_practice=3, seed=None):
    d.heading(f"Set {set_num} - Choosing paths along a road", "Based on 2007, Problem 1")

    if include_orig:
        forks = [(1, 2), (3, 4), (5, 6)]
        opts = [(1, 2, 4), (2, 3, 4), (2, 3, 5), (1, 5, 6), (1, 2, 5)]
        check_fork_road(forks, opts, 2, mode="valid")
        d.problem(
            "Original 2007 #1.",
            "Zita walked from the left to the right and wrote the numbers she saw along the roads in her "
            "notepad. Which of the following groups of numbers could be the numbers written by Zita?",
            fig_fork_road(forks),
            "below",
            [f"{a}, {b} and {c}" for a, b, c in opts],
            choice_cols=3,
        )
        key.append((
            "2007 #1",
            "C",
            "At the 1st fork Zita picks 1 or 2; at the 2nd fork 3 or 4; at the 3rd fork 5 or 6. Only (2, 3 and 5) has one from each fork.",
        ))

    rng = random.Random(seed)
    modes = [0, 1, 2, 3]
    rng.shuffle(modes)
    for idx in range(1, num_practice + 1):
        m = modes[(idx - 1) % len(modes)]
        forks, opts, cols, ans_idx, text, expl = _generate_dynamic_fork_problem(rng, mode_idx=m)
        d.problem(
            f"Practice {set_num}.{idx}",
            text,
            fig_fork_road(forks),
            "below",
            opts,
            choice_cols=cols,
        )
        key.append((f"{set_num}.{idx}", LETTERS[ans_idx], expl))


GENERATE = q_2007_1

if __name__ == "__main__":
    for test_seed in range(30):
        collector = _ProblemCollector()
        key = []
        GENERATE(collector, key, set_num=1, include_orig=True, num_practice=5, seed=test_seed)
        assert len(collector.problems) == len(key) == 6
    print(f"Verified {QUESTION_ID} (model={MODEL}, reviewed={REVIEWED_BY}, dynamic={DYNAMIC}) across 30 random seeds!")
