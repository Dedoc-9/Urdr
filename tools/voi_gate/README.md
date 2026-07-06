<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# voi_gate — a Value-of-Information decision gate

A small, buildable decision engine. It answers one question, continuously:

> **How much uncertainty does an action remove per unit cost, and is that worth
> doing before reality provides the answer?**

    Decision(a) = [ value_per_bit · VoI(a) − Cost(a) > ρ ]
    VoI(a)      = E[ H(X) − H(X | O_a) ]      # mutual information, bits, ≥ 0
    η(a)        = V(a) / (V(a) + Co(a))       # flow-efficiency share ∈ [0,1]

A fuzz run, an extra test, a formal proof, and a human review are all the **same
object**: each produces information, consumes resources, and moves confidence.
They differ only in the measured numbers, not their category.

## What this is *not*

Not the Urðr language core. This is **float** arithmetic (entropy uses `log2`),
so it is a separate tool with its **own** runner and is **not** sealed by
`verify.py` (whose gate is integer-exact by design law). Provenance: the
observable-projector lens (D1 §18) gave the invariant signal-vs-overhead
pattern; this replaces the projector with measurable accounting —
`projection = theoretical lens ; VoI + cost ledger = runtime mechanism`.

Two corrections from the design discussion are baked in:

1. **VoI is mutual information** `I(X;O) = H(X) − E_o[H(X|O=o)] ≥ 0`. A single
   surprising observation can *raise* conditional entropy; only the *expected*
   value is guaranteed non-negative, so we compute the expectation.
2. **bits ≠ cost.** `value_per_bit` is an explicit exchange rate; without it,
   `VoI − Cost` subtracts cost units from bits (a hidden units error).

## Use

```bash
# is a check worth running, or is it ceremony?
python tools/voi_gate/voi_gate.py --diagnostic 0.5 0.95 0.90 --cost 0.1
#   -> {"uncertainty_removed_bits": 0.62, "cost_units": 0.1, "decision": "GREEN"}  (exit 0)
python tools/voi_gate/voi_gate.py --bits 0.03 --cost 0.6
#   -> {"uncertainty_removed_bits": 0.03, "cost_units": 0.6, "decision": "RED"}    (exit 1)

# the falsifier suite (its own runner — NOT verify.py):
python tools/voi_gate/test_voi_gate.py
```

Exit code is 0 for GREEN, 1 for RED, so it drops into a CI step directly.

## Honest grade

- **The engine is `IMPLEMENTED / MEASURED`** — via `test_voi_gate.py` (13
  falsifiers; the gate is required to go both GREEN and RED; the margin ρ bites;
  non-vacuity re-proven by a flipped-inequality defect caught then reverted).
- **The claim that it *improves software outcomes* is `SPECULATIVE / N/A`.**
  That needs longitudinal data — did GREEN actions actually prevent failures, did
  RED ones actually save wasted effort, does ρ need adjusting? `Pipeline.calibration()`
  is built to collect exactly those tallies; it returns counts, never a verdict.
  Until the data exists: `declared ≠ verified`, `built ≠ adopted`.

The falsifier is therefore concrete and stated in advance: **after enough real
decisions, GREEN must correlate with prevented failures and RED with saved
effort, or the gate is miscalibrated (or worthless) and this grade must drop.**
