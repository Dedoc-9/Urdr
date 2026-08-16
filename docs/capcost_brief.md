<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: capcost-law -->

# `capcost` (URDRCPC1) — design brief

*The bounded cache's cost surface becomes evidence, and the two instruments agree on one
schedule.*

## Observe

v1.10 bounded the demo's backing cache and the operator swept the cap on the named host:
reach 500 at cap 0, 131072, 65536 and 32768, and a rail-sized control at reach 60. The sweep
produced two findings worth sealing and one methodological catch. First, a cap above the
ladder's live footprint rides FREE — the 131072 record's occupancy, recomputes and evictions
equal the unbounded record's exactly, with timing inside run-to-run noise. Second, a cap
below the footprint is a CLIFF, not a slope — 65536 sits under the 69,661-tile footprint and
turns 57% of frames late with worst rasters over 90 ms; 32768 turns 78% late with
quarter-second worst frames. Third, the catch: the authoring harness's recompute counts
disagreed with the demo's at every regime-B point, because the demo prefills the ladder
before walking while the harness filled on first rebase — FIFO costs are access-order
dependent even though every digest chain stayed identical.

## Orient

Three claims wanted enforcement. The FOOTPRINT is not a label: a record's prefill count must
equal the sum of resident-grid areas derived from its own printed ladder (cells = outer/stride
+ 1, side = 2·cells + 3 — the demo's grid arithmetic, mirrored), so a record produced under a
different schedule cannot wear the demo's name. The REGIME is not a label either: above the
footprint demands zero evictions and recomputes equal to occupancy; below it demands
occupancy pinned at the cap, positive evictions, inflated recomputes and visible degradation
— so a below-footprint execution relabeled with a bigger cap is refused by its own eviction
scars. And the INSTRUMENT must speak the demo's schedule: the harness was taught to prefill
first, its counts then reproduced the host demo's EXACTLY at all five shared points, and the
old no-prefill counts are committed beside them as the negative control that must always
differ.

## Decide

The committed evidence supports "the ceiling must accommodate the ladder's live footprint" —
and nothing stronger. The 2×-footprint rule is a CANDIDATE safety-margin policy on this walk,
not a proven optimum, and the freeze that adopts it belongs to a later rung with its own
numbers. Reach 60's below-footprint behavior is committed as container counts only (cap
16384, regime B as predicted); its host timing, like the unswept caps, stays unmeasured in
writing.

## Act

`capcost-records` re-reads the six pins, re-derives every footprint and compares every chain
to the committed oracles; `capcost-law` holds the two-regime and one-schedule laws and
matches the pinned table; `capcost-selftest` proves seven plants bite. The falsifier naming
this brief: relabel a below-footprint record with an above-footprint cap, or present the
no-prefill counts as the demo's, and `capcost-law`'s admission refuses before any law is
spoken.
