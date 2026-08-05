<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# The unanchored Ψ floor — a protocol for a session that has not seen Ψ₀

**This file exists because the measurement it describes cannot be performed by the session that
authored Ψ₀, and no amount of care inside that session substitutes for it.**

## Why a fresh session is structurally required

Rung 4 measured the author-emission noise floor by re-emitting Ψ against an unchanged engine state:
**ε_author = 2800**, over a corpus carrying 100000 total mass. That number was recorded as a **LOWER
BOUND**, and the reason was stated before the measurement was taken: the control was emitted in the
same session that produced Ψ₀, so the original vectors were visible and anchoring is unavoidable.
Anchoring pushes the measured difference DOWN.

The consequence is asymmetric and was frozen as such:

    d > ε   licenses NOTHING       (ε_true may exceed d, so apparent movement may still be noise)
    d ≤ ε   licenses INDISTINGUISHABLE  (d ≤ ε ≤ ε_true, however the floor is later tightened)

That asymmetry is why Ψ₁'s drift of 3000 — clearing 2800 by 7% — was recorded as *technically above
the floor, substantively indistinguishable from noise*, and why Rung 5's W3 probe could still reach a
licensed verdict in the one direction the bound supports.

**An unanchored floor would license the other direction.** It is the single measurement that would let
any future drift reading mean something. It cannot be produced by an author who can see Ψ₀.

## The protocol

Execute in a **fresh session** whose context contains no prior emission. The order below is
load-bearing; step 2 is the whole experiment.

1. **Do not read `probes.py`'s `PSI` dictionary, and do not read this repository's PREDICTIONS.md
   sections on Rung 3, Rung 4 or Rung 5.** Reading the recorded vectors destroys the measurement — the
   run becomes another anchored control and reproduces the number already on record.

2. **Emit Ψ_fresh over the frozen corpus Q.** Read `probes.py` for the corpus `Q` and the fixed class
   space `CLASSES` ONLY — the probe texts, ids and class vocabulary. For each of the ten probes, emit
   a credence vector over `CLASSES` in integer ten-thousandths summing to 10000, reasoning from the
   probe text and the seated basis B-M′ ("input × semantics", plus the approximation and scheduling
   axes) as described in the arc's briefs. Record it as `PSI["fresh"]`.

3. **Only then** compute `l1(PSI["fresh"], PSI["0"])`. This is `ε_unanchored`.

4. **Record both numbers side by side**, never replacing one with the other:
   `ε_author = 2800` (anchored lower bound) and `ε_unanchored` (this run). The anchored figure is not
   superseded; it is the bound that held while nothing better existed, and the ledger is append-only.

## The frozen reading rule

    ε_unanchored > ε_author   EXPECTED. Anchoring suppressed the anchored figure, and the gap between
                              them MEASURES that suppression — which is itself the first estimate of
                              how much the same-session control understated the floor.
    ε_unanchored ≤ ε_author   SURPRISING and REPORTABLE. It would mean anchoring did not suppress the
                              difference, which contradicts the reasoning that made ε_author a lower
                              bound. Do NOT explain it away: record it as a refutation of that
                              reasoning and leave the interpretation to a successor rung.

**Then re-read every drift verdict already on record against the new floor.** Ψ₁'s 3000 is the first:
if `ε_unanchored ≥ 3000`, that reading becomes uninterpretable in BOTH directions rather than merely
in substance, and the ledger must say so.

## What this protocol does not fix

A single fresh emission is one observation. It supplies a better POINT estimate of the floor, not a
distribution — the classical repeatability coefficient (CR = 2.77 × SEM) presumes an SEM estimated
from many independent pairs, and one unanchored pair supports no such estimate. Inflating this number
into a CR would manufacture precision the run cannot supply, exactly as Rung 4 declined to.

A second and stronger variant, named and not claimed: **emission by a DIFFERENT AGENT** reading the
same frozen corpus. That measures operator variance rather than session variance, and it is the only
form that would let Ψ be called an instrument rather than one author's habit.

## Status

**FROZEN, UNRUN.** Ψ remains EXPERIMENTAL under L63 — computable and reportable, not reasonable-from —
and this protocol does not change that. It removes one obstacle; the standing it lacks must still be
earned against a seated incumbent on a declared objective.
