#!/usr/bin/env python3
"""Write into each place seed what the resolution found it to be.

The seed file holds what a person says; its contents hold what that names in
the data, so that a generator can decide whether a combination is possible
without asking a server. ADR 0004 left room for exactly this: attributes
belong beside the value, not in a hierarchy above it.

Input is the output of scripts/resolve_places.py.

    python3 scripts/write_place_attributes.py [--check tmp/checks/places.json]
"""
import argparse
import collections
import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# The tag that says what kind of thing it is, most specific first. Written as
# a single line so that a seed with several candidates that disagree is
# visible rather than averaged away.
KIND_KEYS = ["railway", "amenity", "leisure", "landuse", "tourism", "shop",
             "office", "historic", "building", "highway"]
# Lines a person wrote, which a resolution run must not overwrite. "name:en"
# is how the data spells a value that a person spells differently, the way
# "Shibuya Ward" is tagged "Shibuya"; "note" is why a value resolves to
# nothing on purpose.
HAND_KEYS = ("name:en", "note")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", default=os.path.join(BASE, "tmp/checks/places.json"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    found = json.load(open(a.check))

    for value in sorted(os.listdir(os.path.join(BASE, "data/seeds/place"))):
        r = found.get(value)
        if r is None:
            print(f"{value:34s} not resolved, left alone")
            continue
        lines = [f"features={r['n']}", f"match={r['match']}"]
        elements = r["elements"]
        if elements:
            kinds = sorted({e["kind"] for e in elements if e.get("kind")})
            if kinds:
                lines = [f"kind={','.join(kinds)}"] + lines
            types = sorted({e["type"] for e in elements})
            lines.append("element=" + ",".join(types))
            ops = sorted({e["operator:en"] for e in elements if e["operator:en"]})
            if ops:
                lines.append("operators=" + "; ".join(ops))
            lines.append("osm=" + " ".join(
                f"{e['type']}/{e['id']}" for e in elements[:12]))
        path = os.path.join(BASE, "data/seeds/place", value)
        if os.path.exists(path):
            kept = [l.rstrip("\n") for l in open(path)
                    if l.partition("=")[0] in HAND_KEYS]
            lines = kept + lines
        text = "\n".join(lines) + "\n"
        print(f"{value:34s} {r['match']:8s} {r['n']:3d}")
        if not a.dry_run:
            open(path, "w").write(text)


if __name__ == "__main__":
    main()
