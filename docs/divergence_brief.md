<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: divergence-law -->
# `divergence` — design brief (URDRDVG1, S2, the quantization defect in cells)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P41 of batch 11
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 12**. Outcome: **C-FLOOR**; the
author priced C-PRICE 30 against C-FLOOR 28 and **missed by two points**. Reading grade:
**CONFIRMATION**.

## What it is

**The S2 defect measure — and the refutation of the obvious one.** When a real capture is quantized
onto the integer lattice, some cells flip. The natural summary is a RATE (what fraction flipped), and
that is exactly the metric this rung refutes.

## The core law (what `divergence-law` certifies)

**The defect is the LARGEST CONNECTED RUN of flipped cells, because an adversary does not attack the
mean.** The measurement that decides it: **two perturbations with the IDENTICAL rate 2/35 have runs 1
and 2**, and only one of them breaches the wall. A rate cannot distinguish them; a run can.
`divergence-selftest` states the refutation as a plant — **the rate plant assigns the SAME defect to a
perturbation that leaves the wall standing and one that opens it**, which is precisely the failure a
defect measure exists to prevent. It also records why the maximum is ENUMERATED rather than sampled:
**a sampled MEAN run is strictly below the attained worst case**, so sampling would systematically
under-report the quantity that matters.

## The seam (P41's finding)

**A handed-down metric refuted by measurement — the `ashdepth` shape, third carrier.** The prediction
read the module as SUPPLYING a measure (C-PRICE 30) and it does; but what the gate CERTIFIES is that
the intuitive measure is *wrong*, and the run metric is what survives. That is the pattern `ashdepth`
established (a handed-down guard refuted, the vacuity law named) and `recirc` repeated (there is no
loop, and closing it would harm) — measurement overturning an inherited design, with the negative as
the load-bearing content. The two-point miss came from weighing "the module's job" over "what the row
certifies", which is the same error class as P34's and P38's, now on its third instance in four
batches.

The enumerate-don't-sample clause is the quiet inheritance: `voxlat` decided its overflow bound
exhaustively rather than estimating it, `cayley` swept every configuration, and this module enumerates
the maximum rather than sampling a mean. L20 (`sample ≠ universal`) turned into code three times.

## does_not_show

**WHAT RUN A REAL CAPTURE PRODUCES.** The number in the repo bounds a SYNTHETIC wall; it is not a
prediction about a real one, and closing that gap needs a corpus of real scans that does not exist
here — a DATA acquisition problem, not a design one. Also: the physical capture process; whether the
lattice resolution is appropriate; any claim that a small run is *safe* (the run bounds the defect, it
does not price the consequence); wall-clock. A measured worst-case run is a property of this corpus.
`integrity ≠ truth`.

## Falsifier

This brief cites `divergence-law`: the defect measured in cells as the largest connected run, with two
identical-rate perturbations (2/35) having different runs and different wall outcomes. If a rate ever
separated two perturbations the run metric conflated — inverting the refutation — or the enumerated
maximum fell below a sampled mean, that row reddens and this brief's central claim dies with it.
