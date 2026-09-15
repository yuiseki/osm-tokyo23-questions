# osm-tokyo23-questions

Questions about the twenty-three special wards of Tokyo, written to be
answered from OpenStreetMap. 131 of them, in twenty kinds, with no answers.

The dataset is on the Hub. This repository is what it is made of.

- Dataset: [yuiseki/osm-tokyo23-questions](https://huggingface.co/datasets/yuiseki/osm-tokyo23-questions)
- Data to answer against: [yuiseki/osm-tokyo23-src-2026-08](https://huggingface.co/datasets/yuiseki/osm-tokyo23-src-2026-08)

Two rules shape everything here. **No answers**: an answer belongs to a
particular extract on a particular day, so what is recorded is which data each
question was checked against. **No prose written by a model**: every sentence,
and every value that fills a slot in one, was written or chosen by a person.

## Layout

    data/originals/tokyo/NNNN/   41 sentences as a person wrote them
    data/questions/tokyo/NNNN/   90 templates with curated values put in
    data/templates/type_*/       38 templates, filed by what they ask for
    data/seeds/<kind>/<value>    what may fill a slot, and what it is in OSM
    data/questions.jsonl         all 131, one object per line, built not edited

A question is a directory and a slot is a file, so a change to one shows up in
a diff as itself. Filling a template with its own slot files reproduces its
question exactly, which is checkable and is how two mistakes were caught.

## Scripts

    resolve_places.py          what each place seed names in OSM
    write_place_attributes.py  write that back beside the value
    write_place_answerable.py  which attribute questions a place can answer
    compare_resolutions.py     what changed between two resolution runs
    count_combinations.py      how many fillings the tags allow
    check_nonzero.py           which of them have something to find
    select_questions.py        choose five per type, spread across values
    build_jsonl.py             data/questions.jsonl, with --check
    publish.py                 push to the Hub, with a dry run by default

They ask an Overpass server, `OVERPASS_URL`, holding the extract above. Set
`OVERPASS_AREA=` empty for an extract that is already the region.

## Why it is built this way

The decisions, and what went wrong before each one, are in `docs/ADR/`.

| | |
|---|---|
| [0001](docs/ADR/0001-one-directory-per-question-one-file-per-slot.md) | A question is a directory, a slot is a file |
| [0002](docs/ADR/0002-templates-are-filed-by-type-not-by-level.md) | Templates are filed by type, and the level belongs to the question |
| [0003](docs/ADR/0003-a-question-is-what-a-person-would-say.md) | A question is what a person would say, not a specification |
| [0004](docs/ADR/0004-seeds-are-flat-lists-of-what-is-said.md) | Seeds are flat lists of what is said, not a tag hierarchy |
| [0005](docs/ADR/0005-the-dataset-lives-under-data.md) | The dataset lives under data/, and the sentences are tracked |
| [0006](docs/ADR/0006-the-questions-are-numbered-in-one-sequence.md) | The questions are numbered in one sequence |
| [0007](docs/ADR/0007-a-filling-is-checked-before-it-is-kept.md) | A filling is checked twice, by tag and by query |
| [0008](docs/ADR/0008-the-filled-questions-live-apart-from-the-originals.md) | The filled questions live apart from the originals |

`data/README.md` is the dataset card, and `data/provenance.yaml` says who wrote
what and what was checked against which data.

## License

ODbL-1.0. The questions name real places, brands and operators read from
[OpenStreetMap](https://www.openstreetmap.org/), so this is a Derivative
Database, and answers computed from these questions carry ODbL too. The notice
is in `data/LICENSE`.
