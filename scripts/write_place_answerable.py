#!/usr/bin/env python3
"""Which attribute questions each place can answer at all.

"How many storeys does X have?" has no answer unless X carries
building:levels. The tag is a fact about the feature, so it belongs beside
the value like the rest, and then the generator never builds a question whose
answer is missing.

The osm ids already in the seed files are the input, so this is one query.

    python3 scripts/write_place_answerable.py [--dry-run]
"""
import argparse
import json
import os
import urllib.parse
import urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EP = os.environ.get("OVERPASS_URL", "https://overpass.yuiseki.net/api/interpreter")
UA = "osm-tokyo23-questions/0.1 (attribute check)"

# The keys the attribute_lookup templates ask about, in template order.
KEYS = ["building:levels", "start_date", "internet_access", "opening_hours"]


def ask(query):
    body = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(EP, body, {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["elements"]


def read(path):
    attrs = {}
    for line in open(path):
        line = line.strip()
        if "=" in line:
            k, _, v = line.partition("=")
            attrs.setdefault(k, v)
    return attrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = os.path.join(BASE, "data/seeds/place")
    refs = {}
    for value in sorted(os.listdir(root)):
        attrs = read(os.path.join(root, value))
        ids = attrs.get("osm", "").split()
        if ids:
            refs[value] = ids

    wanted = sorted({i for ids in refs.values() for i in ids})
    parts = []
    for ref in wanted:
        t, _, i = ref.partition("/")
        parts.append(f"{t}({i});")
    els = ask("[out:json][timeout:180];(" + "".join(parts) + ");out tags;")
    tags = {f"{e['type']}/{e['id']}": e.get("tags", {}) for e in els}

    for value, ids in refs.items():
        have = []
        for k in KEYS:
            if any(k in tags.get(i, {}) for i in ids):
                have.append(k)
        path = os.path.join(root, value)
        lines = [l.rstrip("\n") for l in open(path)]
        lines = [l for l in lines if not l.startswith("attributes=")]
        if have:
            lines.insert(len(lines) - 1, "attributes=" + ",".join(have))
        print(f"{value:34s} {','.join(have) or '-'}")
        if not a.dry_run:
            open(path, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
