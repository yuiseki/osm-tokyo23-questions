#!/usr/bin/env python3
"""How many fillings of each template are worth asking about.

The cartesian product of the seeds is mostly nonsense: it asks the opening
hours of a station's operator, the total length of a hotel, and how many
Starbucks are inside a street. The seed attributes say what each value is in
OpenStreetMap, so most of that can be dropped without asking a server.

This only counts. Nothing is written.

    python3 scripts/count_combinations.py [--per-template]
"""
import argparse
import itertools
import os
import re

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# A slot's name says which seed kind fills it. Two names are the same kind
# under a different role, because a template sometimes needs two at once.
KIND = {"neighbour": "category", "target": "place"}


def seeds():
    out = {}
    for kind in sorted(os.listdir(os.path.join(BASE, "data/seeds"))):
        d = os.path.join(BASE, "data/seeds", kind)
        out[kind] = {}
        for value in sorted(os.listdir(d)):
            attrs = {}
            for line in open(os.path.join(d, value)):
                line = line.strip()
                if "=" in line:
                    k, _, v = line.partition("=")
                    attrs.setdefault(k, v)
            out[kind][value] = attrs
    return out


def kind_of(slot):
    base = re.sub(r"_\d+$", "", slot)
    base = re.sub(r"^(outer|inner)_", "", base)
    return KIND.get(base, base)


def templates():
    out = []
    root = os.path.join(BASE, "data/templates")
    for t in sorted(os.listdir(root)):
        for f in sorted(os.listdir(os.path.join(root, t))):
            text = open(os.path.join(root, t, f)).read().strip()
            out.append((t[len("type_"):], f[:-4], text,
                        re.findall(r"\{(\w+)\}", text)))
    return out


def is_area(attrs):
    """Something a thing can be inside of, and something with a footprint."""
    kinds = attrs.get("kind", "")
    if not kinds or kinds.startswith("highway="):
        return False
    return any(t in attrs.get("element", "") for t in ("way", "relation"))


def is_station(attrs):
    return "railway=station" in attrs.get("kind", "")


def category_tag(attrs):
    for k in ("amenity", "shop", "tourism", "leisure", "office"):
        if k in attrs:
            return f"{k}={attrs[k]}"
    return None


_NUMBER = None


def wanted_number(text, slot):
    """Singular or plural, as the author filled this slot in this sentence.

    Reading it off the surrounding words was tried and got two of them
    backwards: "List every hotel" is singular and "Among hotels" is plural,
    and no rule about the preceding word separates them. Every template came
    from a question the author wrote, so the answer is in the data.
    """
    global _NUMBER
    if _NUMBER is None:
        _NUMBER = {}
        cats = {}
        root = os.path.join(BASE, "data/seeds/category")
        for v in os.listdir(root):
            for line in open(os.path.join(root, v)):
                if line.startswith("number="):
                    cats[v] = line.strip().split("=")[1]
        base = os.path.join(BASE, "data/originals/tokyo")
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d)
            t = os.path.join(p, "_template")
            if not os.path.exists(t):
                continue
            tpl = open(t).read().strip()
            for name in re.findall(r"\{(\w+)\}", tpl):
                if kind_of(name) != "category":
                    continue
                value = open(os.path.join(p, name)).read().strip()
                _NUMBER.setdefault((tpl, name), cats.get(value))
    return _NUMBER.get((text, slot))


def allowed(text, slots, values, s):
    """Whether this filling is worth asking. Every rule here is decided from
    the seed attributes, not from a query."""
    a = {slot: s[kind_of(slot)][v] for slot, v in values.items()}

    # The operated-by clause exists to pick one feature out of several with
    # the same name. Only a station has it, and only that station's operators.
    if "operator" in values:
        # The clause governs the place it follows. "both operated by X" says
        # so explicitly and governs every place in the sentence; anywhere else
        # only the slot immediately before it is a station, and the target of
        # a distance is not.
        if "both operated by" in text:
            governed = [k for k in values if kind_of(k) == "place"]
        else:
            m = re.search(r"\{(\w+)\} operated by \{operator\}", text)
            governed = [m.group(1)] if m else []
        for slot in governed:
            if not is_station(a[slot]):
                return False
            ops = [o.strip() for o in a[slot].get("operators", "").split(";")]
            if values["operator"] not in ops:
                return False
            # "JR Shibuya Station operated by Tokyo Metro" contradicts
            # itself. The data cannot tell the JR station from the others,
            # which is the point of keeping the value, but the sentence can.
            if values[slot].startswith("JR ") and \
                    not values["operator"].startswith("East Japan Railway"):
                return False

    # An attribute question needs the attribute. The four templates ask about
    # four tags, and a place that does not carry one cannot answer it.
    ATTR = {"storeys": "building:levels", "erected": "start_date",
            "wireless internet": "internet_access",
            "opening hours": "opening_hours"}
    for word, key in ATTR.items():
        if word in text:
            if key not in a["place"].get("attributes", "").split(","):
                return False

    # Inside, and the footprint comparison, need something with an inside.
    if "are inside {place}" in text and not is_area(a["place"]):
        return False
    if "larger footprint" in text:
        # A building, because the sentence says building, and one building:
        # "the University of Tokyo" carries building=university among eight
        # kinds across twenty features, which is a campus, not a thing with a
        # footprint to compare.
        for slot in ("place_1", "place_2"):
            kinds = a[slot].get("kind", "").split(",")
            if not any(k.startswith("building=") for k in kinds):
                return False
            if len(kinds) > 2 or int(a[slot].get("features", "0")) > 2:
                return False
    # A length is a length of a way.
    if "total length" in text and not a["place"].get("kind", "").startswith(
            "highway="):
        return False

    # Two brands compared are compared as the same kind of thing. The
    # question the author wrote is a McDonald's against a Burger King, not a
    # cafe against a bank.
    brands = [k for k in values if kind_of(k) == "brand"]
    if len(brands) == 2:
        if category_tag(a[brands[0]]) != category_tag(a[brands[1]]):
            return False

    # Two places compared have to be two places. "Shibuya Station" and "JR
    # Shibuya Station" are different values that name the same five stations,
    # and "Shibuya Stream" and "the Shibuya Stream building" are one way
    # under two names, so comparing the values is not enough: the features
    # they resolve to must not overlap.
    places = [k for k in values if kind_of(k) == "place"]
    if len(places) > 1:
        refs = [set(a[k].get("osm", "").split()) for k in places]
        for i in range(len(refs)):
            for j in range(i + 1, len(refs)):
                if refs[i] & refs[j]:
                    return False

    # A thing is not near itself and does not contain itself. "hotel" and
    # "hotels" are different seed values, so comparing the values misses it;
    # the tag is what says they are the same kind of thing.
    cats = [k for k in values if kind_of(k) == "category"]
    if len(cats) > 1:
        tags = [category_tag(a[k]) for k in cats]
        if len(set(tags)) != len(tags):
            return False
    if cats and "place" in values:
        place_kinds = a["place"].get("kind", "").split(",")
        if any(category_tag(a[k]) in place_kinds for k in cats):
            if "inside {place}" in text or "are inside" in text:
                return False

    # A brand is a kind of category; pairing them only says something when
    # the category contains the brand.
    for b in [k for k in values if kind_of(k) == "brand"]:
        for c in [k for k in values if kind_of(k) == "category"]:
            if category_tag(a[b]) != category_tag(a[c]):
                return False

    # Two slots of the same kind side by side must differ, and the two radii
    # of a sensitivity question must be in order.
    for kind in ("place", "category", "brand"):
        same = [v for k, v in values.items() if kind_of(k) == kind]
        if len(same) != len(set(same)):
            return False
    # "a 250 metre radius" and "within 250 metres" are the same distance in
    # two shapes, and English does not let them swap. The shape is a property
    # of the position, so the seed holds both and the sentence picks.
    for slot, v in values.items():
        if kind_of(slot) != "radius":
            continue
        attributive = re.search(r"a \{" + slot + r"\}[^?]*radius", text)
        want = "attributive" if attributive else "plural"
        if a[slot].get("form") != want:
            return False

    radii = [(k, v) for k, v in values.items() if kind_of(k) == "radius"]
    if len(radii) == 2:
        (k1, v1), (k2, v2) = sorted(radii)
        if int(s["radius"][v1]["metres"]) >= int(s["radius"][v2]["metres"]):
            return False

    # Plural where the sentence asks for many, singular where it asks for one.
    for slot, v in values.items():
        if kind_of(slot) == "category":
            want = wanted_number(text, slot)
            if want and a[slot].get("number") != want:
                return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-template", action="store_true")
    a = ap.parse_args()
    s = seeds()
    print("seeds: " + ", ".join(f"{k} {len(v)}" for k, v in s.items()))
    print()
    by_type = {}
    for typ, num, text, slots in templates():
        pools = [sorted(s[kind_of(x)]) for x in slots]
        raw = 1
        for p in pools:
            raw *= len(p)
        ok = 0
        for combo in itertools.product(*pools):
            values = dict(zip(slots, combo))
            if allowed(text, slots, values, s):
                ok += 1
        by_type.setdefault(typ, [0, 0])
        by_type[typ][0] += raw
        by_type[typ][1] += ok
        if a.per_template:
            print(f"{typ + '/' + num:44s} {raw:>12,} -> {ok:>9,}")
    if a.per_template:
        print()
    print(f"{'type':34s} {'cartesian':>14s} {'allowed':>11s}")
    for typ in sorted(by_type, key=lambda t: -by_type[t][1]):
        raw, ok = by_type[typ]
        print(f"{typ:34s} {raw:>14,} {ok:>11,}")
    print(f"{'total':34s} {sum(v[0] for v in by_type.values()):>14,} "
          f"{sum(v[1] for v in by_type.values()):>11,}")


if __name__ == "__main__":
    main()
