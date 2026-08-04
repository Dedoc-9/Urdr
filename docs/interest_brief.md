<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: interest-soundness -->
# `interest` — design brief (URDRAOI1, T3.21, MMO Stage C opener)

**Read**: 2026-08-04, the centrality-ordered READ pass — P24 of batch 6
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ** (the bases agreed — not a discrimination).
Reading grade: **CONFIRMATION**.

## What it is

**Deterministic Area-of-Interest relevance**: which peers even need to hear about which actors — the
primitive that lets a world scale past one shard (a peer receives only the actors relevant to it,
not all N). The *correctness* of the filter is MEASURED; its *speed* stays NOT_MEASURED. Two phases,
the classic broad/narrow split, both exact and division-free: **narrow** (`aoi_radius` — B is
relevant to A iff Chebyshev distance max(|Δx|, |Δy|) ≤ R, complete and sound) and **broad**
(`aoi_buckets` — the world tiled into 2^k buckets via `bucket = x >> k`, an exact shift; B is a
candidate iff its bucket is in A's 3×3 neighborhood — what an engine actually queries, O(local),
DECLARED as a speed strategy).

## The core law (what `interest-soundness` certifies)

**Broad-phase soundness**: for any actor cloud and any radius R ≤ 2^k, the broad phase *contains*
the narrow phase — `aoi_radius(R) ⊆ aoi_buckets(k)` — so the acceleration never misses a relevant
actor (a missed relevant actor is a desync bug; an extra candidate is only wasted bandwidth the
narrow phase filters). The R ≤ 2^k precondition is load-bearing — at R > 2^k a relevant actor two
buckets away is missed, and the gate plants exactly that defect — and `strict > 0` asserts the broad
phase *strictly* over-approximates somewhere, so the containment is non-vacuous. `interest-exactness`
adds symmetry (B relevant to A iff A to B) and tamper-evidence (the digest binds cloud, parameter,
result).

## The seam (P24's finding)

Sound over-approximation with the narrow phase as the exact filter — the **approximation axis's
third carrier** (`frontier`, `ashdepth`, `interest`), strengthening the already-minted axis rather
than minting it. The bases agreed on C-EQ, so this joint is retirement-neutral. And `strict > 0` is
L61's eighth vacuity carrier: a containment nobody exceeds is empty, so the module asserts it isn't.

## does_not_show

The network delivery (who sends what to whom — the transport, not this set-valued predicate);
predictive / dynamic AoI (leading an actor's motion) and priority / LOD tiers (DECLARED policy — a
static radius filter is certified); continuous sub-cell positions (a glide pose floors into the same
buckets — a clean follow-on); throughput / per-tick cost (NOT_MEASURED — the O(local) claim is a
design target until a sealed bench). `integrity ≠ truth`.

## Falsifier

This brief cites `interest-soundness`: broad ⊇ narrow for R ≤ 2^k, strictly somewhere. If the broad
phase ever missed a relevant actor within the precondition, or the over-approximation went vacuous,
that row reddens and this brief's central claim dies with it.
