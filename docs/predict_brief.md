<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: predict-equivalence -->
# `predict` — design brief (URDRPRED1, T3.17, Stage A opener)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P50 of batch 14
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 15**. Outcome: **C-EQ**, matching the
pre-declared **ROW**-reading over the role-reading (C-R), and the leading credence (46) correct.
Reading grade: **CONFIRMATION**.

## What it is

**The client-prediction reconcile primitive — Stage A's opener, and the thing that makes a responsive
client honest.** A client that waits for the server before moving feels broken; a client that moves
first must be corrected when it guesses wrong, and the correction must land on exactly the authority's
answer rather than near it.

## The core law (what `predict-equivalence` certifies)

**Rollback-replay equivalence: `reconstruct == drive(auth)` for every prediction** — reconciling a
mispredicted client reproduces precisely what the authority would have computed, not an approximation
of it. And the sharper half: **the reusable prefix is BIT-IDENTICAL to the authority, so partial
rollback == full re-simulation.** The optimization that makes prediction affordable — replaying only
the suffix after the divergence — is proven to give the same answer as throwing everything away and
re-simulating, which is the claim an implementation is most tempted to assume.

`predict-localize` binds the divergence point rather than leaving it to a heuristic: **reconcile IS
`lockstep.first_desync`**; a correct prediction needs no rollback; and a **different-input,
same-pose** prediction needs none either — the reconcile is POSE-level, not input-level, so a client
that reached the right place by a different route is not punished for it. `predict-refusal` shows the
lazy-reconcile defect (one mispredicted pose too many) diverging, with 3/3 typed `PRED-REFUSE`
(window mismatch · empty window · bad transcript).

## The seam (P50's finding)

**An equivalence wearing an admission's name — FP-ROW's second win.** "Reconcile" sounds like
adjudicating a client's claim, and the pre-declared role-reading said C-R on that basis; the central
row certifies an equality. The disclosure made at the freeze stands: this was a weaker test than P48,
because the row is *named* `predict-equivalence` and the name leaks its class, so the win is recorded
at that reduced weight rather than counted as if the reading had been inferred from harder evidence.

The pose-level clause is the quiet gem. A reconcile that compared INPUTS would refuse a client whose
different keystrokes produced an identical pose — correct by any observable measure — and calling that
a misprediction would be punishing a client for the route rather than the destination. Certifying at
the pose level makes the primitive agnostic to how the client got there, which is exactly the property
`splice`'s memorylessness needs downstream.

## does_not_show

Continuous or fixed-point prediction (that is `cpredict`, the T3.20 sibling); network latency,
bandwidth or the transport that carries the transcript; adversarial clients (a mispredicting client is
WRONG here, not malicious — `warden` polices malice); prediction QUALITY or hit rate (the law is about
reconciling wrongly-predicted state, never about predicting well); wall-clock. An equivalence between
partial rollback and full re-simulation is not a claim that either is fast. `integrity ≠ truth`.

## Falsifier

This brief cites `predict-equivalence`: `reconstruct == drive(auth)` for every prediction, with the
reusable prefix bit-identical to the authority so partial rollback equals full re-simulation. If a
reconciled client ever landed on a state the authority would not have computed, or the reused prefix
diverged by a single byte from a full re-sim, that row reddens and this brief's central claim dies
with it.
