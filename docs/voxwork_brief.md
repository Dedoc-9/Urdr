<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxwork-floor -->

# `voxwork` (URDRVXO1) — design brief

*The performance arc opens with a ruler and nothing else. A speedup measured against a ruler that
arrived in the same commit is a speedup measured against itself.*

## Observe

The correctness arc closed at `voxcam`. This is the first rung of a different arc whose whole law is
one line — **same exact observable, less work** — and this rung does the first half only.

The instrument is the seventh transcription of the committed rasteriser loop with a counter beside
every branch. It is bound in the strongest direction available: its colour and depth buffers must
equal `voxref.render`'s **as lists**, element for element, on every declared frame. Not as digests,
which would let two different pictures collide; not on one frame, which would let a transcription
drift where the trace does not go.

| | |
|---|---|
| pixels walked | 664553 |
| output pixels | 55296 |
| overdraw | **12×** |

And the fate of a walked pixel is a partition, asserted per frame so that no unit of work is
uncounted or counted twice:

| fate | count | share | dies to |
|---|---|---|---|
| outside the triangle | 419370 | 63% | the three edge tests |
| covered but beaten | 179290 | 27% | the depth compare |
| written | 65893 | 10% | — |

## Orient

**Nine pixels in ten are walked to produce nothing, and the two losses are of different kinds.** That
second clause is the whole reason the partition exists rather than a single wasted-work number.
Coverage failure is a question about a *triangle's shape*, and a question about a shape is answerable
for a whole tile at once. Depth failure is a question about *what else is in front*, and that is
answerable for a whole primitive at once. Different mechanisms, different remedies, different arms —
so they are counted apart and stay apart, because the moment they are summed the arc loses the
ability to say which arm bought what.

**The arithmetic is modelled and the model is checked against execution.** 36 multiplies per quad in
the Q16 basis multiply, 8 more and 8 divides in the projection's screen divide, 4 per triangle in the
signed area, six per walked pixel in the three edge functions, 3 multiplies and one divide per
covered pixel in the depth interpolation. 6633411 multiplies, 506663 divides. The closed form must
*equal* the count taken from the run — a cost model only ever compared to itself is a formula, and
this tree has been burned by one before.

**One law reddened before it shipped, and the correction is the useful part.** The first draft
asserted that the edge functions are three quarters of the multiplies. They are 71%, not 76%, and the
law refused the claim rather than the claim being softened to fit. What that exposes is worth more
than the original sentence: the setup is 1910544 multiplies, **more than a fifth of the total**, and
1387584 of those are the basis multiply paid for *every* quad including the 5859 the near test then
throws away — before anything is known about any of them. A performance arc that assumed the inner
loop was everything would aim every arm at it and leave a fifth of the work untouched. Both bounds
are now asserted and both can redden.

## Decide

**No wall clock appears anywhere in this rung, and that is enforced rather than promised.** A timing
assertion inside a deterministic gate is nondeterministic; it flakes, and then it gets loosened until
it cannot fail. This tree's standing rule is counts on-gate and wall-clock off, in a committed record
from a named host — `sealframe`'s own bridge, and `attest` and `probelog` are what it looks like when
honoured. `no_wall_clock_enters_this_rung` reads this module's own AST and refuses a timing import,
so a performance arc cannot smuggle a stopwatch into the gate one rung at a time, and the detector is
planted against a source that *does* import one, because a law with an empty live population is
indistinguishable from a law that cannot look.

`does_not_show`: **nothing about time** — these are exact integer operation counts, and an operation
count is not a duration, because a division and an addition are one operation each and are not one
cost each. Nothing about memory traffic or cache behaviour, which are properties of a machine and a
layout and this rung measures neither. **That any of this work is removable** — naming waste is not
retiring it, and a bound on what a cheaper test could save is a different rung with an arm in it. And
nothing is altered: `voxref` is untouched and `O_t` is byte-identical with the observer active, which
is the only reason any number here means anything.

## Act

`voxwork-floor` holds the census, the partition and the overdraw, `voxwork-model` the two model-equals-
execution checks and the arithmetic split, `voxwork-clock` the stopwatch refusal and its plant,
`voxwork-selftest` the record plants.

The walk model is the part worth pointing at. It derives the walk from the projected bounding boxes
*without running the inner loop at all*, and is then required to equal the counted walk on every
frame. That is the check a census would fail if it had quietly started counting something else, and
it is the reason the floor can be used as a ruler by rungs that have not read its source.

The falsifier naming this brief: `voxwork-floor` reddens if the ruler ever moves the buffers it
measures, if the three fates stop summing to the walk on any frame, or if the reference stops walking
ten times its own output — the last being the day this floor must be re-read rather than quoted.
