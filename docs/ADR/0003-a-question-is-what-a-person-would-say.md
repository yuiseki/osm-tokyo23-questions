# 0003. A question is what a person would say, not a specification

Accepted, 2026-09-15.

## Context

Two of the author's 34, tokyo_0023 and tokyo_0032, were held back while the
others were decomposed, because they carry an OSM tag in their prose:

    What is the shortest distance in metres from Shibuya Station operated by
    East Japan Railway to the boundary of Yoyogi Park (the leisure=park
    polygon)?

The question was whether `leisure=park` should become a slot.

## What the original was

The author's original was:

    JR 渋谷駅から代々木公園までの距離を教えてください。

tokyo_0022 is that sentence in English. tokyo_0023 is the same question with
the answer's definition written into it: which distance, measured to what,
and the tag that fixes which feature is meant. It is not a second question. It
is the specification that makes the first one answerable.

The same adjustment is visible in the anchor. The original says JR 渋谷駅.
`JR` cannot be derived from the data, because none of the 205 stations in
these regions carries operator:short or operator:short:en, so it became
"operated by East Japan Railway", which operator:en does supply. The sentence
moved toward what the data can express.

## Decision

tokyo_0023 and tokyo_0032 are not templates. The set holds questions a person
would say. Where a question is ambiguous, that is a property of the question
and not a defect to be written out of it.

They stay under `data/originals/` with their `_question`, `level` and `type`
and no `_template`, as a record of what the translation to English changed.

## Consequence

31 templates, unchanged. No template contains an OSM tag.
