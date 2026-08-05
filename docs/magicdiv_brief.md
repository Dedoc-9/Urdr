<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: magicdiv-law -->
# `magicdiv` — design brief (URDRMAG1, division by an invariant constant)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P45 of batch 13
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**, the author's leading credence (48) correct.
FP-ROW status: **NON-DISCRIMINATING** (role-reading and row-reading both said C-EQ). Reading grade:
**CONFIRMATION**.

## What it is

**Replacing a division with a multiply and a shift, and proving the replacement is not an
approximation.** Division is the one arithmetic operation this arc keeps out of every authority path,
because integer division semantics differ between languages for negative operands and because a
rounding question anywhere in a certified computation is a rounding question everywhere downstream.
When the divisor is a compile-time invariant, the division can be replaced — and the replacement must
be proven identical, not merely close.

## The core law (what `magicdiv-law` certifies)

**`floor(n/d) == (m*n) >> s`, DECIDED EXHAUSTIVELY over the whole word — every divisor × every
dividend, 0 failures.** A decided finite statement, not a sampled sweep: the claim is not that the
identity held on the cases anyone thought to try, but that the space was enumerated and contains no
counterexample. The row also grades the **handed-down corollaries rather than repeating them** — the
Hausdorff-dimension claim that arrived with the technique is **REFUTED by definition**, not inherited.

`magicdiv-selftest` is where the exhaustion earns its cost: the floor-instead-of-ceil multiplier
**fails on some divisors while remaining CORRECT for powers of two**. That subtlety is the point — a
sampled check on easy divisors would have passed the defective multiplier, and only exhaustion refuses
it. The plant is chosen to be exactly the one sampling would miss.

## The seam (P45's finding)

**Enumerate-don't-sample, on its fourth carrier.** `voxlat` decided its overflow bound exhaustively
rather than estimating, `cayley` swept every configuration, `divergence` enumerated the maximum
because a sampled mean sits strictly below the attained worst case, and `magicdiv` decides the whole
word. Four modules, one discipline: where the space is finite, enumerate it, and say "decided" instead
of "tested". L20 (`sample ≠ universal`) turned into code four times. The second habit visible here is
**grading what you inherit** — the Hausdorff claim came with the technique and was refuted rather than
repeated, which is the same move `divergence` made against the rate metric and `horn` made against the
continuous bound.

## does_not_show

Speed — the identity is MEASURED, the performance benefit is not gated here (wall-clock lives in
`bench.py`, host-tagged); non-invariant divisors (the whole construction assumes the divisor is fixed);
word sizes other than the one enumerated (the decision is exhaustive over THAT word, and a different
width is a different finite space needing its own enumeration); signed-division semantics beyond the
floor convention certified. A decided identity on this word is not a claim about arithmetic in general.
`integrity ≠ truth`.

## Falsifier

This brief cites `magicdiv-law`: `floor(n/d) == (m*n) >> s` decided exhaustively over the whole word,
every divisor × every dividend, 0 failures. If a single (divisor, dividend) pair ever diverged — or if
the enumeration were narrowed to a sample, which is the same defect wearing better clothes — that row
reddens and this brief's central claim dies with it.
