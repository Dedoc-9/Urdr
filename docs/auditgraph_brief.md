<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: auditgraph-law -->
# `auditgraph` — design brief (URDRAGR1)

**Read**: 2026-08-04, the centrality-ordered READ pass — P18 of batch 4
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-PRICE** — the κ bound central, the challenger's
sharper pricing winning the joint. Reading grade: **CONFIRMATION**.

## What it is

**The exclusion price** — what `splitview` assumed away, and why its cheapest recommendation is the
wrong one to ship. `splitview` decided undetected equivocation is possible exactly when the gossip
graph is disconnected, that the minimum edge count for a guarantee is k−1, and therefore a spanning
tree suffices. Every statement is true — and the last only against an adversary with no membership
control. The gossip graph there is **exogenous**: given, and the server plays against it. In an MMO
the server *builds* the graph — matchmaking is the attack surface.

## The core law (what `auditgraph-law` certifies)

An official server decides who shares a session; if it also chooses the audit topology it
constructs a disconnection rather than hoping for one — over the Bell(k) session partitions,
Bell(k)−1 leave the audit graph disconnected and the server picks. **Committing the topology to
client identity** collapses that to 0 of 1, leaving only ADMISSION. And the **exclusion price
theorem**: under a committed topology, the price of undetected equivocation is exactly **κ(T), the
vertex connectivity** — decided by *running the attack* (enumerate every client subset the server
might exclude, ask whether the survivors split) and comparing against κ by MAX-FLOW under Menger's
theorem, across all 771 connected labelled graphs to order 5, 0 exceptions. The corollary reverses
`splitview`: the graphs the server can never split at any exclusion budget are exactly the complete
ones — a spanning tree costs 1 exclusion, a ring 2, all-pairs infinity. Redundant gossip's value is
*invisible* until the adversary controls membership.

## The recorded correction (self-applied L23)

The first version of the central sentence was a lie, recorded rather than repaired in silence: it
compared `exclusion_price` against `vertex_connectivity` — the same loop over the same subsets
calling the same `components`, separated only by a guard that cannot change the answer — and sold
that as "two computations agreeing." It shipped three times. It was refuted **by mutation**:
corrupt `components` and the old census still reports 0 exceptions, merely shrinking its own
denominator, while the Menger census reports 181. `cross_check_is_falsifiable` now runs exactly
that mutation on every gate pass. And the fix reached only the numerator: `connected_graphs` — the
*denominator* — was built from the same flood fill, so a fault that narrowed the world without
causing disagreements would still have passed; `is_connected` is now cross-checked against max-flow
(1099/1099), and `validate_graph` turns an out-of-range endpoint or self-loop from a silently
dropped edge into a typed refusal.

## The seam (P18's finding)

Cost — the price pattern on equivocation — with a topology theorem (all-pairs uniquely
unbreakable) as its structural corollary. The deeper resonance the checkpoint recorded: the
denominator defect is the **vacuity law's fifth carrier** — a narrowed census reading as clean is
an empty answer wearing a measurement's clothes, exactly the failure `ashdepth` named.

## does_not_show

Dishonest content of an admitted session (κ prices *exclusion*, never truthfulness — a live server
that lies is `splitview`'s and `liveness`'s territory); the cost of *building* all-pairs gossip
(bandwidth, `bench.py`); graphs beyond order 5 (the censuses are exhaustive only to there).
`integrity ≠ truth`.

## Falsifier

This brief cites `auditgraph-law`: κ = exclusion price, decided by attack vs Menger max-flow. If the
attack census and the max-flow census ever disagreed on a graph, that row reddens and this brief's
central claim dies with it.
