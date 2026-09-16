# 0004. Seeds are flat lists of what is said, not a tag hierarchy

Accepted, 2026-09-15. Replaces `seeds/tags/`, which is in the history.

## What was there

The first `seeds/` was a tag hierarchy: `seeds/tags/<key>/<value>/`, with
empty marker files `can_became_category` and `can_became_place` saying which
slot a tag could fill, and brands nested underneath, as
`seeds/tags/amenity/cafe/brands/Starbucks`.

## Why it is gone

Enumerating what the 31 templates actually ask for gives nineteen slot names,
which collapse to eight once the numbering is folded and two aliases are
resolved. `neighbour` is a category and `target` is a place; they have their
own names only because a template needs two of the same kind at once.

| slot | uses |
| --- | --- |
| place | 30 |
| radius | 15 |
| category | 11 |
| operator | 10 |
| brand | 10 |
| neighbour | 7 |
| target | 6 |
| area | 3 |
| count | 2 |

What a slot needs is a way of saying the thing. `place` is filled with "the
Grand Hyatt Tokyo" or "Shibuya Station", not with `tourism=hotel`. The tag
classifies the feature; it is not what appears in the sentence. A hierarchy
over tags therefore answers a question the question set does not ask.

## Decision

    data/seeds/place/     data/seeds/category/  data/seeds/brand/
    data/seeds/operator/  data/seeds/radius/    data/seeds/area/
    data/seeds/count/

One file per value, the filename being the value, the contents empty for now
and available for attributes later.

Singular and plural are separate values. "hotel" and "hotels" both exist
because the templates ask for both: "Which {category} is in the largest
building in {area}?" wants one and "How many {category} are within {radius}
of {place}?" wants the other. Deriving the plural mechanically is not safe;
a rule of that kind produced "clotheses" in a sister repository.

## Content

Seeded from the values the author's own 34 questions use: 15 places, 9
categories, 5 radii, 3 brands, and one each of operator, area and count.

## What is lost

The tag hierarchy could have decided mechanically which template applies to
which value, since only a `railway=station` place can take the operated-by
clause. Nothing records that now. If it is needed, it belongs beside the
value rather than above it.

## Added 2026-09-15, eight places

Chosen by the author to give the value-carried ambiguity of ADR 0002 more
than one example. Until now only "Shibuya Station" had it.

    Shinjuku Station    Asakusa Station     Meguro Station
    Oshiage Station     Otemachi Station
    the University of Tokyo                 Waseda University
    Meiji University

The stations are ones served by several operators, so the name alone does
not pick one feature. The universities have several campuses under one name:
Hongo and Komaba; the main campus, Toyama and Nishi-Waseda; Surugadai,
Izumi and Nakano. "How far is X from the University of Tokyo" therefore has
no single answer, in the same way "Which is the nearest Shinto shrine to
Shibuya Station" has none.

The English is the ordinary English name in each case. The article in "the
University of Tokyo" follows the rule in ADR 0001 that a value is a complete
way of saying the thing.

Whether each name really resolves to more than one feature is not asserted
here. It is a property of the data and has not been measured.

## Added 2026-09-15, six operators

`operated by {operator}` is only answerable when the clause can be matched
against `operator:en`, so these are the strings OpenStreetMap carries, taken
from the stations the place seeds resolve to:

    Tokyo Metro      Toei      Tokyu Railways
    Keiō railway     Keisei Electric Railway
    East Japan Railway Company

With only "East Japan Railway" the clause worked at Shibuya and nowhere else.
Shinjuku and Harajuku carry "East Japan Railway Company", which is the same
company under a different string, and both are now present.

This bends the rule the rest of this file states. "Keiō railway" is how the
data writes it, not how a person writes it, and "Toei" is a prefix rather
than a company name. The clause exists to name a feature that the place name
alone does not pick out, so the string that does the picking is the one that
belongs here. Where the data has only Japanese, as at Asakusa and Otemachi
and Meguro, nothing was added: an English name invented here would name
nothing.

## What a seed file contains, from 2026-09-15

The file name is the value. The contents are what that value names in
OpenStreetMap, as `key=value` lines, so that a generator can tell whether a
combination is possible without asking a server. This is the place the
earlier decision left open: beside the value, not above it.

    data/seeds/category/cafes        amenity=cafe
                                     number=plural
    data/seeds/brand/Starbucks       brand:wikidata=Q37158
                                     amenity=cafe
                                     cuisine=coffee_shop
    data/seeds/place/Shibuya Station features=5
                                     element=node
                                     operators=East Japan Railway; ...
    data/seeds/radius/500 metres     metres=500
    data/seeds/operator/Tokyo Metro  operator:en=Tokyo Metro
    data/seeds/area/Shibuya Ward     boundary=administrative
                                     admin_level=7
                                     name:en=Shibuya

Nothing here is asserted from memory. The category and brand tags are the
conditions `poi-qa/scripts/build_human_qa.py` actually queries; the brand
tags were then counted across Tokyo, 318 Starbucks all `amenity=cafe`
`cuisine=coffee_shop`, 323 McDonald's and 45 Burger King all
`amenity=fast_food` `cuisine=burger`. The place attributes are written by
`scripts/write_place_attributes.py` from a resolution run.

Two things fall out of it. A brand is a subset of a category, so "How many
Starbucks" and "How many cafes" are the same question narrowed, and a
template holding both must not pair a brand with a category that excludes it.
And McDonald's and Burger King are identical in every tag but
`brand:wikidata`, which is what makes tokyo_0011, "which is closer, a
McDonald's or a Burger King", a question about the brand and not about the
kind of shop.

The ward's `name:en` is "Shibuya", not "Shibuya Ward". The value is what a
person says; the tag is what matches.

## Added 2026-09-15, twenty-one brands

Ranked by how many branded features stand within 800 metres of Shibuya,
Shinjuku, Ueno and Asakusa, then filtered by hand. The ranking's own top
entries are share-cycle ports, vending machines and coin car parks, which
carry a brand but are not things anyone asks the number of near a station.

    shop=convenience   FamilyMart  7-Eleven  Lawson  Ministop
    amenity=cafe       Doutor  Tully's Coffee  St. Marc Cafe
    amenity=fast_food  Matsuya  Sukiya  Hidakaya
    amenity=restaurant Saizeriya  Gyu-Kaku
    shop=mobile_phone  SoftBank  NTT Docomo  au
    amenity=bank       Mizuho Bank  MUFG Bank
    amenity=pharmacy   Matsumoto Kiyoshi
    shop=clothes       Uniqlo
    amenity=pub        Torikizoku
    amenity=karaoke_box  Karaoke-kan

The value is the ordinary English spelling, not the tag. OpenStreetMap writes
7-ELEVEN, LAWSON, DOUTOR, ST.MARC CAFÉ, UNIQLO, NTT docomo and Gyū-Kaku;
where the two differ the file carries a `brand=` line with the data's form.
Matching is by `brand:wikidata`, which is the same either way, so the spelling
costs nothing. This is the opposite call from the operators, where the string
was the only thing that could match and the data's form had to win.

With three brands, two of which were identical in every tag but their
wikidata id, "which is closer, a McDonald's or a Burger King" was the only
comparison available. There are now several same-kind pairs to ask it of:
Starbucks against Doutor, Matsuya against Sukiya, FamilyMart against
7-Eleven.

"au" is a brand a person says but a strange word in a sentence. It is kept
because it is what the shops are called, and a question that reads oddly is
for a later decision, not for the seed list.

## Added 2026-09-15, the twenty-three special wards

`area` held one value, so every question naming a ward named Shibuya. All
twenty-three are now present, read from the `admin_level=7` boundaries inside
Tokyo whose Japanese name ends in 区. The other thirty-nine boundaries at that
level are cities, towns and island villages and were not taken.

The value is "Shibuya Ward" because that is what the author asked for when
distinguishing 渋谷区 from 渋谷. OpenStreetMap tags the ward as `Shibuya`,
without the word Ward, so the file carries `name:en=` with the data's form,
and `name:ja=` beside it. Two wards differ in spelling as well: Bunkyō and
Chūō are tagged with macrons and the value drops them, the same call as the
brands.

Toshima is the name of a ward and of an island village. Only the ward is
here, so `osm=relation/1759506` is what disambiguates it, not the name.

## Added 2026-09-15, streets, towers and four plurals

Three types had too few fillings to choose five questions from.
`length_total` had one, because the only street was Shibuya Center-gai.
`area_compare` had thirty, because only six places were tagged as buildings.
`area_rank` had seven, because only seven categories were plural.

    streets     Dogen-zaka Street  Jingu-dori Street  Meiji-dori Avenue
                Asakusa-dori  Kokusai-dori  Shinjuku-dori Avenue
                Sotobori-dori  Sotobori-dori Avenue
    buildings   Azabudai Hills Mori JP Tower  Roppongi Hills Mori Tower
                Midtown Tower  Shinjuku Sumitomo Building
                Shinjuku Nomura Building  Mode Gakuen Cocoon Tower
                Tokyu Kabukicho Tower  Shibuya Scramble Square
    categories  cinemas  churches  Shinto shrines  movie theaters

The last two of the streets are one street under two names. OpenStreetMap has
96 ways as "Sotobori-dori" and 66 as "Sotobori-dori Avenue", so the total
length of Sotobori-dori depends on which name is asked about. That is the
same shape as Shibuya Station naming five stations, carried by a value rather
than by a sentence, and it is in the seeds deliberately. Yasukuni-dori and
Roppongi-dori are split the same way and were left out; one example is
enough to start with.

The plurals were written by the author. ADR 0004 says deriving them
mechanically is not safe and this file does not start doing it.

All eight towers carry `building:levels`, which takes "How many storeys does
X have" from nine fillings to seventeen.

## Added 2026-09-16, twenty categories where models are weak

The nine categories this file started with, and the eighteen values they grew
into, are the words a person reaches for first: cafe, restaurant, hotel, park,
church, cinema, bar, nightclub, convenience store. Three models writing SQL
against a frozen extract name those tags correctly almost every time. The
collection was therefore asking about the part of OpenStreetMap that is
already known.

Twenty tags were added on the opposite criterion, ranked by how often three
models failed to name them: Qwen3.6-35B-A3B, Qwen2.5-Coder-3B and
Qwen2.5-Coder-1.5B, asked for SQL with no examples, over 1,206 questions.

    shop=car_repair      86%   automobile repair shop
    shop=bicycle         85%   bike shop
    shop=hobby           85%   hobby shop
    tourism=museum       85%   museum
    shop=confectionery   80%   confectionery store
    leisure=pitch        79%   sports pitch
    office=courier       78%   courier service
    shop=butcher         78%   butcher shop
    shop=pastry          75%   pastry shop
    office=estate_agent  75%   real estate agent
    shop=video_games     73%   video game store
    leisure=garden       68%   garden
    amenity=parcel_locker 67%  parcel locker
    shop=florist         65%   flower shop
    shop=electronics     63%   consumer electronics store
    shop=shoes           57%   shoe store
    amenity=hospital     33%   hospital
    amenity=college      26%   college
    amenity=parking      15%   parking area
    office=government    86%   government office

The boundary between `shop` and `amenity` and `craft` and `office` is where
they fall off. The value is in the question and the key is not, so a model
reading "bakeries" still has to know it is `shop` and not `amenity`, and the
recorded errors are `shop=bakery` written as `amenity=bakery`,
`shop=hairdresser` as `craft=hairdresser`, `amenity=pharmacy` as
`healthcare=pharmacy`.

Three candidates were dropped. `amenity=atm` and `amenity=shower` are named
correctly 93% and 94% of the time, so they would add words without adding
difficulty, and "shower" names a bathroom fitting as readily as a public one.
`tourism=information` is in ADR 0009: no English noun means that tag.

## Where the nouns came from, and where they did not

Not from the tag value. The sister repository's generator forms its noun by
adding an s to the value, and against these twenty tags that produces
"electronicses", "shoeses", "video gameses", "conveniences", "governments" and
"parkings". The warning earlier in this file, that a mechanical plural gave
"clotheses", has now been earned twice.

Not from a model either. What fills a slot here is written or chosen by a
person and that has not changed.

Candidates were gathered from Wikidata, whose property `P1282` holds the
OpenStreetMap tag a concept corresponds to, written as `shop=bakery` without
the wiki's `Tag:` prefix. The English label of the item carrying that
statement is a noun: `shop=video_games` gives "video game store",
`amenity=parking` gives "parking area", `shop=florist` gives "flower shop",
which is a better answer than "florist" because it is not the tag value.
Twenty of the twenty-three tags had such an item. The OSM wiki's own
`related_terms`, through osm-tag-corpus, filled a little of the rest, though
they are mostly German and Spanish.

The author read the candidates and wrote the two forms. Two did not come from
any lookup: `office=government` has no Wikidata item with that property and
`tourism=information` was abandoned. One was overruled: Wikidata calls
`leisure=pitch` an association football pitch, and the OSM tag is any sport,
so the value is "sports pitch".

Capitalisation was normalised down. The candidates arrived as "Government
office" and the eighteen values already here are lower case except the proper
adjective in "Shinto shrine", and a capital mid-sentence would have been this
collection's only one.

## What this does not yet establish

That the questions these fill have answers. The tags were taken from questions
that are answerable in `tokyo23-260831.osm.pbf`, so each tag has features
within reach of some anchor, and that is not the same as every filling being
non-empty. ADR 0007 is the rule and `scripts/check_nonzero.py` is the check.
