<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: recirc-law -->
# `recirc` — design brief (URDRRCC1, the Galois-frontier recirculation)

**Read**: 2026-08-04, the centrality-ordered READ pass — P28 of batch 7
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-FLOOR** — "there is no loop": a soundness-of-absence
result, the `ashdepth` inversion (P17) recurring as a second vacuity carrier. Reading grade:
**CONFIRMATION**.

## What it is

**The rung that refutes its own elegant proposal — twice.** The proposal: rather than queueing
discarded states back with generation counters, recirculate them structurally as a fixed-point
iteration on the Galois frontier, `P_{t+1} = P_t ∪ (γ_k(α_k(P_t)) \ P_t)`. The idea is genuinely
elegant and needs no counters. Two claims were attached to it, and **both invert under measurement** —
which is the whole content of the rung, because one of them would have made the system *less* safe
while looking more principled.

## The core law (what `recirc-law` certifies)

**There is no loop.** (1) The union is redundant because the abstraction is extensive, so the step is
just `γ∘α` — a CLOSURE OPERATOR, hence IDEMPOTENT by the adjunction (a theorem, not a property of the
data). The Kleene iteration reaches its fixed point in AT MOST ONE STEP for every input (measured step
counts 1,1,1,1,1,1,0,0), so the count is a CONSTANT and cannot encode a per-capture defect —
CONSEQUENCE 1 refuted. (2) The closure is COARSER than its input, so distinct captures COLLAPSE onto a
shared fixed point (400 raw sets → 5 fixed points), and an honest capture collides with a doctored one
that quietly dropped a single obligation — so fixed-point equality is a STRICTLY WEAKER integrity
check than raw equality, raising false negatives on exactly the omission attack `geoquorum` exists to
catch — CONSEQUENCE 2 refuted, and dangerous. The salvage is real: refining the LEVEL when the
iteration stalls is genuinely multi-step, bounded by the level ladder (not the cell count), floored at
`ashdepth`'s k_min and total without a heuristic.

## The seam (P28's finding)

The `ashdepth` pattern (P17) recurring: a handed-down elaboration refuted by measurement, and the
ABSENCE is the sound answer. The correct architecture is STRICTLY FORWARD — the discarded states are a
terminal residue handed once to the semantic layer, never a queue that cycles; `frontier`'s obligation
signature already IS that residue, carried forward under conservation and monotonicity. The "no loop"
answer is made non-vacuous (L61) by MEASURING that closing the loop would HARM — a second vacuity
carrier, v_D=0, not a mint. The unnamed gem is the **dangerous-elegance** observation — the
more-principled-looking check is a regression — recorded as a candidate to WATCH, not minted: it is
the arc's measurement-refutes-seduction method, not a distinct seam family (L3).

## does_not_show

That the refinement ladder's step count is a USEFUL quality metric (it is well-defined and bounded,
which is strictly less than useful); anything about float capture (this operates on the already
quantized pair domain); that raw-lattice equality is itself sufficient for fraud detection (it is not
— that is `geoquorum`; the point here is only that the closure is WEAKER than it); cross-placement.
`integrity ≠ truth`.

## Falsifier

This brief cites `recirc-law`: extensive + monotone + IDEMPOTENT (one-step convergence), and the
collapse (distinct captures share a fixed point, honest collides with doctored). If the closure ever
took more than one Kleene step, or the fixed point distinguished the honest/doctored pair raw equality
conflates were the danger absent, that row reddens and this brief's central claim dies with it.
