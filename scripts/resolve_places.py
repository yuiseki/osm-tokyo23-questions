#!/usr/bin/env python3
"""What each place seed names in OpenStreetMap, asked of an Overpass server.

The seeds hold what a person would say. What that names in the data is a
different fact, and the two do not line up: "Shibuya Station" names five
stations, "Aoyama Cemetery" is tagged "Aoyama Cemetery(Sakura)", and nothing
at all is tagged "University of Tokyo" on its own.

Nothing here is written back into data/. The result is used to decide which
filled questions are worth keeping, and to see which places carry the
ambiguity that ADR 0002 says the value carries.

    python3 scripts/resolve_places.py [--out tmp/checks/places.json]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

EP = os.environ.get("OVERPASS_URL", "https://overpass.yuiseki.net/api/interpreter")
UA = "osm-tokyo23-questions/0.1 (seed resolution check)"
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# The remote server holds the planet, so the search is narrowed to Tokyo. The
# local extract is already the twenty-three wards and nothing else, and its
# prefecture boundary is clipped, so no area can be built from it: there the
# scope is the whole database.
AREA_FILTER = os.environ.get(
    "OVERPASS_AREA", 'area["name:en"="Tokyo"]["admin_level"="4"]->.a;')
SCOPE = "(area.a)" if AREA_FILTER else ""
AREA = "[out:json][timeout:60];" + AREA_FILTER

# The noun the person said, and what it is tagged as. "Shibuya Station" must
# resolve to a station: matching the name alone also found a ramen shop whose
# name:en is "Shibuya", and widening "Oshiage" found a rice-cracker shop, a
# cat cafe, a police box and a primary school. The noun is in the sentence,
# so it costs nothing to use it.
EXPECTED = [
    (" Station", ['nwr{s}["railway"="station"]{f};']),
    (" University", ['nwr{s}["amenity"="university"]{f};']),
    (" Cemetery", ['nwr{s}["landuse"="cemetery"]{f};']),
    (" Park", ['nwr{s}["leisure"="park"]{f};']),
    (" Hotel", ['nwr{s}["tourism"="hotel"]{f};']),
    (" Street", ['way{s}["highway"]{f};']),
    (" Avenue", ['way{s}["highway"]{f};']),
    ("-dori", ['way{s}["highway"]{f};']),
]

# Tags that make an element a thing a person would point at. A station is a
# place; the bus stop, the crossing and the subway entrance outside it are
# not, and matching by name alone drags in dozens of them.
PLACE_TAGS = [
    'nwr{s}["railway"="station"]{f};',
    'nwr{s}["amenity"]{f};',
    'nwr{s}["leisure"]{f};',
    'nwr{s}["landuse"]{f};',
    'nwr{s}["tourism"]{f};',
    'nwr{s}["shop"]{f};',
    'nwr{s}["office"]{f};',
    'nwr{s}["building"]{f};',
    'nwr{s}["historic"]{f};',
    'way{s}["highway"~"^(primary|secondary|tertiary|residential|'
    'unclassified|pedestrian|living_street|service)$"]{f};',
]
# Even within those, these are fragments of infrastructure rather than places.
DROP = [("highway", "bus_stop"), ("highway", "traffic_signals"),
        ("highway", "crossing"), ("highway", "motorway_junction"),
        ("railway", "subway_entrance"), ("railway", "tram_stop"),
        ("public_transport", "stop_position"),
        ("public_transport", "platform"), ("railway", "platform")]


def ask(query, tries=3):
    for i in range(tries):
        try:
            body = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(EP, body, {"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)["elements"]
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(20)


def hand_name(value):
    """A spelling the data uses that the value does not.

    "Shinjuku-dori Avenue" was tagged that way a year ago and is now
    "Shinjuku-dori Ave.". The value stays as a person would say it and the
    seed file carries the data's spelling, the same arrangement the wards and
    the brands already use.
    """
    path = os.path.join(BASE, "data/seeds/place", value)
    if not os.path.exists(path):
        return None
    for line in open(path):
        if line.startswith("name:en="):
            return line.strip().split("=", 1)[1]
    return None


def sayable_forms(value):
    """The shapes the same name takes in the data.

    The article belongs to the value (ADR 0001) and never appears in name:en.
    OSM station names do not carry the word Station: Shibuya Station is
    name=渋谷 plus railway=station.
    """
    forms = {value}
    hand = hand_name(value)
    if hand:
        forms.add(hand)
    forms.add(re.sub(r"^[Tt]he ", "", value))
    for f in list(forms):
        if f.endswith(" Station"):
            forms.add(f[: -len(" Station")])
        # ADR 0001 puts a trailing generic noun into the value, so that
        # "the Shibuya Stream building" can stand where a template says
        # "inside {place}". The noun is not part of the name in the data.
        for generic in (" building", " Building"):
            if f.endswith(generic):
                forms.add(f[: -len(generic)])
        if f.startswith("JR "):
            forms.add(f[3:])
            if f.endswith(" Station"):
                forms.add(f[3: -len(" Station")])
    return sorted(forms)


def expected_for(value):
    for suffix, parts in EXPECTED:
        if value.endswith(suffix):
            return parts
    return PLACE_TAGS


def build(forms, mode, parts=None):
    """exact, then contains. Two passes rather than one loose pass, so that a
    name that resolves cleanly is never widened and never picks up a
    neighbour that merely contains it."""
    alt = "|".join(re.escape(f) for f in forms)
    f = (f'["name:en"~"^({alt})$"]' if mode == "exact"
         else f'["name:en"~"({alt})"]')
    return AREA + "(" + "".join(p.format(f=f, s=SCOPE)
                                for p in (parts or PLACE_TAGS)) + ");out tags center;"


KIND_KEYS = ["railway", "amenity", "leisure", "landuse", "tourism", "shop",
             "office", "historic", "building", "highway"]


def kind(tags):
    """The tag that says what kind of thing this is, most specific first."""
    for k in KIND_KEYS:
        if k in tags:
            return f"{k}={tags[k]}"
    return None


def keep(tags):
    return not any(tags.get(k) == v for k, v in DROP)


def resolve(value):
    forms = sayable_forms(value)
    parts = expected_for(value)
    for mode in ("exact", "contains"):
        els = [e for e in ask(build(forms, mode, parts)) if keep(e.get("tags", {}))]
        if els:
            return mode, els
    return "none", []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "tmp/checks/places.json"))
    ap.add_argument("--only", help="resolve one value only")
    a = ap.parse_args()

    seeds = sorted(os.listdir(os.path.join(BASE, "data/seeds/place")))
    if a.only:
        seeds = [s for s in seeds if s == a.only] or [a.only]
    out = {}
    for value in seeds:
        mode, els = resolve(value)
        out[value] = {"match": mode, "n": len(els), "elements": [
            {"type": e["type"], "id": e["id"],
             "kind": kind(e.get("tags", {})),
             "name": e.get("tags", {}).get("name"),
             "name:en": e.get("tags", {}).get("name:en"),
             "operator:en": e.get("tags", {}).get("operator:en")
                            or e.get("tags", {}).get("operator"),
             "center": e.get("center") or ({"lat": e.get("lat"), "lon": e.get("lon")}
                                           if "lat" in e else None)}
            for e in els]}
        print(f"{value:32s} {mode:8s} {len(els):3d}", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("\nwrote", a.out)


if __name__ == "__main__":
    main()
