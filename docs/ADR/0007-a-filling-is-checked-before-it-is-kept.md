# 0007. A filling is checked twice, by tag and by query

Accepted, 2026-09-15.

## Context

Filling the templates from the seeds gives 43,257,101 sentences. Nearly all
are nonsense: the opening hours of a railway operator, the total length of a
hotel, how many Starbucks are inside a street. The set wants five questions
per type, so what matters is not how many can be made but which are worth
asking.

## Decision

Two passes, in this order, because the first is free and the second is not.

By tag, from the attributes in the seeds (`scripts/count_combinations.py`):

    the operated-by clause only on a station that has that operator, and it
      governs the place it follows, not every place in the sentence
    inside, and the footprint comparison, only on something with an inside
    the footprint comparison only between two buildings
    a length only of a way
    an attribute question only of a place carrying that tag
    a brand only with a category that contains it
    two brands compared only against the same kind of thing
    two slots of one kind distinct, two radii in order
    singular or plural as the author filled that slot in that sentence
    "within 250 metres" but "a 250 metre radius"
    a place named JR something not operated by Tokyo Metro

155,224 of 43,257,101 survive, 0.36 per cent.

By query, against overpass.yuiseki.net (`scripts/check_nonzero.py`): does the
question have anything to find. Measured at 0.30 seconds a query, and 71 of
92 sampled questions had something. Only a count is asked for. No answer is
stored: the dataset holds questions.

## The exception

`existence` is the one type where an empty answer is a correct answer. "Is
there a movie theater within 100 metres of Shibuya Station?" is a question
whether or not there is one, and a set of five that are all yes would be a
worse set. The five are chosen to contain both.

Every other type is kept only when non-empty, and the two sensitivity types
want more than that: the counts at the two radii have to differ, or the
question answers itself.

## What the two passes cannot do

Neither says whether a question is worth asking. "How many hotels are inside
Yoyogi Park" passes both and is a strange thing to ask. Reading the fillings
is what caught the ones already fixed, and a person reading the final
seventy-five is the last pass.

## What the check was run against, and a problem with it

Everything above was measured on overpass.yuiseki.net, whose data is stamped
`2025-09-14T23:59:55Z`. That is a year old. It was reported by another
session working on a 2026-08-31 extract, and confirmed here from the server's
own `osm3s.timestamp_osm_base` and against api.openstreetmap.org:

    way/469925865      410 Gone     the only id in the Yoyogi Park seed
    relation/19862716  200          what Yoyogi Park is now, name:en intact
    node/6283002002    410 Gone     one of the six in the Shinjuku Station seed
    node/2389061846    200          Shinjuku, and it now carries
                                    operator:en=Odakyu Electric Railway

So the seeds' `osm=`, `features=`, `operators=` and `attributes=` lines
describe the world of a year ago. Two of the 216 ids no longer exist, one
station has five features rather than six, and at least one operator string
the data now carries is missing from `data/seeds/operator/` because it was
not there to be found.

None of this touches a question's prose, and the dataset holds no answers, so
nothing recorded here is wrong about the questions themselves. What it
touches is the second pass: a filling kept because it had something to find
may have nothing to find now, and the reverse.

Which data the check should run against is not decided here.

## The extract itself had a hole, and total counts did not show it

Reported by the session building the extract, and confirmed here. Its
twenty-three-ward mask was cut from boundaries fetched a year earlier, so a
boundary way created the day before the planet file fell outside the mask.
`complete_ways` keeps a way only if one of its nodes is inside, so Setagaya's
boundary came through with 134 of its 135 ways, its ring does not close, and
Overpass builds no area for it.

    area["name"="世田谷区"]   returns nothing, and raises no error

Tested here against the local import: twenty-two of the twenty-three wards
answer, Setagaya does not. Nothing else showed it. File size, node counts,
and the 216 osm ids in the seeds all looked right.

The lesson is not about that one ward. A question of the form "which X in
Y ward" would simply have come back empty for one ward in twenty-three, and
the check in this file would have dropped those fillings as uninteresting
rather than as broken. An empty answer and a missing area are the same shape
from here.

So the check now asks, before anything else, whether every area seed produces
an area. Totals cannot be trusted to reveal a hole; only asking each thing
the questions will ask can.

The extract is being rebuilt. Everything measured against the first one is
provisional.
