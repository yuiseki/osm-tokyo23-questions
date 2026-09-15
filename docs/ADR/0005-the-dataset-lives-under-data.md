# 0005. The dataset lives under data/, and the sentences are tracked

Accepted, 2026-09-15.

## What happened

The 34 questions the author wrote were decomposed under `tmp/human/`, which
is in `.gitignore`. The templates and the seeds were derived from them and
were tracked; the sentences they were derived from were not. The only copy of
the part a person actually wrote sat outside the repository's history.

At the same time `originals/`, `seeds/` and `templates/` sat at the top level
beside `docs/` and `scripts/`, which are about the dataset rather than part
of it.

## Decision

    data/originals/<region>/<NNNN>/   the questions, one directory each
    data/templates/   templates, in type directories
    data/seeds/       seven slot kinds, one file per value

    docs/             ADRs
    scripts/          anything that reads data/
    tmp/              ignored; scratch only

`data/originals/` is tracked, with a level for the region: the questions
here are Tokyo's, and another city's would sit beside them without renumbering
anything. A question directory holds `_question`, `_source`,
`type`, `level`, a `_template` where one was written, and one file per slot.

## Why the originals are tracked rather than derived

They cannot be derived. `data/templates/` and `data/seeds/` are an
abstraction over them: the templates drop the values and the seeds drop the
sentences, and neither alone reconstructs a question the author wrote. The
check that a template refilled with its own slot files reproduces `_question`
exactly is only possible while the sentence is present.

It is also the provenance. No part of the dataset may be prose written by a
model, and `data/originals/` is where that claim is checkable. `_source`
records how each sentence came to exist; ADR 0006 has the table and the
counts.

## Consequence

359 tracked files under `data/`. The earlier paths, `templates/level_N`,
`seeds/tags/` and the untracked `tmp/human/`, are in the jj history.
