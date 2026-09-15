# 0006. The questions are numbered in one sequence

Accepted, 2026-09-15.

## Context

The 34 questions arrived with two id series. `tokyo_hNN` were written from
scratch. `tokyo_eNN` are eleven of those same sentences with the anchor name
replaced, and the letter was the only thing recording that.

The difference matters to whoever built the answers and not to whoever reads
the question set. It also leaked a numbering with holes: h03 is absent, and
the e-numbers mirror h-numbers, so the series runs e01 to e04, then e11 to
e14, then e20, e23, e24.

## What h03 was

It was the explicit counterpart of tokyo_0021, "Which is the nearest Shinto
shrine to Shibuya Station operated by East Japan Railway?". It was dropped
upstream when distance was redefined from representative point to
`ST_Distance`: on that definition the first shrine is 286.8 metres away and
the second 301.0, a gap of 14.2 metres, and the answer stops being unique.
Its re-anchored twin survived and is tokyo_0026.

Recorded in `poi-qa/tmp/memo/qa.md`.

## Decision

`tokyo_NNNN`, one sequence, in the order the source file lists them, with
anything written later appended. The
provenance moves into a file, `_source`, which carries the string the source
data uses:

    human-authored                                      26
    human-authored, anchor substituted                   9
    human-authored, anchor and target substituted        2

That string is the claim this dataset has to be able to defend: no question's
prose was written by a model. The substitution was mechanical, done by
`poi-qa/scripts/build_human_qa.py`, which reuses the author's sentence and
replaces only the anchor name. It was done because eleven of the first
twenty-four were anchored on Shibuya Station, so one anchor's difficulty
governed 45 per cent of the set.

## The mapping

| new | old | source |
| --- | --- | --- |
| tokyo_0001 | tokyo_h01 | human-authored |
| tokyo_0002 | tokyo_h02 | human-authored |
| tokyo_0003 | tokyo_h04 | human-authored |
| tokyo_0004 | tokyo_h05 | human-authored |
| tokyo_0005 | tokyo_h06 | human-authored |
| tokyo_0006 | tokyo_h07 | human-authored |
| tokyo_0007 | tokyo_h08 | human-authored |
| tokyo_0008 | tokyo_h09 | human-authored |
| tokyo_0009 | tokyo_h10 | human-authored |
| tokyo_0010 | tokyo_h11 | human-authored |
| tokyo_0011 | tokyo_h12 | human-authored |
| tokyo_0012 | tokyo_h13 | human-authored |
| tokyo_0013 | tokyo_h14 | human-authored |
| tokyo_0014 | tokyo_h15 | human-authored |
| tokyo_0015 | tokyo_h16 | human-authored |
| tokyo_0016 | tokyo_h17 | human-authored |
| tokyo_0017 | tokyo_h18 | human-authored |
| tokyo_0018 | tokyo_h19 | human-authored |
| tokyo_0019 | tokyo_h20 | human-authored |
| tokyo_0020 | tokyo_h21 | human-authored |
| tokyo_0021 | tokyo_h22 | human-authored |
| tokyo_0022 | tokyo_h23 | human-authored |
| tokyo_0023 | tokyo_h24 | human-authored |
| tokyo_0024 | tokyo_e01 | human-authored, anchor substituted |
| tokyo_0025 | tokyo_e02 | human-authored, anchor substituted |
| tokyo_0026 | tokyo_e03 | human-authored, anchor substituted |
| tokyo_0027 | tokyo_e04 | human-authored, anchor substituted |
| tokyo_0028 | tokyo_e11 | human-authored, anchor substituted |
| tokyo_0029 | tokyo_e12 | human-authored, anchor substituted |
| tokyo_0030 | tokyo_e14 | human-authored, anchor substituted |
| tokyo_0031 | tokyo_e23 | human-authored, anchor and target substituted |
| tokyo_0032 | tokyo_e24 | human-authored, anchor and target substituted |
| tokyo_0033 | tokyo_e13 | human-authored, anchor substituted |
| tokyo_0034 | tokyo_e20 | human-authored, anchor substituted |

## Three sentences that were not in the source file

tokyo_0035 to tokyo_0037 were written into the conversation on 2026-09-14 and
had no id of their own:

| id | question |
| --- | --- |
| tokyo_0035 | How many convenience stores are located near JR Shibuya Station? |
| tokyo_0036 | Which cafe is closest to Shibuya Station? |
| tokyo_0037 | Where is the nearest park to Shibuya 109? |

They supply what the 34 did not have: a proximity with no radius, and a
nearest-feature question with the category as a variable and in the singular.

tokyo_0037 was written as "Shibuya 190" and kept that way until the author
said it was a mistyped "Shibuya 109". Nothing in the data is named Shibuya
190, which is how the question came to be looked at: it was the one place
seed that resolved to nothing.

They carried no recorded level, and none is invented for them. ADR 0002 says
the level belongs to the filled question and depends on what the value names
in the data, so it is not derivable from the sentence.

A fourth sentence was listed with them for a while and has been removed:
"How many cafes are there around Shibuya 109?" is mine, not the author's. It
was my English for something the author had said in Japanese, and it was then
recorded as if the author had written it. `tmp/original.md` keeps the record.
Nothing in `data/` contains it.

## Consequence

37 questions, 34 templates in 15 types, 40 seed values in 7 kinds, 359 files
under `data/`. The ADRs before this one were written with the old ids and now
name the new ones. Templates and seeds carry no question id, so the
renumbering did not touch them; the three new sentences added three templates
and five seed values.
