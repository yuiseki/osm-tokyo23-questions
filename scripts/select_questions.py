#!/usr/bin/env python3
"""Choose five questions per type, out of everything the rules allow.

The two checks in ADR 0007 say which fillings are possible and which have an
answer. Neither chooses. This does, and what it optimises for is spread: a
type whose five questions all name Shibuya Station teaches nothing that one
of them would not.

It writes a file to read, not the dataset. Nothing under data/ is touched.

    python3 scripts/select_questions.py --out tmp/checks/selected.md
"""
import argparse
import collections
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import count_combinations as cc
import check_nonzero as cz

# What the questions were checked against. Recorded in each question, because
# "this has an answer" is only true of some particular data.
CHECKED = ("tokyo23-260831.osm.pbf "
           "md5 44a4ba2182379c147f20a27ad1b513ef, "
           "osm_base 2026-08-30T23:50:59Z")

BASE = cc.BASE
WANTED = 5
# Out of coverage on purpose. tokyo_0040 asks about Sapporo already and one
# is enough; every filling using it is empty by construction, which would
# crowd out the questions that are empty for a reason worth knowing.
EXCLUDE_PLACES = {"Sapporo Station"}


def existing():
    """Every question already in the set, so a new one is new.

    Both directories, not just the originals. This used to read only
    data/originals/, which was right when data/questions/ was rewritten from
    scratch on every run and could not contain anything to collide with. It is
    appended to now, so a filling already sitting there has to be excluded or
    the same question is written twice under two numbers.
    """
    out = set()
    for rel in ("data/originals/tokyo", "data/questions/tokyo"):
        base = os.path.join(BASE, rel)
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d)
            t = os.path.join(p, "_template")
            if not os.path.exists(t):
                continue
            tpl = open(t).read().strip()
            vals = {}
            for slot in re.findall(r"\{(\w+)\}", tpl):
                f = os.path.join(p, slot)
                if not os.path.exists(f):
                    break
                vals[slot] = open(f).read().strip()
            else:
                out.add((tpl, tuple(sorted(vals.items()))))
    return out


def spread_pick(rows, wanted, rng):
    """Take questions that repeat each other's values as little as possible.

    Greedy: at each step take the candidate whose values are least used so
    far. It is not optimal and does not need to be; the point is that five
    questions of a type do not all name the same station.
    """
    used = collections.Counter()
    chosen = []
    pool = list(rows)
    rng.shuffle(pool)
    while pool and len(chosen) < wanted:
        best = min(pool, key=lambda r: (sum(used[v] for v in r["values"].values()),
                                        r["order"]))
        pool.remove(best)
        for v in best["values"].values():
            used[v] += 1
        chosen.append(best)
    return chosen


def write_questions(types, picked):
    """One directory per question, the same shape as data/originals/.

    Kept apart from the originals because the prose came about differently:
    there a person wrote the sentence, here a person wrote the template and
    the values and this filled one into the other. No answer is written. That
    a question has one is why it is here, not something the set records.
    """
    root = os.path.join(BASE, "data/questions/tokyo")
    os.makedirs(root, exist_ok=True)
    # Append. This used to delete every directory here and number the new set
    # from 0001, which was harmless while nothing outside referred to a
    # number. Both this set and the answers computed from it are published
    # now, and filled/tokyo/0001 names a particular question to anyone who
    # has it, so the numbers do not move. ADR 0006 wanted one sequence and
    # this is what continuing it means.
    n = max((int(d) for d in os.listdir(root) if d.isdigit()), default=0)
    first = n + 1
    for typ in types:
        for r in picked[typ]:
            n += 1
            d = os.path.join(root, f"{n:04d}")
            os.makedirs(d)
            write = lambda name, text: open(os.path.join(d, name), "w").write(
                text + "\n")
            write("_question", cz.fill(r["text"], r["values"]))
            write("_template", r["text"])
            write("type", typ)
            write("_source", "\n".join([
                "source=filled from a template and the seeds",
                f"template=type_{typ}/{r['num']}.txt",
                f"checked={CHECKED}"]))
            for slot, value in sorted(r["values"].items()):
                write(slot, value)
    print(f"wrote {n - first + 1} questions as {first:04d}..{n:04d} "
          f"under {root}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "tmp/checks/selected.md"))
    ap.add_argument("--per-template", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--write", action="store_true",
                    help="write the chosen questions under data/questions/")
    a = ap.parse_args()

    s = cc.seeds()
    rng = random.Random(a.seed)
    already = existing()
    pool = cz.candidates(s, a.per_template, rng)

    by_type = collections.defaultdict(list)
    for order, (typ, num, text, values) in enumerate(pool):
        if any(v in EXCLUDE_PLACES for v in values.values()):
            continue
        if (text, tuple(sorted(values.items()))) in already:
            continue
        by_type[typ].append({"num": num, "text": text, "values": values,
                             "order": order})

    picked_by_type = {}
    lines = ["# Five questions per type, chosen from what the rules allow",
             "",
             "Not the dataset. A file to read before anything is written.", ""]
    short = []
    for typ in sorted(by_type):
        rows = by_type[typ]
        keep = []
        for r in rows:
            attrs = {sl: s[cc.kind_of(sl)][v] for sl, v in r["values"].items()}
            try:
                if typ in cz.SENSITIVE:
                    c1, c2 = cz.sensitivity_counts(typ, r["values"], attrs, s)
                    if c1 == c2:
                        continue
                    r["note"] = f"{c1} then {c2}"
                elif typ in cz.BOTH_WAYS:
                    q = cz.query_for(typ, r["text"], r["values"], s)
                    r["note"] = "yes" if cz.ask(q) else "no"
                elif typ in ("containment_rank", "neighbour_count_rank"):
                    if not cz.rank_ok(typ, r["values"], attrs, s):
                        continue
                elif typ not in cz.TRIVIAL:
                    q = cz.query_for(typ, r["text"], r["values"], s)
                    if not cz.ask(q):
                        continue
            except Exception as e:
                print(f"  fail {typ}: {e}", file=sys.stderr)
                continue
            keep.append(r)
            if len(keep) >= 60:
                break
        if typ in cz.BOTH_WAYS:
            yes = [r for r in keep if r["note"] == "yes"]
            no = [r for r in keep if r["note"] == "no"]
            chosen = (spread_pick(yes, 3, rng) + spread_pick(no, 2, rng))
        else:
            chosen = spread_pick(keep, WANTED, rng)
        picked_by_type[typ] = chosen
        lines.append(f"## {typ}  ({len(chosen)} of {len(keep)} checked)")
        lines.append("")
        for r in chosen:
            q = cz.fill(r["text"], r["values"])
            note = f"  _{r['note']}_" if r.get("note") else ""
            lines.append(f"- {q}{note}")
        lines.append("")
        if len(chosen) < WANTED:
            short.append(f"{typ}: {len(chosen)}")
    if a.write:
        write_questions(sorted(by_type), picked_by_type)

    if short:
        lines += ["## Short of five", ""] + [f"- {x}" for x in short] + [""]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
