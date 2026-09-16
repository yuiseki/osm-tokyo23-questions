#!/usr/bin/env python3
"""One line per question, for handing the set to somewhere that wants a file.

The directories under data/ are the copy people edit and diffs are read in
(ADR 0001). This is the same content in the shape a loader expects, written
from them and never the other way round.

Each file in a question's directory becomes a field. The ones beginning with
an underscore are records rather than slots, and lose the underscore:
`_question` is `question`, `_template` is `template`, `_source` is `source`.
Every other file is a slot and keeps its name, so a row carries `place` and
`radius` where the template asked for them and not otherwise.

    python3 scripts/build_jsonl.py [--out data/questions.jsonl] [--check]
"""
import argparse
import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# Where the questions come from, and what that says about them. "written" is
# a sentence a person wrote; "filled" is a template of theirs with curated
# values put into it (ADR 0008).
COLLECTIONS = [("written", "data/originals/tokyo"),
               ("filled", "data/questions/tokyo")]
RENAME = {"_question": "question", "_template": "template", "_source": "source"}
# `_source` holds one line in the written questions and several key=value
# lines in the filled ones. A loader wants columns, not a block of text, so
# the key=value shape becomes fields of its own.
SOURCE_KEYS = {"source": "source", "template": "template_file",
               "checked": "checked"}
# `_tags` is read by build_tag_hints.py and does not belong in a question.
# Naming the tag is the step this set exists to ask about, and a question
# carrying its own tags would answer it. It lives in data/tag_hints.jsonl,
# joined on id by anyone who wants it.
SKIP = {"_tags"}


def read(path):
    return open(path, encoding="utf-8").read().strip()


def rows():
    for origin, rel in COLLECTIONS:
        root = os.path.join(BASE, rel)
        if not os.path.isdir(root):
            continue
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d)
            row = {"id": f"{origin}/tokyo/{d}", "origin": origin,
                   "region": "tokyo"}
            for f in sorted(os.listdir(p)):
                if f in SKIP:
                    continue
                value = read(os.path.join(p, f))
                if f == "_source" and "=" in value.split("\n")[0]:
                    for line in value.split("\n"):
                        k, _, v = line.partition("=")
                        if k in SOURCE_KEYS:
                            row[SOURCE_KEYS[k]] = v
                    continue
                row[RENAME.get(f, f)] = value
            yield row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "data/questions.jsonl"))
    ap.add_argument("--check", action="store_true",
                    help="compare the file with the directories, write nothing")
    a = ap.parse_args()

    built = list(rows())
    if a.check:
        have = [json.loads(l) for l in open(a.out, encoding="utf-8")]
        if have == built:
            print(f"{a.out} matches the directories, {len(built)} questions")
            return 0
        print(f"{a.out} does not match the directories")
        for i, (x, y) in enumerate(zip(have, built)):
            if x != y:
                print(f"  first difference at line {i + 1}: {x.get('id')}")
                break
        if len(have) != len(built):
            print(f"  {len(have)} lines against {len(built)} questions")
        return 1

    with open(a.out, "w", encoding="utf-8") as f:
        for row in built:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    fields = sorted({k for r in built for k in r})
    print(f"wrote {len(built)} questions to {a.out}")
    print("fields: " + ", ".join(fields))


if __name__ == "__main__":
    raise SystemExit(main())
