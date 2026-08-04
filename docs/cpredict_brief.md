<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: cpredict-equivalence -->
# `cpredict` — design brief (URDRCPRED1, T3.20)

**Read**: 2026-08-04, the centrality-ordered READ pass — P19 of batch 4
(`../exe_epistemics/PREDICTIONS.md`), declared **NON-SCORING**: `horizon`'s read (P7) had already
exposed this module's reconcile/reconstruct interface and the δ = 0 byte-exact property, so its
core law was known before the seal and it moves no tournament weights. Reading grade:
**CONFIRMATION**.

## What it is

**Continuous client-prediction reconcile.** A client predicts a movement transcript; the authority
disagrees from some boundary. `cpredict` localizes the *first* mispredict boundary k and replays
only the suffix, resuming from the last agreed pose — memoryless, byte-exact — rather than
re-simulating from the start. It is the reconcile half of the netcode prediction loop, on terrain.

## The core law (what the rows certify)

`cpredict-equivalence`: the reconstructed authoritative trajectory equals the ground-truth glide
bit-for-bit (δ = 0 — the immersion-consistency distance is exactly zero, which is what makes the
rollback cost *purely* a function of depth, the property `horizon` builds its window on).
`cpredict-refines`: reconcile localizes the first mispredict boundary and the resumed suffix
refines the authority; the witness binds the reconstruction; floored fractional resume poses are
handled (the `splice` resume law). `cpredict-refusal` is the typed domain battery.

## The seam (P19's finding — recorded, not scored)

Representation with a measured localization: the reconcile is an identity law (reconstruct == glide)
whose *mechanism* is a boundary measurement (where prediction and authority first diverge). It is
`drive`'s transcript identity plus a diff — the composition that `horizon` and `splice` both build
on. Read here only to complete the brief coverage; the epistemics abstain because the law was
disclosed.

## does_not_show

Wall-clock of the reconcile (that is `horizon`'s op-cost bound + `bench.py`); multi-authority or
non-monotone corrections (single-authority reconcile only); the network transport of the late
input. `integrity ≠ truth`.

## Falsifier

This brief cites `cpredict-equivalence`: reconstruct == authoritative glide, δ = 0. If a
reconstructed trajectory ever diverged from the ground-truth fold, that row reddens and this
brief's central claim dies with it.
