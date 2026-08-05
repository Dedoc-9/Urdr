<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: bombtest-law -->
# `bombtest` — design brief (URDRBMB1, interaction-free tamper detection)

**Read**: 2026-08-05, the READ pass under the successor selector — P33 of batch 9
(`../exe_epistemics/PREDICTIONS.md`). **NON-SCORING: contamination declared** — `hainuwele/README.md`'s
"Weak spots, named" section, read in full before the freeze, states this module's central finding
outright. The reading below is recorded but scores nothing and enters no census, under the rule that
excluded P10 (`govern`) and P19 (`cpredict`). Reading grade: **CONFIRMATION**.

## What it is

**Certifying that a recorded computation contains an illegal step WITHOUT ever running that step.**
The Dentatus Replay Court proves a published result is the untampered consequence of its inputs by
re-running the workflow bit-for-bit. That is the strongest check available, and its cost is not an
engineering matter: it requires possessing the inputs and executing the rules. A reviewer holding
embargoed patient data, a licensed model, or a week of cluster time cannot pay it. **Re-execution is
the detonation** — and the Elitzur–Vaidman question transposes exactly: can a reviewer certify a trail
is tampered without executing the tampered step?

## The core law (what `bombtest-law` certifies)

**Interaction-free means one measured thing, not a physical claim: the audit path invokes the rule
EXACTLY ZERO times, instrumented as a call count.** That is a claim about ACCESS AND COST. Five
structural features transfer from the interferometer and all five are classical: a check that cancels
to a constant in the honest case; tampering that breaks the cancellation; **one-sided** firing (no
false positives); **silence that is INCONCLUSIVE, not innocence**; and efficiency improvable by adding
arms, at a cost. What does NOT transfer is the part that makes EV remarkable — a real bomb's mere
*disposition* to absorb altering the amplitude with no absorption occurring has no classical
mechanism, and treating the analogy as more than structural would be inflation.

The soundness is a **NEVER-CLAIM discharged exhaustively**, in Holzmann's SPIN sense — a detector
wired so that in the honest case it cannot fire, where an accepting run IS the counterexample: over
the full state space and every legal transition, no conserved functional is ever broken (4096 states,
13824 legal transitions, **0 acceptances**). `bombtest-selftest` proves the instrument bites: a
planted NON-CONSERVED arm makes the never-claim accept 4608 times against 0 honest.

## The seam (P33's reading, unscored)

A one-sided screen whose soundness is an exhaustive absence and whose novelty is a COST claim rather
than a detection claim. Notable in its own record: the docstring corrects itself in place — a first
draft said 24576 transitions (4096 × 6, every state times every rule, counting boundary-blocked moves
that never fire), and the correction is recorded rather than rounded to, on the stated grounds that
writing down a product instead of reading the counter is the same class of error as reporting a sample
as a universal. The module polices its own arithmetic by the rule the arc applies to prose.

## does_not_show

**An ADAPTIVE adversary.** Detection is measured against a NON-ADAPTIVE tamperer; an adversary who
reads the invariants picks a kernel delta and is caught 0 of 70 times. It is a **screen, never a
verdict**, and it does not replace the hash chain or the Replay Court. Silence establishes nothing
(the inconclusive port is load-bearing, not a weakness to be argued away); the analogy to physics is
structural only; and no claim is made about wall-clock or about the cost of the arms.

## Falsifier

This brief cites `bombtest-law`: the never-claim discharged over the full state space with zero
acceptances, and the zero-invocation audit path. If the honest case ever produced an acceptance (a
false positive, which would make the screen condemn honest work), or the audit path invoked the rule
even once, that row reddens and this brief's central claim dies with it.
