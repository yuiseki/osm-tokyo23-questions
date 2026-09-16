#!/usr/bin/env python3
"""data/tag_hints.jsonl: which OSM tags each question turns on.

Not an answer. An answer belongs to a particular extract on a particular day
and this set does not carry one; a tag is what the thing is called in
OpenStreetMap and does not move when the data does. Nor is it new: every tag
here is already in data/seeds, beside the value that names it. This is that
mapping read out per question.

It is a separate file on purpose. Naming the tag is the step language models
actually fail at, and by a margin: asked to write SQL for 1,206 of these
questions with no examples, Qwen2.5-Coder-3B chose the wrong key for a quarter
of the categories it named, and even the 35B missed a fifth. A hint sitting in
the same row as the question would be handed to anything being measured on it.
Joined on `id` when it is wanted, absent when it is not.

Two questions carry no template and no slots, and their tags are written in a
`_tags` file beside them. Both name the tag in the sentence itself, so the
file transcribes rather than decides.

Greedy, because it is a hint and not a specification. The category, the brand
and its class, the operator, the boundary tags of a ward, the kind of thing a
place is, the key an attribute question reads. Some of those are not needed to
answer; none of them is misleading.

    python3 scripts/build_tag_hints.py
    python3 scripts/build_tag_hints.py --check
"""
import argparse
import collections
import json
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(BASE, "data/tag_hints.jsonl")

# Lines in a seed file that describe the value rather than tag the thing.
NOT_A_TAG = {"features", "number", "form", "metres", "note", "match",
             "element", "operators", "osm", "attributes", "kind", "spelling"}

# An attribute question asks for the value of one tag, so the hint is the key
# alone. Naming the value would be answering. Which key belongs to which
# question is in the template, not in the slots.
ATTRIBUTE_KEY = {
    "How many storeys does {place} have?": "building:levels",
    "When was {place} erected?": "start_date",
    "Is the wireless internet at {place} free of charge?":
        "internet_access:fee",
    "What are the opening hours of {place}?": "opening_hours",
}


def seed(kind, value):
    path = os.path.join(BASE, "data/seeds", kind, value)
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


def tags_of(kind, value, keys=None):
    s = seed(kind, value)
    return {f"{k}={v}" for k, v in s.items()
            if k not in NOT_A_TAG and (keys is None or k in keys)}


def hand_written(qid):
    """Tags recorded beside a question that has no template.

    Two of the written questions name their entities inside the sentence and
    have no slots, so nothing can be looked up for them. Both also name their
    tag inside the sentence, in the parenthesis the author added to say which
    park and which cemetery was meant, so the file beside them is a
    transcription rather than a decision.
    """
    origin, region, num = qid.split("/")
    d = "data/originals" if origin == "written" else "data/questions"
    path = os.path.join(BASE, d, region, num, "_tags")
    if not os.path.exists(path):
        return set()
    return {l.strip() for l in open(path, encoding="utf-8")
            if l.strip() and not l.startswith("#")}


def hints(q):
    out = hand_written(q["id"])
    for slot, value in q.items():
        if slot.startswith(("category", "neighbour")):
            out |= tags_of("category", value)
        elif slot.startswith("brand"):
            out |= tags_of("brand", value)
        elif slot == "operator":
            out |= tags_of("operator", value)
        elif slot == "area":
            # The ward's own name too: the value is "Shibuya Ward" and
            # OpenStreetMap tags it "Shibuya", which is the sort of thing a
            # hint is for.
            out |= tags_of("area", value, {"boundary", "admin_level", "name:en"})
        elif slot == "name":
            out |= tags_of("name", value)
        elif slot.startswith(("place", "target")):
            for part in seed("place", value).get("kind", "").split(","):
                if "=" in part:
                    out.add(part.strip())
    key = ATTRIBUTE_KEY.get(q.get("template", ""))
    if key:
        out.add(key)
    return sorted(out)


def render():
    rows = []
    with open(os.path.join(BASE, "data/questions.jsonl"), encoding="utf-8") as f:
        for line in f:
            q = json.loads(line)
            rows.append({"id": q["id"], "osm_tag_hints": hints(q)})
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                   for r in rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = render()
    if a.check:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if have != text:
            print("data/tag_hints.jsonl is not what the questions say")
            return 1
    else:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(text)

    rows = [json.loads(l) for l in text.splitlines()]
    n = collections.Counter(len(r["osm_tag_hints"]) for r in rows)
    tags = collections.Counter(t for r in rows for t in r["osm_tag_hints"])
    print(f"{len(rows)} questions, {len(tags)} distinct tags")
    print("hints per question: "
          + ", ".join(f"{k}:{v}" for k, v in sorted(n.items())))
    none = [r["id"] for r in rows if not r["osm_tag_hints"]]
    if none:
        print(f"no hint: {', '.join(none)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
