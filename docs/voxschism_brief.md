<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxschism-selection -->

# `voxschism` (URDRVXX1) — design brief

*The populations are real and no free signal selects them.*

## Observe

The proposal under test is an architecture, not an optimisation: stop making one strategy universally
better, let several **specialise against each other's failure modes**, and let measured local
conditions decide which one runs. `voxfriction`'s sharp phase boundary at four owners is what makes
that idea worth testing here rather than merely restating.

This rung is a **census** and builds no competing implementation, because the question comes first:

> Does the workload partition into populations where different algorithms have different positive net
> margins — and can anything cheap tell which population a tile is in?

Four strategies are costed on every one of the 1,728 tiles of the lattice. The setup every strategy
pays identically — 4,625,280 operations of projection and per-triangle constants — is excluded, so it
cannot flatten the comparison toward zero.

| strategy | total | tiles it would have won |
|---|---|---|
| `reference` (untiled, attributed per tile) | 7,496,434 | 1,344 |
| `normal` (tiled bin raster) | 17,664,724 | **0** |
| `steno1` (certificate at one owner only) | 14,655,516 | 349 — *every one with exactly one owner* |
| `stenoN` (certificate at any owner count) | 14,411,893 | 35 — *every one with two or three* |

The attribution is a partition, not an estimate: each walked pixel of a triangle's own bounding box
belongs to exactly one tile, and 7,496,434 + 4,625,280 = 12,121,714, the committed reference exactly.

## Orient

**Yes on the populations.** Three strategies win somewhere and their winning sets are *disjoint by
owner count*. The differentiation the architecture predicts is visible and measured.

**And `normal` wins zero tiles of 1,728.** Not merely dominated on the total, which `voxbreak` already
showed — never the best strategy for a single tile anywhere. That is the mechanism behind the
scaffolding tax: it is not an overhead on a good idea, it is the cost of a traversal that is never the
right answer.

**No on the selection, and the number is exactly zero.** A hindsight oracle picking the winner per
tile costs 6,163,028 against the reference's 7,496,434 inner — with the common setup, **10,788,308
against 12,121,714, eleven per cent under**, the first arrangement in this arc to get under the
reference at all. But the oracle *reads the outcome*. Replace it with the best fixed rule per group:

| signal | groups | best-fixed total | margin captured |
|---|---|---|---|
| owner cardinality | 7 | 7,496,434 | **zero** |
| longest same-owner run | 4 | 7,496,434 | **zero** |
| both, bucketed | 16 | 7,496,434 | **zero** |
| both, exact and unbucketed | 68 | 7,496,434 | **zero** |
| *`frame` index* (**plant**, not a signal) | *323* | *7,215,958* | *+280,476* |

In every group of every partition, at every resolution, the best fixed strategy is `reference`.

**And the mechanism is visible inside the best population there is.** Among the 571 one-owner tiles,
`steno1` wins 349 and wins them by 1,235,531 — then loses the other 222 by **1,700,567**, net
**−465,036**. A certificate that fails does not merely forgo its saving: it pays the read, the encode,
the verify and its own owner-only raster, and *then* pays the full tile anyway. Each losing tile costs
about twice what each winning tile saves. **The signal is not weak; the population it identifies is
unprofitable**, and no sharper reading of the same signal can repair that.

**The zero is a measurement and not an inability**, and the `frame` row is the plant that proves it.
Handed the frame index — not a property of a tile at all, but a name for which picture is being drawn
— the same machinery finds +280,476 across 323 groups. So the apparatus *can* find margin; it finds
none in the geometry because there is none in the signals available, and it finds some in the frame
index because that is memorising the benchmark. The plant is declared as a plant, never appears in
`SIGNALS`, and no margin is claimed from it.

## Decide

**The architecture's two levels come apart, and separating them is this rung's contribution.**
`voxfriction` established that owner cardinality predicts *whether the certificate fires*, sharply and
usefully. This rung establishes that the same signal carries *no information about which strategy
wins*. Those were one question until they were measured apart, and a regime-selective renderer needs
the second one answered, not the first.

So schismogenesis is supported at the level of populations and refuted at the level of selection — on
this workload, with these four strategies, using the only two signals this architecture makes free.

**No rule is frozen here**, and that is the discipline rather than modesty. The honest sequence is
measure, freeze the population, declare the rule, then test it on a *subsequent* workload. This rung
performs the first two steps and stops, because the third has nothing to declare: every candidate rule
measured to exactly zero.

## Act

`tools/terrain/voxschism.py`, gate stage `voxschism` (four rows: census / populations / selection /
selftest), red-first `tests/test_voxschism.py` (46 falsifiers), and the committed record
`spec/attest/voxref-schism.txt`.

`does_not_show`: nothing about time, and no wall clock enters. Nothing about memory. Not that no
signal exists — four partitions of the two free signals are measured, and a signal nobody has thought
of is not ruled out; what is ruled out is the two this architecture makes free. Not that the four
strategies are the right four. Not that the oracle's eleven per cent is reachable — it is a ceiling,
and the whole point of the rung is that nothing cheap reaches it. And no promotion: `voxref` is
untouched.
