# 0002. Templates are filed by type, and the level belongs to the question

Accepted, 2026-09-14. Supersedes the first layout, which is in the history.

## What happened

The templates were first placed under `templates/level_N`, taking each
question's recorded `problem_complexity`. The layout broke on its first
collision. "Which is the nearest {category} to {place}?" appeared in both
level 2 and level 5, from tokyo_0026 and tokyo_0021, which are the same
sentence.

They differ in what fills `place`. 0026 fills it with "the Grand Hyatt Tokyo",
which names one feature. 0021 fills it with "Shibuya Station", which names
five, all railway=station, separable only by operator. The nearest Shinto
shrine is a different answer depending on which, so 0021 is a question about
ambiguity and 0026 is not.

The level is a property of the filled question. A template has no level.

## Decision

`data/templates/type_<type>/NNNN.txt`, numbered sequentially within a type.

Two types were folded in for the same reason:

- `anchor_sensitivity` held a sentence identical to one in
  `nearest_neighbor`. The ambiguity was in the value.
- `distance_definition_sensitivity` held "How far is {target} from {place}?",
  which is a distance question. It becomes a definition-sensitivity item when
  the target is a polygon, where the centroid and the boundary disagree; for
  Yoyogi Park that is 1477.8 metres against 804.2.

`radius_sensitivity` was kept, for the opposite reason. Its sentence names
both radii, so it asks about ambiguity whatever values fill it. The
difference is whether the sentence or the value carries the property.

## Consequence

31 templates in 15 types. Within a type the plain and the operated-by
variants sit next to each other, and `type_distance` runs from vague to
explicit: "How far is X from Y", the same with the operator named, then "the
straight-line distance in metres" in both forms.

Whether a filled question is anchor-sensitive or definition-sensitive is not
recorded anywhere yet. It is a property of the value and needs a home.
