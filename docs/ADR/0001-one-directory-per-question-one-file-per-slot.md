# 0001. A question is a directory, a slot is a file

Accepted, 2026-09-14.

## Context

The set is assembled by hand from templates and curated values. Nothing is
synthesised and no answers are stored, so the format's only job is to be
editable in a text editor and readable in a diff.

## Decision

One directory per question. One file per slot, named for the slot, holding
that slot's values one per line. Files beginning with an underscore are
records rather than inputs:

    _template   the sentence with its literal spans replaced by slots
    _question   the sentence as the author wrote it
    _source     how the sentence came to exist (ADR 0006)

`level` and `type` are attributes of the question, not slots.

A template must reproduce its `_question` exactly when its slots are filled
with the first line of each file. That is checkable and is how two mistakes
were caught: a missing question, and two slots left un-numbered.

## Rules that follow

A value is a complete way of saying the thing, article included. "the Grand
Hyatt Tokyo", not "Grand Hyatt Tokyo" with a "the" left in the template. The
same applies to a trailing noun that belongs to the name: "the Shibuya Stream
building" is the value and the template reads `How many {category} are inside
{place}?`, which then also serves a park or a station concourse.

When two slots of the same kind stand side by side, both are numbered:
`{place_1}` and `{place_2}`, never `{place}` beside `{place_2}`. When they
differ in meaning rather than position, the meaning names them:
`{outer_radius}` and `{inner_radius}`.

`operated by {operator}` is not absorbed into the place value. The pair with
it and without it is the point: "Shibuya Station" names five features in
OpenStreetMap and "Shibuya Station operated by East Japan Railway" names one.
Keeping the clause in the template keeps both versions of every question
available.

## Consequence

The author's 34 questions produced 31 templates. Ten of them are a pair
differing only in that clause.

## A file to hand out, from 2026-09-15

`data/questions.jsonl` is the same content in one file, one JSON object per
question, built by `scripts/build_jsonl.py` and never edited. It exists
because that is the shape a dataset host expects, and the directories are
still where a question is edited and where a diff is read.

Each file in a question's directory is a field. The underscore records lose
the underscore, `_source` is split on its `key=value` lines into `source`,
`template_file` and `checked`, and every other file is a slot keeping its own
name, so a row has `place` and `radius` only where the template asked for
them.

`--check` rebuilds from the directories and compares, so the two cannot
drift apart unnoticed.
