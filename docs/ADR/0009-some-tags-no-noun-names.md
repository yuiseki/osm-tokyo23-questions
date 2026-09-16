# 0009. Some tags have no noun, and those questions are not written

Accepted, 2026-09-16.

## What happened

Twenty-three OpenStreetMap tags were picked up for `data/seeds/category` on
the grounds that three models fail to name them while writing SQL, so the
collection would gain vocabulary where models are weak. Each needed the noun
a person would use. Most had one. `tourism=information` did not, and the
attempt to find one is the reason this file exists.

It was the most promising of the twenty-three. Three models, asked to write
SQL for questions about it, named the tag correctly zero times out of
forty-eight. It has 5,181 features in the extract, so questions about it would
have answers everywhere.

The generator had called it "informations", which is not English. Wikidata has
no item whose `P1282` is this tag, so no label could be read out. Working from
the OSM wiki, "tourist information" was proposed, then "tourist information
centers" as better English, then "tourist information board".

Each of those is a real thing and none of them is the tag.

## What the tag holds

    information=board          2,566   49.5%
    information=map            1,466   28.3%
    information=guidepost        881   17.0%
    no information tag           135    2.6%
    information=office            78     1.5%
    information=route_marker      33     0.6%
    the rest                      22     0.4%

Half are boards. A quarter are maps on a post. A sixth are signposts at a
path junction. Seventy-eight, one and a half per cent, are the staffed desk
that an English speaker means by "tourist information centre".

## Why no noun exists

Not because English is short of words. Because the tag is a bag of unlike
things, held together by what they are for rather than by what they are.
`tourism=information` means "this thing informs a visitor", and English has
no count noun for that. Every candidate names one member and excludes the
rest.

The consequence is not stylistic. "How many tourist information centres are
within 500 metres of Tokyo Station" answered against `tourism=information`
returns a count of signposts, and the question and its answer are about
different things. A collection whose premise is that a question is what a
person would say cannot carry it, because the person saying it would be
misunderstood.

## Decision

`tourism=information` is skipped, and the worksheet at
`data/synthetic/NOUNS.txt` records the reason beside it rather than leaving
it looking unfinished.

More generally: where the features under one tag are unlike each other, no
noun names them, and a noun forced on to them writes a question that does not
mean what it counts. Such a tag is skipped. The test is not whether a noun can
be found but whether the noun covers the tag, and the way to run it is to
count the sub-tags before choosing the word.

## What is not being said

That the tag is badly designed. It is a perfectly good tag for the purpose
`tourism=information` serves, which is to gather everything a renderer might
draw an i on. The mismatch is between that purpose and the way a person
counts things in a sentence.

That the tag is useless here. It is the opposite, and this is worth saying
plainly because it was nearly thrown away with the noun. A tag that cannot be
named in one word, and whose meaning lives in a second tag beneath it, is a
good test of whether a model knows OpenStreetMap rather than knowing English.
Asking a model to count the information boards near a station requires it to
produce `tourism=information` and `information=board` together, which is a
two-level convention with no counterpart in the schema of any other database.
Nothing in the present collection tests that. It belongs in a question written
for it, and the questions that would have been generated from a wrong noun are
not it.

The count above is the material: boards, maps, guideposts and offices are four
tags with four clean nouns, and each is answerable in this extract.
