<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: testament-death -->
# `testament` — design brief (URDRTST1, T3.44, MMO Stage I)

**Read**: 2026-08-04, the centrality-ordered READ pass — P30 of batch 8
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ** — and the author's leading credence (C-INV 40)
LOST to its own second-place call (C-EQ 22). Recorded as a miss, not smoothed over. Reading grade:
**CONFIRMATION**.

## What it is

**Durable intent — the write that survives its writer.** `resurrect` proved the READ side of death (a
successor replays a saved world from the store alone); this rung proves the WRITE side. A client
authors an edit under a lease and may DIE holding it; the intent survives as a TESTAMENT — 144 bytes,
`MAGIC | regional edit record (104) | SHA-256`, and nothing more, because the lease it was authored
under is DERIVABLE (the record's parent digest + region ARE the lease). The name is exact twice over: a
last WILL (intent surviving its author, executed by a successor only under the conditions it names)
and TESTIMONY (the record as evidence, content-addressed, corruption-refusing).

## The core law (what `testament-death` certifies)

**Death is invisible to the answer.** A REAL successor process, given nothing but the store and an
address, performs probate over a disk-only channel — and its output is BIT-IDENTICAL to the admission
the never-died writer would have produced, twice over. `testament-probate` states the same equality
inward: probate == the living admission == the global reproof, so everything the lease law proved is
INHERITED (lost-update impossibility, amortized == reproved, interval transport). EXACTLY-ONCE is free
rather than added: the admission moves the very authority the testament names, so a second probate
refuses. And the refusal SPEAKS — "executed" (the current chunk state IS what this intent produces:
the will was carried out) vs "distributed" (a foreign edit moved the authority: re-author) —
adjudicated by deriving the expected child from the RETAINED parent state and comparing content
addresses; a store no longer retaining the parent refuses "unadjudicable" rather than guessing.
THE EXECUTOR IS PURE: a refused probate writes nothing, the store byte-identical after.

## The seam (P30's finding)

**The prediction read the motivation; the rows certify the mechanism.** "Survives its writer" sounds
like a continuity INVARIANT (B-M′'s founding axis, and the credence went there at 40) — but what is
actually gated is an EQUALITY: the successor computes the same bytes the living writer would have.
Survival is the story; bit-identity across the death boundary is the law. That is the recovery-
equivalence pattern (`persist`/`resurrect`) extended from state to INTENT, and the honest lesson is
that a role sentence describing WHY a rung exists is weak evidence for WHAT its central row certifies
— `claim ≠ code`, applied to the author's own prediction. The unnamed gem is the three-flavor refusal
earned from EVIDENCE rather than assumed: no flavor is ever guessed from missing evidence, which is
the `geoquorum` discipline (a refusal must say which kind it is) reaching the durability layer.

## does_not_show

A crash DURING probate's persist-back (the successor prints, the caller persists — torn writes are
the caller's crash-atomicity boundary, `persist`'s law); WHO may leave a testament (issuance —
`authinput`/capability territory, DECLARED); retry POLICY after "distributed" (re-authoring is the
client's choice; the law only guarantees the flavors are true); batching (a will with many bequests is
a chain of these primitives); garbage collection of executed testaments (the store keeps everything —
anamnesis; compaction is operational); wall-clock (`bench.py`); cross-placement. A surviving intent is
not a CORRECT intent — probate certifies that the will was executed as written. `integrity ≠ truth`.

## Falsifier

This brief cites `testament-death`: the through-death admission by a real successor over a disk-only
channel, twice, bit-identical and equal to the never-died admission. If a successor's probate ever
diverged from the living admission, or a refused probate perturbed the store, that row reddens and
this brief's central claim dies with it.
