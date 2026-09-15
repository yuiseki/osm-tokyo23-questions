#!/usr/bin/env python3
"""Ask Overpass whether a filled question has anything to find.

The tag rules in count_combinations.py say a filling is possible. They cannot
say it is non-empty: nothing in the tags rules out asking for the nearest
nightclub to a cemetery in a district that has none. This asks.

Only the count is asked for, never the answer. The dataset holds no answers
and none is written here; the query exists to decide whether the question is
worth keeping.

    python3 scripts/check_nonzero.py --sample 100
"""
import argparse
import itertools
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import count_combinations as cc

BASE = cc.BASE
EP = os.environ.get("OVERPASS_URL", "https://overpass.yuiseki.net/api/interpreter")
UA = "osm-tokyo23-questions/0.1 (non-empty check)"

# Types whose answer cannot be empty once the values resolve. A distance
# between two features that both exist is a number; an attribute question was
# already restricted to places carrying the tag.
TRIVIAL = {"distance", "bearing", "attribute_lookup", "length_total",
           "area_compare",
           # both are answered by counting what the seeds already record
           "area_rank", "name_count"}
# The one type where an empty answer is a correct answer (ADR 0007). It is
# asked all the same, because a set of five that are all yes is a worse set.
BOTH_WAYS = {"existence"}
# These ask whether the answer changes with the radius, so counting at one
# radius says nothing. Both are counted and they have to differ.
SENSITIVE = {"radius_sensitivity", "radius_sensitivity_compare"}


def ask(query, tries=3):
    if query is None:
        raise ValueError("no query was built for this question")
    for i in range(tries):
        try:
            body = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(EP, body, {"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=240) as r:
                body = r.read()
            try:
                return json.loads(body)["elements"]
            except ValueError:
                # Overpass answers 200 with an HTML page when it refuses a
                # query, so the reason has to be dug out of the page.
                text = body.decode("utf-8", "replace")
                msgs = re.findall(r"Error</strong>: (.*?)</p>", text)
                raise RuntimeError("; ".join(msgs) or text[:200])
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(10)


def selector(attrs):
    """The Overpass filter for a category or a brand."""
    if "brand:wikidata" in attrs:
        return f'["brand:wikidata"="{attrs["brand:wikidata"]}"]'
    parts = []
    for k in ("amenity", "shop", "tourism", "leisure", "office"):
        if k in attrs:
            parts.append(f'["{k}"="{attrs[k]}"]')
            break
    if "religion" in attrs:
        parts.append(f'["religion"="{attrs["religion"]}"]')
    return "".join(parts)


def anchor_set(place_attrs, name="a"):
    """The features the place name resolves to, as an Overpass set."""
    parts = []
    for ref in place_attrs.get("osm", "").split():
        t, _, i = ref.partition("/")
        parts.append(f"{t}({i});")
    return "(" + "".join(parts) + f")->.{name};"


def area_set(area_attrs, name="ar"):
    rid = area_attrs["osm"].split("/")[1]
    return f"area({3600000000 + int(rid)})->.{name};"


def count_of(query):
    """How many features the query finds, via Overpass's own count."""
    els = ask(query)
    for e in els:
        if e.get("type") == "count":
            return int(e["tags"]["total"])
    return len(els)


def sensitivity_counts(typ, values, a, s):
    """The two counts a sensitivity question turns on."""
    target = a.get("brand") or a.get("category")
    out = []
    for slot in ("radius_1", "radius_2"):
        r = a[slot]["metres"]
        if typ == "radius_sensitivity_compare":
            q = ("[out:json][timeout:120];" + anchor_set(a["place_1"], "a")
                 + f'nwr(around.a:{r}){selector(target)};out count;')
        else:
            q = ("[out:json][timeout:120];" + anchor_set(a["place"])
                 + f'nwr(around.a:{r}){selector(target)};out count;')
        out.append(count_of(q))
    return out


def rank_ok(typ, values, a, s):
    """Whether a question that ranks has anything to rank.

    Asking only whether the category exists in the ward is not enough. "Which
    cinema is in the largest building" wants cinemas that are in buildings,
    and more than one building, or the superlative picks the only candidate.
    "Which hotel has the most cafes near it" wants more than one hotel, and
    at least one cafe somewhere near them, or every count is zero and there
    is no most.
    """
    area = area_set(a["area"])
    head = "[out:json][timeout:120];"
    n = count_of(head + area + f'nwr(area.ar){selector(a["category"])};out count;')
    if n < 2:
        return False
    if typ == "containment_rank":
        # The containing areas that are buildings. is_in takes the members of
        # the set one at a time, so the category set is collected first.
        q = (head + area + f'nwr(area.ar){selector(a["category"])}->.c;'
             '.c is_in->.in; way(pivot.in)["building"];out count;')
        return count_of(q) >= 2
    r = a["radius"]["metres"]
    q = (head + area + f'nwr(area.ar){selector(a["category"])}->.c;'
         f'nwr(around.c:{r}){selector(a["neighbour"])};out count;')
    return count_of(q) >= 1


def query_for(typ, text, values, s):
    """A query that returns something when the question has an answer."""
    a = {slot: s[cc.kind_of(slot)][v] for slot, v in values.items()}
    head = "[out:json][timeout:120];"

    def radius(slot):
        return a[slot]["metres"]

    if typ in ("range_count", "nearest_neighbor", "existence"):
        target = a.get("brand") or a.get("category")
        r = (radius("radius") if "radius" in values else
             radius("radius_2") if "radius_2" in values else "500")
        return (head + anchor_set(a["place"]) +
                f'nwr(around.a:{r}){selector(target)};out ids 1;')
    if typ == "containment_count":
        # Inside means inside. Asking within fifty metres of the centre was a
        # stand-in, and it answered empty for Sensō-ji, Tokyo Skytree and
        # Takashimaya Times Square, which all have plenty inside them. A way
        # or relation becomes an area with map_to_area.
        return (head + anchor_set(a["place"]) +
                'way.a; map_to_area->.ar; relation.a; map_to_area->.ar2;'
                f'(nwr(area.ar){selector(a["category"])};'
                f'nwr(area.ar2){selector(a["category"])};);out ids 1;')
    if typ in ("containment_rank", "neighbour_count_rank"):
        # Handled by rank_ok, which needs more than one query.
        return None
    if typ == "multi_criteria_filter":
        if "area" in values:
            return (head + area_set(a["area"]) +
                    f'nwr(area.ar){selector(a["category"])};out ids 1;')
        return (head + anchor_set(a["place"]) +
                f'nwr(around.a:{radius("radius_1")})'
                f'{selector(a["category"])};out ids 1;')
    if typ == "multi_criteria_rank":
        return (head + anchor_set(a["place"]) +
                f'nwr(around.a:{radius("outer_radius")})'
                f'{selector(a["category"])};out ids 1;')
    if typ == "nearest_brand_compare":
        return (head + anchor_set(a["place"]) +
                f'nwr(around.a:2000){selector(a["brand_1"])};'
                f'nwr(around.a:2000){selector(a["brand_2"])};out ids 1;')
    if typ == "radius_sensitivity_compare":
        return (head + anchor_set(a["place_1"], "a") + anchor_set(a["place_2"], "b") +
                f'nwr(around.a:{radius("radius_2")}){selector(a["category"])};'
                f'nwr(around.b:{radius("radius_2")}){selector(a["category"])};'
                'out ids 1;')
    return None


def candidates(s, per_template, rng, attempts_per_hit=400):
    """Fillings worth asking about, drawn at random rather than enumerated.

    Enumerating is what count_combinations.py does, and at 111 million
    products it takes twenty-five minutes. Nothing here needs the whole list:
    five questions a type are wanted, so a few hundred candidates a template
    is plenty, and rejection sampling gets them in seconds. A template whose
    rules are tight enough that random draws keep failing gives up and is
    enumerated instead.
    """
    out = []
    for typ, num, text, slots in cc.templates():
        pools = [sorted(s[cc.kind_of(x)]) for x in slots]
        space = 1
        for p in pools:
            space *= len(p)
        seen = set()
        if space <= 200000:
            found = []
            for combo in itertools.product(*pools):
                values = dict(zip(slots, combo))
                if cc.allowed(text, slots, values, s):
                    found.append(combo)
            rng.shuffle(found)
            for combo in found[:per_template]:
                out.append((typ, num, text, dict(zip(slots, combo))))
            continue
        # Where an operator has to match the places, draw it first and offer
        # only the stations it runs. The both-operated-by template allows
        # 2,464 of 64 million fillings, which is four hits in a hundred
        # thousand blind draws, and one question came out of it.
        op_slot = next((x for x in slots if cc.kind_of(x) == "operator"), None)
        place_slots = [x for x in slots if cc.kind_of(x) == "place"]
        conditioned = None
        if op_slot and place_slots:
            conditioned = {}
            for op in s["operator"]:
                stations = [v for v in s["place"]
                            if op in [o.strip() for o in
                                      s["place"][v].get("operators", "").split(";")]]
                if stations:
                    conditioned[op] = stations
        tries = 0
        while len(seen) < per_template and tries < per_template * attempts_per_hit:
            tries += 1
            if conditioned:
                op = rng.choice(sorted(conditioned))
                pick = {}
                for x, p in zip(slots, pools):
                    if x == op_slot:
                        pick[x] = op
                    elif x in place_slots and "both operated by" in text:
                        pick[x] = rng.choice(conditioned[op])
                    elif x == place_slots[0]:
                        pick[x] = rng.choice(conditioned[op])
                    else:
                        pick[x] = rng.choice(p)
                combo = tuple(pick[x] for x in slots)
            else:
                combo = tuple(rng.choice(p) for p in pools)
            if combo in seen:
                continue
            values = dict(zip(slots, combo))
            if cc.allowed(text, slots, values, s):
                seen.add(combo)
                out.append((typ, num, text, values))
    return out


def fill(text, values):
    for slot, v in values.items():
        text = text.replace("{" + slot + "}", v)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--per-template", type=int, default=200,
                    help="how many candidates to draw from each template")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--type", help="one type only")
    a = ap.parse_args()
    s = cc.seeds()

    rng = random.Random(a.seed)
    t0 = time.time()
    pool = candidates(s, a.per_template, rng)
    if a.type:
        pool = [c for c in pool if c[0] == a.type]
    print(f"{len(pool):,} candidates drawn in {time.time()-t0:.1f}s")

    picked = pool if a.sample <= 0 else rng.sample(pool, min(a.sample, len(pool)))
    ok = empty = skipped = failed = 0
    yes = {True: 0, False: 0}
    t0 = time.time()
    for typ, num, text, values in picked:
        if typ in TRIVIAL:
            skipped += 1
            continue
        attrs = {slot: s[cc.kind_of(slot)][v] for slot, v in values.items()}
        try:
            if typ in ("containment_rank", "neighbour_count_rank"):
                if rank_ok(typ, values, attrs, s):
                    ok += 1
                else:
                    empty += 1
                    print(f"  nothing to rank  {fill(text, values)}")
                continue
            if typ in SENSITIVE:
                c1, c2 = sensitivity_counts(typ, values, attrs, s)
                if c1 != c2:
                    ok += 1
                else:
                    empty += 1
                    print(f"  same at both radii ({c1})  {fill(text, values)}")
                continue
            q = query_for(typ, text, values, s)
            if q is None:
                skipped += 1
                continue
            els = ask(q)
        except Exception as e:
            failed += 1
            print(f"  FAIL {typ} {e}")
            continue
        if typ in BOTH_WAYS:
            ok += 1
            yes[bool(els)] += 1
            continue
        if els:
            ok += 1
        else:
            empty += 1
            print(f"  empty  {fill(text, values)}")
    dt = time.time() - t0
    asked = ok + empty + failed
    print(f"\nasked {asked}, non-empty {ok}, empty {empty}, failed {failed}, "
          f"trivial {skipped}")
    if yes[True] or yes[False]:
        print(f"existence: yes {yes[True]}, no {yes[False]}")
    if asked:
        print(f"{dt:.1f}s total, {dt/asked:.2f}s per query")


if __name__ == "__main__":
    main()
