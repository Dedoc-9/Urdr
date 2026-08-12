<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: confound-schedule -->
# `confound` — design brief (URDRCNF1)

## The log refuted the harness with the harness's own numbers

The first admissible rollback log came back from the named host and said `narrowed` was faster than
`moulded` in **23 of 28 cells**, median 500 ns.

Read what the harness times:

```python
rec  = MS.record_for(rep, ...)      # `narrowed` = `moulded` + a widths tuple
flat = rec if rep == "flat" else MD.to_vouch(world, (rec[0], rec[1], rec[2]))
```

Both non-flat arms go through `to_vouch`, and the widths `narrowed` stores are **never read** during
replay. `narrowed` executes a strict superset of `moulded`'s timed instructions. A representation
doing more work cannot be faster — so the log was not measuring the representation.

## It was measuring when the cell ran

`cells()` iterated representation-outermost. In the run that produced the log:

| representation | run positions |
|---|---|
| `flat` | 0–27 |
| `moulded` | 28–55 |
| `narrowed` | 56–83 |

Every `flat` sample preceded every `moulded` sample preceded every `narrowed` sample, across 16 800
timed operations on a handheld under a turbo power profile. Clock ramp, thermal state and allocator
warmth all drift monotonically through a run like that, and the treatment axis was aligned with the
drift. *"Narrowed is fastest"* and *"narrowed ran last"* were the same measurement, and no number of
extra iterations would have separated them.

> **A factor perfectly correlated with run position is not measured, it is confounded.**

## Three verdicts, because they are three findings

`CONFOUNDED` — the levels are disjoint contiguous blocks; the factor *is* run position.
`SKEWED` — interleaved, but some level still sits systematically early or late.
`BALANCED` — every level's mean run position is within tolerance of the run's midpoint.

A detector with only the block test would call a merely front-loaded factor balanced, which is why
`SKEWED` is planted separately.

## The repair is a schedule, not a caveat

Cells are visited at `(i × STRIDE) mod n`. Co-primality makes that a **permutation by
construction**, so no cell is dropped or run twice — a guarantee a hand-written interleave does not
have, and a stride sharing a factor refuses rather than silently producing a short run.

`STRIDE = 25` is a **choice re-derived by search**: every co-prime stride is scored against a
criterion fixed in advance — minimise the worst per-axis deviation of a level's mean run position
from the midpoint — and the smallest stride attaining the floor is taken. Six tie. The falsifier
redoes the search rather than trusting the number, so a future plan that makes another stride better
turns this red with the measurement already in hand.

Randomisation would balance just as well and is **refused**: determinism is the floor, and a seed is
one more thing a result can depend on. Asserted on the source — `random` and `secrets` are not
imported.

`TOLERANCE = 0.05` is non-vacuous in both directions. The structural floor for this plan is 0.0357
(seven depth levels do not tile 84 positions evenly), so a tighter bound would refuse every possible
schedule; the shipped order's deviation was 0.333, so a looser one would admit the defect the module
exists to catch.

## A cell is not an experiment

`depth` is what the harness *asks* for. The replay walk saturates against the world's own length, so
the ticks it actually performs stop rising:

| workload | ticks | depths that produce them |
|---|---|---|
| `all_airborne` | 2 | 2, 4, 8, 16, 32, 64 |
| `all_grounded` | 11 | 16, 32, 64 |
| `alternating` | 11 | 16, 32, 64 |
| `frequent_landing` | 12 | 16, 32, 64 |

**28 cells, 17 distinct, 11 duplicates.** Any count over those cells carries a denominator that is
39% copies — L44 with the numerator disguised as the axis. The repair is to carry the work beside
the request: every row now names `depth`, `ticks` and its run position `pos`, so saturation and
ordering are visible in the log rather than deducible from a docstring.

## `does_not_show`

**Balance is not independence.** Spreading a factor across the run removes the *correlation* between
treatment and position; it does not remove position as a source of variance, and it cannot detect a
drift that is periodic at the stride.

This module grades the **schedule**, never the numbers — it makes no timing claim at all. And it
reads the plan's axes as *data*, so a factor nobody put in the plan is invisible: a harness
confounded with something it never recorded reads `BALANCED` and is not.

## Grade

**MEASURED** — every axis reads `BALANCED` under the pinned schedule; the shipped order reads
`CONFOUNDED` with spans checked as exact thirds; the stride's optimality is re-derived by search;
every cell is visited exactly once; the saturation is counted exactly. **DECLARED** — the tolerance,
the stride, and the axis list.
