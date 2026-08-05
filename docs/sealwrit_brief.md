<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: sealwrit-provenance -->
# `sealwrit` — design brief (URDRSWT1, T3.49, W3 — the signed wire)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P56 of batch 16
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 17**. Outcome: **C-R**, the author's
leading credence (36) correct. Reading grade: **CONFIRMATION**.

## What it is

**WHO may write, separated from WHAT may change.** `wire` established equal-or-refuse replication: a
record is admitted only if it reproduces the authority's bytes. That polices the *content* of a write
and says nothing about its *author*. This rung adds the second axis — a signed writ — and, crucially,
keeps the two from contaminating each other.

## The core law (what `sealwrit-provenance` certifies)

**An unregistered, wrong-keyed, mis-signed, or tail-collision-forged writ refuses BEFORE the state
law, with replica and ledger BYTE-IDENTICAL — and the genuine writ still admits.** The parenthetical
is the discipline: *a failed signature blocks nothing honest*. A provenance layer that refused
legitimate writes would be worse than none, so the row asserts both directions. And the plant is
pointed: **the first-byte defect verifier ACCEPTS the forgery the real one refuses**, so the
signature check is shown to be doing work no shortcut reproduces.

## The seam (P56's finding)

**The ordering is the theorem, and it is stated as one.** `sealwrit-order`: **eligibility precedes
admission.** A writ that is BOTH mis-signed and state-unlawful refuses `SEAL` — that is the ordering
proof, since a system checking state first would have reported the other code. A perfectly signed
stale record refuses `WIRE`: **a signature cannot launder state.** And neither refusal seals anything —
**eligibility is consumed by admission, never by attestation.** That last clause closes the attack a
naive design invites: presenting a writ, having it refused on state, and treating the signature as
spent-and-therefore-verified.

`sealwrit-reuse` completes it: the first admission **seals the keypair to its digest**, so an identical
redelivery rides free to the CAS (at-most-once, inherited from the wire), while a verified-DISTINCT
state-lawful record under a sealed keypair **refuses on the ledger** — the reuse leak's exact exploit,
contained rather than argued away.

So the role's "WHO × WHAT" is real, but it is not a two-law join: the axes are kept in a strict ORDER
with a proof that the order holds, which is why the central row reads as admission rather than
composition.

## does_not_show

Key management, distribution or revocation (a registered keypair is an input here); whether the
signer is who they claim to be outside the registry (attribution, not identity — `tilecert`'s
distinction); the cryptographic strength of the signature scheme; wall-clock or verification cost;
collusion between a registered writer and a cheater. A writ that admits was signed by a registered
key and is state-lawful — never that its author was honest. `integrity ≠ truth`.

## Falsifier

This brief cites `sealwrit-provenance`: unregistered, wrong-keyed, mis-signed and tail-collision-forged
writs refusing before the state law with replica and ledger byte-identical, while the genuine writ
still admits. If a forged writ ever admitted — or a genuine one were blocked by the signature layer,
which is the failure that would make provenance worse than nothing — that row reddens and this brief's
central claim dies with it.
