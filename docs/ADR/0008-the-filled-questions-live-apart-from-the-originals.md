# 0008. The filled questions live apart from the originals

Accepted, 2026-09-15.

## Context

The set now holds two kinds of question. A person wrote the sentence of one
kind. The other was made by putting a curated value into a curated template,
which is how ninety more came about, five for each of the eighteen types.

Both are the author's language. Neither was written by a model. But they did
not come about the same way, and the difference matters to anyone measuring
with them: the originals are what a person actually asked, and the filled
ones are what the templates can say.

## Decision

    data/originals/tokyo/NNNN/   the sentence as a person wrote it
    data/questions/tokyo/NNNN/   a template with values put into it

Same shape in both: `_question`, `_template`, `type`, `_source`, and one file
per slot. The numbering restarts, because they are two collections and a
question is named by both.

`_source` in the filled ones records which template and what the question was
checked against:

    source=filled from a template and the seeds
    template=type_range_count/0001.txt
    checked=tokyo23-260831.osm.pbf md5 44a4ba2182379c147f20a27ad1b513ef,
            osm_base 2026-08-30T23:50:59Z

The data is named because "this question has an answer" is only true of some
particular data. The same check against a year-old server disagreed: a place
that resolved then does not resolve now, and one that resolves now was a
different feature then.

## What is not written

The answer. The checks in ADR 0007 found, for each of these ninety, that
there is something to find; for `existence` they found whether it is yes or
no, and for the two sensitivity types they found both counts. None of that is
stored. The set holds questions, and a question that carries its own answer
is no longer a question.

The review file `tmp/checks/selected.md` keeps those notes, and is ignored.

## Consequence

131 questions: 41 written, 90 filled. Every filled question reproduces from
its own template and slot files, no two are the same sentence, and none
repeats one of the 41.
