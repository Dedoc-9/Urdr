<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: horizon-bound -->
# `horizon` — design brief (URDRLAT1, T3.32, MMO Stage H)

**Read**: 2026-08-04, the centrality-ordered READ pass — run 2's second blind READ (P7,
`../exe_epistemics/PREDICTIONS.md`), and the first on which the rival bases genuinely
discriminated: B-A′ predicted an envelope, B-B′ an adjudication, and the rows chose. Outcome:
**P7-C-A** — B-A′ right; the cost family's third preregistered instance. Reading grade:
**CONFIRMATION** — the module is what its rows certify. This resolution's second zero-arrival
closed run 2 under the signed continuation rule.

## What it is

**The rollback-horizon reconcile window**: the worst-case reconciliation latency of a client
correction, made a certified hard bound. The OPODIS 2025 insight turned concrete — because this
repo reconciles byte-exactly (`cpredict.reconstruct` lands on the authority bit-for-bit, δ = 0),
the *only* cost of a late input is how far back it rolls, and that is bounded by the snapshot
horizon: `cpredict` localizes the first mispredict boundary k, the rollback depth is n − k, and

- **ADMIT** — depth ≤ H: the reconcile replays at most H boundaries, byte-exact, with op-cost
  bounded by H × per-boundary work (an `opcost` bound; `reconcile_cost` is the exact count of the
  replayed suffix).
- **REFUSE** — depth > H: the misprediction is older than the snapshot window; there is no state to
  roll back to, so it is a typed `HORIZON-REFUSE` — a stale correction is refused, never served
  late.

## The core law (what `horizon-bound` certifies)

The worst-case reconcile latency **equals** the horizon: an admitted correction never replays more
than H boundaries, and `worst_case_window(H) == H` — a tight envelope, not slack. Around it:
`horizon-reconstruct` (depth 0 for a correct prediction; an admitted reconcile equals the
authoritative glide byte-for-byte), `horizon-refuse` (the typed refusal beyond the window), and
`horizon:scenes` (correct / recent / deep pinned to URDRLAT1 digests binding depth and verdict).

## The seam (P7's finding)

**Cost, confirmed — and the family discriminator earned.** The predicate reads a *measured
magnitude* (depth, computed from the reconcile — never claimed) against a *declared ceiling* (H, a
policy number, like `SHARD_BUDGET`): the signature that distinguishes the cost pattern (opcost,
budget, horizon) from admission (jurisdiction, warden — which read state-lawfulness). The refusal
is the envelope's enforcement, exactly as in `opcost.within_budget`. What neither rival named: the
envelope *exists because* reconciliation is byte-exact — δ = 0 collapsed every other cost of
lateness, so the window law rides on the representation seam. And the module **mints nothing**:
pure composition of `cpredict`'s reconcile and `opcost`'s counts — the composition signature, third
sighting.

## does_not_show

Wall-clock of the reconcile (this bounds the WORK; time follows via `bench.py`,
MEASURED-on-named-host). The snapshot STORAGE cost of keeping H states (an operational parameter,
not certified here). Non-monotone or multi-authority corrections (this certifies the
single-authority reconcile `cpredict` covers). Network transport of the late input. And H itself is
a POLICY number — the module enforces a window, it does not derive what H should be.
`integrity ≠ truth`.

## Falsifier

This brief cites `horizon-bound`: the row certifying depth ≤ H on admit and worst-case window == H.
If an admitted reconcile ever replayed more than H boundaries, or the window stopped equalling the
horizon, that row reddens and this brief's central claim dies with it.
