<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: wire-replicate -->
# `wire` — design brief (URDRWIR1, T3.47, the wire-phase opener)

**Read**: 2026-08-04, the centrality-ordered READ pass — run 2's first blind READ (P6,
`../exe_epistemics/PREDICTIONS.md`), frozen with rival basis predictions, graded credences, MT kill
conditions, and the interface instrument's risked background call (which was right). Outcome:
**P6-C-AB** — the second consecutive tie: one central row certifies adjudication and transport
inseparably. Reading grade: **CONFIRMATION** — the module is what its rows certify.

## What it is

**Equal-or-refuse replication.** Production replication ships derived state and asks the client to
trust it; CRDTs design types whose merges cannot conflict. This wire does neither: every update IS
the essence-bearing object — the 104-byte URDRRAN0 regional record, verbatim — and the receiving
client ADMITS it under the same laws the authority used, against its own replica. The client is a
**verifier, not a believer**: a malicious or buggy server produces a typed `WIRE-REFUSE` with the
replica byte-unchanged, never a silent desync.

## The core law (what `wire-replicate` certifies)

After every admission the replica equals the authority **byte-for-byte** on the resident set — with
the new chunk **derived, never shipped** (104 bytes per edit regardless of chunk size; the frame
property makes recomputation exact). And ordering needs no machinery: **in-region order is
structural** (each record's parent is the previous chunk state's address — terraform's chain law on
the wire; an out-of-order update refuses on the stale parent, admits on in-order retry, and an exact
duplicate refuses at-most-once for free, because its own admission moved the parent it binds);
**cross-region order is provably irrelevant** — every interleaving of disjoint-authority updates
lands the identical replica, RAN-0's nullity doing duty as the wire's ordering law.

Around it: `wire-interest` — the interest filter is one frozenset test on the essence's spatial
axis, **sound** (an irrelevant edit cannot touch a resident chunk; the unsent client stays
byte-equal) and **necessary with the violation detected** (a withheld relevant update is caught by
the next admission's CAS — drift is refused, never absorbed). `wire-refuse` — tamper, unheld
region, out-of-order, raw bytes, and duplicate each refuse, and **every refuse leaves the replica
byte-identical** (the client never half-applies). `wire:scenes` pins four configurations
(faithful_mirror / narrow_gaze / crooked_wire / silent_drift) to URDRWIR1 digests.

## The seam (P6's finding)

The rivals disagreed — B-A′ predicted transport/ordering central, B-B′ predicted
equality-adjudication central — and the row fused them: the equality is *achieved by* transporting
the essence and re-adjudicating it under canonical law. Two consecutive C-AB ties are now coupling
data: these axes co-occur in every replication-adjacent central law read so far, and a compound
basis element ("verified essence-replication") becomes mintable if a third tie accrues. The module
also **mints nothing** — pure composition, each absence a theorem already paid for — which the
mutants' composition axis (added from P5's residual) classified correctly on its first forward
outing: the checkpoint mutation paid off prospectively, not just on replay.

## does_not_show

TRANSPORT itself is DECLARED, not carried: loss, reordering, and duplication are modeled by the
delivery-order falsifiers — the laws are transport's obligations, stated where a transport must
meet them, not a socket implementation. WHO may send is `authinput`'s territory (this rung
certifies state law: a lawful update admits whoever relays it; an unlawful one refuses whoever
signs it). Interest SHIFT (acquiring/releasing regions mid-session) is operational policy over
`chunkload`'s verified fetch. Fan-out scheduling is `govern`'s. Wall-clock and bandwidth are
`bench.py`'s. Cross-placement: URDRWIR1 joins the placement frontier. And the interest law's
detection is *eventual* (the next in-region admission), not instantaneous. `integrity ≠ truth`.

## Falsifier

This brief cites `wire-replicate`: the row certifying update-is-the-record, per-step byte equality
with derivation, and interleaving invariance. If a replica stopped equalling the authority after
admission, a snapshot rode the wire, or two interleavings of disjoint updates diverged, that row
reddens and this brief's central claim dies with it.
