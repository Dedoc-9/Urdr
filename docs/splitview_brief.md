<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: splitview-law -->
# `splitview` — design brief (URDRSPV1, the official server's own audit)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P57 of batch 17
(`../exe_epistemics/PREDICTIONS.md`). **NON-SCORING: contamination declared at the freeze** — the
README states this module's finding outright, which is the P33/P49 situation. Read and briefed; enters
no census and no meta. Reading grade: **CONFIRMATION**.

## What it is

**The rung that turns the server from an unexamined trusted party into an examined one.** Every rung
before it hardens the world against a lying *client*. This one asks the other question: if the
official server forks — showing two mutually inconsistent worlds to different clients — who can tell?

## The core law (what `splitview-law` certifies)

**A forked server is NOT detectable by verification, and IS detectable only by comparison.** Measured:
**the strongest solo detector flags 0 of 240 forks, while one crossing comparison flags 240 of 240.**
And the decisive clause — **the zero is a property of the INPUT, not a weakness of the detector**: a
confined client's transcript is bit-identical to the honest one. There is nothing in it to find. No
cleverer verifier helps, because the evidence does not exist locally.

`splitview-selftest` bites four plants, and two of them are unusually instructive. The
**root-inequality detector is INVERTED** — it cries fork on **258 of 258 honest pairs**, because
differing roots are the *resting state* rather than evidence. And **the cut theorem stated without its
depth hypothesis over-claims 3232 times**: the theorem is true, and true only with the hypothesis
attached.

## The seam (P57's reading, unscored)

**An impossibility measured rather than argued — and the arc's cleanest instance of a zero that is a
result.** `sea-marangoni` insisted a zero must be earned by a plant that could have made it nonzero;
here the zero (0 of 240) is earned by showing the input itself is bit-identical, so no detector could
have done better. That distinction — *the evidence is absent* versus *my instrument missed it* — is the
whole content of the rung, and it is what makes the recommendation downstream (compare, do not verify)
a consequence rather than a preference.

The inverted-detector plant deserves its own line: a detector that fires on 258 of 258 honest pairs is
not merely wrong, it is anti-correlated, and it would have looked like a *sensitive* fork detector to
anyone who never ran it against honest input. That is L62's null-entrant lesson arriving from a
different direction.

## does_not_show

WHO forked, or which branch is canonical — detection localizes to a *pair*, never to a culprit, and
attribution needs signed heads this model does not carry (the README names this as a standing gap).
Nor does it show that comparison is CHEAP (that is `auditgraph`'s kappa), that exclusion is VISIBLE
(`patience` refutes exactly that assumption), or anything about a server that mints its own
participants. A fork proved is not a fork attributed. `integrity ≠ truth`.

## Falsifier

This brief cites `splitview-law`: a forked server undetectable by verification (0 of 240 by the
strongest solo detector) and detectable by comparison (240 of 240 by one crossing), with the zero a
property of the input. If any solo detector ever flagged a fork from a confined transcript — which
would mean the transcripts were not bit-identical after all — that row reddens and this brief's central
claim dies with it.
