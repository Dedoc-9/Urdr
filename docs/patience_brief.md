<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: patience-law -->
# `patience` — design brief (URDRPAT1, the price of the price)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P49 of batch 14
(`../exe_epistemics/PREDICTIONS.md`). **NON-SCORING: contamination declared at the freeze** —
`hainuwele/README.md` states this module's FINDING outright, which is the P33 (`bombtest`) situation
rather than P41's (a stated boundary). It is read and briefed; it enters no census, no meta, and no
FP-ROW count. Reading grade: **CONFIRMATION**.

## What it is

**The rung that audits the rung before it.** `auditgraph` priced undetected equivocation at kappa and
sold that price as converting an **invisible integrity attack into a visible availability attack** —
an appealing trade, because availability failures are noticed. `patience` asks what "visible" was
resting on.

## The core law (what `patience-law` certifies)

**The visibility both `auditgraph` and `splitview` relied on was DECLARED, never established.** Every
word of the integrity-becomes-availability trade rests on a partition being *seen*, and Chandra–Toueg
is the reason it cannot simply be assumed: a crashed process and an arbitrarily slow one are
indistinguishable to any asynchronous observer. A server that **stalls rather than excludes** therefore
obtains the same partition at a visible cost of zero — the exclusion ladder holds only at T ≥ Δ, and
below the delay envelope the 1/2/∞ ladder collapses to **0/0/0**.

`patience-selftest` bites three plants, and one of them names a class this repository had not needed a
name for: **LINEAR patience growth is SOUND** — it terminates, and the test asserts that it does — and
it **loses on PRICE alone**, costing 63 false alarms where doubling costs 6, and 199 against 8 at
Δ/T₀ = 200. A correct alternative rejected purely on cost is a different kind of refutation from a
wrong one, and the module says so rather than lumping them together.

## The seam (P49's reading, unscored)

**An inherited guarantee refuted by measurement — the `ashdepth`/`recirc`/`divergence` shape, and the
first instance aimed at a SIBLING RUNG rather than at handed-down literature.** The other three
refuted an outside intuition (a vacuity guard, an elegant loop, a rate metric); this one refutes the
arc's own previous rung, in its own vocabulary, and prices what buying the hypothesis back would cost
(`ceil(log2(ceil(Δ/T₀)))` one-time false alarms). The sound-but-too-expensive class is the quiet
contribution: it separates "this does not work" from "this works and you cannot afford it", which the
claim ladder had no cell for.

## does_not_show

That the residual is CLOSED — `liveness` takes it up and makes its shape exact without removing it, and
the README still names it the largest open hole in the authority arc. Nor does it show that Δ is
knowable in practice (the ladder *assumes* the envelope); nor anything about a real network's delay
distribution; nor that doubling is optimal rather than merely far cheaper than linear on the measured
corpus. Pricing an attack is not preventing it. `integrity ≠ truth`.

## Falsifier

This brief cites `patience-law`: the exclusion ladder holding only at T ≥ Δ, with the stalling server
obtaining the same partition at visible cost zero and the 1/2/∞ ladder collapsing to 0/0/0 below the
envelope. If a stalling server ever paid a nonzero visible cost below the delay envelope — restoring
the visibility `auditgraph` assumed — that row reddens and this brief's central claim dies with it.
