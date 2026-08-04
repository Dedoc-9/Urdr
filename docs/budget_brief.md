<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: budget-descent -->
# `budget` — design brief (URDRBGT1)

**Read**: 2026-08-04, the centrality-ordered READ pass — the **fifth and final brief of the
preregistered run** (P5, `../exe_epistemics/PREDICTIONS.md`), and the first read as a
**basis-discriminating experiment**: two rival seam bases froze conflicting predictions for this
module before it was opened. Outcome: **P5-C-AB** — one central row certifies both predictions
inseparably; the tie class the frozen partition anticipated. Meta: **M-0**. Reading grade:
**CONFIRMATION** — the module is what its rows certify.

## What it is

**The defect budget as a monotone resource**: `jurisdiction`'s composition theorem
(defect(A∪B) ≤ defect(A)+defect(B), decided in cells) turned from passive knowledge into active
enforcement. A shard declares a total budget in CELLS; every admitted capture is charged its
**measured** defect (`charge_for` reads the lattice — its signature admits no parameter through which
a submitted number could enter the accounting); a charge that would take the remainder below zero
raises typed `BUDGET-OVERDRAWN`; a negative charge is refused as a refund (`BUDGET-REFUSE`).

## The core law (what `budget-descent` certifies)

**A well-founded descent on (ℕ, <)** — one law with two inseparable faces: the ledger is monotone
non-increasing by pure integer subtraction with no clamp (never up: a refund is refused at the type
boundary), and it bottoms out in refusal (with unit charges exactly 6 succeed and the 7th raises;
spending exactly to zero is legal, the *next* charge is what refuses; the remainder never goes
negative). The module's own derivation runs monotonicity-first: *a quantity that can go back up has
no termination argument and therefore no bound.* Why that clause is load-bearing is **measured, not
argued** (`budget-selftest`): the refund pump — crediting budget back for clean blocks — lets 4
trivially-clean submissions buy a cost-4 violating block the honest ledger refuses, and the reachable
budget is unbounded in submissions (100 clean reach 100; 1000 reach 1000) against an honest cap of 6.

## The composition law (what `budget-accounting` certifies — the dimension neither basis predicted)

Per-part charging is **sound by subadditivity**: summing per-part costs can only OVER-charge, never
under (55 pairs, 0 under-charges), so a budget that survives per-part accounting has survived the
true total. The conservatism is **priced, not hidden** (2 pairs over-charge by at most 1 cell). And
on **prefix-disjoint** shards the accounting is **exact** — 49 of 55 pairs, 0 exceptions, sum ==
union with no covariance term — which is what makes tiling sound: a city is prefix-partitioned tiles
whose budgets compose to the shard total, the partition forced by the word, the composition by the
law. Two further design-refusals are measured (`budget-selftest`): modality credits admit what the
lattice refuses (a typed word is not a lattice operation), and the privilege lane is a structural
firewall — `authoritative_admit` takes no privilege argument and its verdict is invariant across
every privilege value.

## The seam (P5's finding)

Both rival bases were half right, and the frozen partition recorded the tie honestly: the exhaustion
envelope (B-A's cost recurrence — the pattern now preregistered twice: `opcost`, `budget`) and the
monotone one-way law (B-B's flow reading of "a refund voids the bound") are one descent law. What
neither basis carried is the **composition axis** — soundness/exactness of the accounting under
union — the run's largest unnamed dimension, inherited by the five-joint decision rung as direct
Test-A evidence.

## does_not_show

The budget bounds admitted **defect, never truth** — a within-budget capture can be entirely wrong at
zero cost. `SHARD_BUDGET` is a POLICY number: this rung enforces an allocation, it does not derive
one. Cells are commensurable here by construction; a real deployment may find a jurisdictional cell
and a quantization cell are not equally bad. No bound on an adversary who can influence the DECLARED
budget (a governance surface this rung does not model). Defect sources inherit `jurisdiction`'s and
the quantization model's own declared boundaries. `integrity ≠ truth`.

## Falsifier

This brief cites `budget-descent`: the well-founded-descent row. If a refund stopped refusing, a
charge clamped instead of raising, the 7th unit charge succeeded, or the remainder went negative,
that row reddens and this brief's central claim dies with it.
