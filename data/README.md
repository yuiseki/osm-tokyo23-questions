---
license: odbl
language:
- en
task_categories:
- question-answering
- text-retrieval
tags:
- openstreetmap
- geospatial
- tokyo
- text-to-sql
- overpass
- benchmark
size_categories:
- n<1K
---

# osm-tokyo23-questions

Questions a person would ask about the twenty-three special wards of Tokyo,
written to be answered from OpenStreetMap. 215 of them, in twenty kinds.

**No answers.** The set is questions and nothing else. Answers belong to a
particular extract on a particular day, and a question carrying its own answer
stops being a question. What is recorded instead is which data each question
was checked against, so that someone can compute the answers and say what they
computed them from.

**No prose written by a model.** Every sentence, and every value that fills a
slot in one, was written or chosen by a person. This matters for a benchmark:
text from a commercial assistant would tie the set to the phrasings that
assistant favours, and would muddy where the data came from.

## A record

```json
{
  "id": "filled/tokyo/0090",
  "origin": "filled",
  "region": "tokyo",
  "question": "How many Starbucks are within 250 metres of Meiji-dori Avenue?",
  "template": "How many {brand} are within {radius} of {place}?",
  "type": "range_count",
  "brand": "Starbucks",
  "place": "Meiji-dori Avenue",
  "radius": "250 metres",
  "source": "filled from a template and the seeds",
  "template_file": "type_range_count/0001.txt",
  "checked": "tokyo23-260831.osm.pbf md5 44a4ba2182379c147f20a27ad1b513ef, osm_base 2026-08-30T23:50:59Z"
}
```

| field | meaning |
|---|---|
| `id` | `<origin>/<region>/<number>` |
| `origin` | `written`, a sentence a person wrote; `filled`, a template with values put in |
| `question` | the sentence |
| `template` | the same sentence with its literal spans replaced by slots |
| `type` | what the question asks for, twenty of them |
| `level` | the difficulty recorded for the first 34. Absent elsewhere |
| `source` | how the sentence came about |
| `template_file` | which template, for a filled question |
| `checked` | the data a filled question was checked against |

Every other field is a slot, and a row carries it only where its template asked
for one: `place`, `place_1`, `place_2`, `target`, `category`, `neighbour`,
`neighbour_1`, `neighbour_2`, `brand`, `brand_1`, `brand_2`, `operator`,
`radius`, `radius_1`, `radius_2`, `outer_radius`, `inner_radius`, `area`,
`count`, `name`. Filling a template with its own slot values reproduces its
question exactly, which is how two mistakes were caught while building it.

## The twenty types

| | | |
|---|---|---|
| nearest_neighbor 16 | attribute_lookup 14 | distance 14 |
| range_count 14 | multi_criteria_filter 13 | bearing 12 |
| multi_criteria_rank 12 | nearest_brand_compare 12 | radius_sensitivity 12 |
| area_compare 11 | area_rank 11 | containment_count 11 |
| containment_rank 11 | existence 11 | radius_sensitivity_compare 11 |
| neighbour_count_rank 11 | length_total 9 | name_count 7 |
| distance_definition_sensitivity 2 | anchor_sensitivity 1 | |

The last two exist only among the written questions. They are not shapes of
sentence: their difficulty is carried by the value. "Which is the nearest
Shinto shrine to Shibuya Station?" is the same sentence as one filed under
`nearest_neighbor`, and it is a question about ambiguity only because Shibuya
Station names five stations in OpenStreetMap, separable by operator alone.

Several types are about that kind of trouble rather than around it.

- `existence` keeps both answers. Three of its five are yes and two are no,
  because a set where every answer is yes teaches less.
- `radius_sensitivity` and `radius_sensitivity_compare` ask whether the answer
  changes with the radius, and are only kept where it does.
- `name_count` asks how many stations carry a name, which is the ambiguity the
  other questions run into, asked directly.
- One question names Sapporo Station, which this extract does not cover.

## Where the questions come from

41 were written as sentences. 174 were filled from 38 templates and a list of
curated values, and every one of them was asked of the data first: a question
whose answer is empty, or whose ranking has one candidate, or whose two radii
give the same count, is not in the set.

The second 84 of those were added on 2026-09-16 with a vocabulary chosen for
where models are weak rather than for what comes to mind first. The nine
categories this set began with are cafe, restaurant, hotel, park, church,
cinema, bar, nightclub and convenience store, and three language models
writing SQL name those tags correctly almost every time. Twenty tags were
added ranked the other way, by how often those models failed to name them:
shop=car_repair at 86%, shop=bicycle at 85%, shop=confectionery at 80%,
office=estate_agent at 75%, down to amenity=parking at 15%. The boundary
between `shop` and `amenity` and `craft` and `office` is where they fall
off. `provenance.yaml` has the detail and
the ADRs in the repository have the reasoning.

The values are real: 62 places, 23 brands, 23 wards, 58 categories, 11 radii,
8 operators, 7 station names. Each carries what it is in OpenStreetMap, which
is what lets a filling be rejected before anything is asked. "Shibuya Station
operated by Tokyo Metro" is possible and "JR Shibuya Station operated by Tokyo
Metro" is not.

## The tags, separately

`tag_hints.jsonl` beside this file says which OpenStreetMap tags each question
turns on, keyed by `id`:

```json
{"id": "written/tokyo/0001",
 "osm_tag_hints": ["amenity=cafe", "brand:wikidata=Q37158",
                   "cuisine=coffee_shop", "operator:en=East Japan Railway",
                   "railway=station"]}
```

215 questions, 123 distinct tags. Not an answer: an answer belongs to a
particular extract on a particular day, and a tag is what the thing is called
in OpenStreetMap whichever day it is. Not new either; every one of them is in
the seeds beside the value that names it.

It is a separate file rather than a column because naming the tag is the step
that is hard. Asked to write SQL for 1,206 questions of this shape with no
examples, Qwen2.5-Coder-3B chose the right value under the wrong key for a
quarter of the categories it named, and Qwen3.6-35B-A3B for a fifth: `shop`
written as `amenity`, `amenity=pharmacy` as `healthcare=pharmacy`,
`shop=hairdresser` as `craft=hairdresser`. A hint in the same row as the
question is handed to whatever is being measured on it. Join it on `id` when
that is what is wanted.

Greedy, because it is a hint and not a specification. The category, the brand
and the class it belongs to, the operator, a ward's boundary tags and the name
OpenStreetMap gives it, the kind of thing a place is, and the key an attribute
question reads, which is a key on its own because its value is the answer.

## Checked against

[yuiseki/osm-tokyo23-src-2026-08](https://huggingface.co/datasets/yuiseki/osm-tokyo23-src-2026-08)

    tokyo23-260831.osm.pbf
    md5 44a4ba2182379c147f20a27ad1b513ef, 87,399,745 bytes
    osm_base 2026-08-30T23:50:59Z

The twenty-three wards cut from the planet file of 2026-08-31. That dataset
ships the same extract this set was checked against, along with the ward
boundary it was cut with and the same data as PostGIS parquet, so the answers
can be computed in SQL or in Overpass QL from one frozen source.

Naming the data is not a formality. A year-old server was tried first and
disagreed: Yoyogi Park was a way and is now a relation, one Shinjuku Station
node is gone, and a street was renamed from "Shinjuku-dori Avenue" to
"Shinjuku-dori Ave." and stopped resolving. Answers computed against a
different extract will differ, and questions that have an answer here may not
have one there.

## Source

GitHub: [yuiseki/osm-tokyo23-questions](https://github.com/yuiseki/osm-tokyo23-questions)
holds what these questions are made of: one directory per question, the
templates, and the seed values with what each one is in OpenStreetMap.

The data to answer them against is
[yuiseki/osm-tokyo23-src-2026-08](https://huggingface.co/datasets/yuiseki/osm-tokyo23-src-2026-08).

## License

ODbL-1.0. (The Hub's license identifier for this is `odbl`.)

The questions name real places, brands and operators, read from
[OpenStreetMap](https://www.openstreetmap.org/), so this is a Derivative
Database:

    (c) OpenStreetMap contributors, available under the Open Database License.
    https://www.openstreetmap.org/copyright

Answers computed from these questions against OSM are derived from OSM and
carry ODbL too. The full notice is in `LICENSE` beside this file.
