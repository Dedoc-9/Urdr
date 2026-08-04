<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: geoquorum-law -->
# `geoquorum` — design brief (URDRGEO1, S4)

**Read**: 2026-08-04, the centrality-ordered READ pass — P21 of batch 5
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-SPLIT** — the coverage/integrity distinction is
the law, with a decided quorum theorem under it. Reading grade: **CONFIRMATION**.

## What it is

**Adversarial geometry submission**: admitting user-authored world geometry against evidence the
submitter does not control. `voxlat` makes quantization canonical and a divergence bound would
bound how far a rendered splat sits from its collision lattice — but both defend against ERROR, not
INTENT, and the reason is exact: **a submitter who thins a wall in the splat and derives the
lattice from the doctored splat produces a pair whose internal divergence is zero.** Both are
wrong; they agree perfectly. `divergence_is_blind` measures exactly that — self-consistency is the
one property a liar can always supply, so no per-submission bound can separate honest from
doctored.

## The core law (what `geoquorum-law` certifies)

The only evidence a liar does not control is **other people's captures of the same place** —
`oobprior`'s structurally-excluded cohort, applied to geometry (blocks identified by Morton prefix
via `voxlat`'s lattice, so "the same place" is an exact integer predicate, not a tolerance). The
**quorum theorem, decided**: occupancy is admitted by strict majority; for a cohort of k with c
colluding, consensus flips exactly at **c ≥ ceil(k/2)** — enumerated over every (k, c) with k ≤ 9,
not derived (a first draft asserted floor(k/2)+1 and the enumeration refused it). Operational
corollary: **an even cohort buys nothing** (cohort 4 has exactly cohort 3's resistance), so cohorts
should be odd. A lone liar flips nothing at any cohort of 3+, and at `MIN_COHORT = 5` cannot frame
an honest contributor either — the module's own non-vacuity floor.

## The two refusals (P21's finding)

The law is a *distinction*, not a single predicate: **UNAVAILABLE** (coverage — too few observers
to adjudicate) versus **FAILED** (integrity — the cohort adjudicated and the submission lost). This
is the discriminability-of-refusal — *why* a refusal fired, absence versus contradiction — the same
THIN-vs-DEVIATE split `cohort` cited one layer up. Recorded as a candidate axis to watch; both
bases classified it as admission with a typed sub-reason, so no new family minted (L3). It is also
L61's seventh carrier: MIN_COHORT is a non-vacuity precondition, and the resolution read
non-starved.

## does_not_show

Whether an admitted geometry is *correct* (the cohort adjudicates agreement, never ground truth —
a whole cohort can be wrong together); cohorts beyond k = 9 (the theorem is exhaustive only to
there); the recruitment policy (who is in the cohort — the honest-exclusion structure is
`oobprior`'s, the policy operational). `integrity ≠ truth`.

## Falsifier

This brief cites `geoquorum-law`: divergence-is-blind + the enumerated ceil(k/2) quorum. If a
per-submission bound ever separated the honest and doctored pairs, or the flip threshold disagreed
with the enumeration on some (k, c), that row reddens and this brief's central claim dies with it.
