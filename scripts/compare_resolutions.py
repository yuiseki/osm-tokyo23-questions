#!/usr/bin/env python3
"""What changed between two resolution runs.

The seeds were first resolved against overpass.yuiseki.net, whose data is
stamped 2025-09-14. They are resolved again against the 2026-08-31 extract.
The difference is a year of OpenStreetMap, and it says which seed attributes
were wrong and which questions may have changed answer.

    python3 scripts/compare_resolutions.py OLD.json NEW.json
"""
import json
import sys


def main():
    old = json.load(open(sys.argv[1]))
    new = json.load(open(sys.argv[2]))
    names = sorted(set(old) | set(new))
    changed = 0
    for n in names:
        o, w = old.get(n), new.get(n)
        if o is None:
            print(f"{n:34s} only in new: {w['match']} {w['n']}")
            changed += 1
            continue
        if w is None:
            print(f"{n:34s} only in old: {o['match']} {o['n']}")
            changed += 1
            continue
        oi = {f"{e['type']}/{e['id']}" for e in o["elements"]}
        wi = {f"{e['type']}/{e['id']}" for e in w["elements"]}
        oo = {e["operator:en"] for e in o["elements"] if e["operator:en"]}
        wo = {e["operator:en"] for e in w["elements"] if e["operator:en"]}
        if oi == wi and oo == wo and o["match"] == w["match"]:
            continue
        changed += 1
        print(f"{n}")
        if o["match"] != w["match"]:
            print(f"    match   {o['match']} -> {w['match']}")
        if o["n"] != w["n"]:
            print(f"    count   {o['n']} -> {w['n']}")
        for i in sorted(oi - wi):
            print(f"    gone    {i}")
        for i in sorted(wi - oi):
            print(f"    new     {i}")
        for x in sorted(oo - wo):
            print(f"    lost op {x}")
        for x in sorted(wo - oo):
            print(f"    new op  {x}")
    print(f"\n{changed} of {len(names)} places differ")


main()
