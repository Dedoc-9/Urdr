<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: meshattest:laws -->
# `meshattest` — design brief (URDRMAT1, M2.5, mesh reality attestation)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P47 of batch 13
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 14**. Outcome: **C-EQ**, matching the
pre-declared ROW-reading over the ROLE-reading (C-R) — **FP-ROW's first genuine win**. Reading grade:
**CONFIRMATION**.

## What it is

**Phase M's laws, run against reality instead of against a simulation of it.** `nway`, `migrate` and
`mesh` are certified in-process, where the scheduler is cooperative and the transport is a function
call. This rung re-runs the migration law across **real sockets and real processes**, where messages
can be reordered, duplicated, delayed or forged by something the test harness does not control.

## The core law (what `meshattest:laws` certifies)

**Reality replays LAWFUL under the UNMODIFIED law.** The synthetic handoff (A→B, with a usurper
refused and a disjoint region untouched) and the relay (A→B→C custody chain, with a mid-chain usurper
refused) each replay lawful under `migrate` **deterministically** — and the decisive clause:
**the migration certificate the checker re-mints MATCHES reality's record.** The law is not adapted for
the real transport; the real transport is shown to satisfy the law already, with the re-minted
certificate and the recorded one agreeing.

`meshattest:forges` supplies the adversarial half under one principle — **reality may not overrule the
law**: a usurper's write recorded ADMIT (a double-writer laundering through a socket), a drifted
witness, a forged certificate, a certificate to the wrong destination, an untyped outcome, a dropped
migration, and a drifted final witness **each refuse typed**. `meshattest-selftest` proves the trace
itself cannot be edited: a single byte flip refuses on the self-digest, and an anonymized re-seal
refuses on the named-host law.

## The seam (P47's finding)

**An attestation is an EQUIVALENCE, not a certificate — and that is what FP-ROW predicted.** The role
line ("real sockets, real processes") reads as something that *attests*, i.e. admits or refuses, and
the pre-declared role-reading said C-R on exactly that basis. The row certifies agreement: what the
real-socket, real-process run produces equals what the law says it must, with the re-minted certificate
matching the record. That is the `mesh == monolith` / `hand` bit-identity pattern carried across a real
transport rather than a new mechanism. The refusal battery is the guard, not the law.

This module is also one of the arc's four TRUE CONFORMANCE GAPS (gate stage and falsifiers, no pinned
corpus), and — like `view_witness` (P32) — the read found nothing hiding there: an attestation whose
subject is a live socket run cannot have its evidence pinned in advance without ceasing to be an
attestation. The missing corpus is a consequence of what the module is, not a debt.

## does_not_show

That the network is HONEST — the forge battery covers an enumerated set of attacks, not all of them;
performance, throughput or latency over the real transport (no wall-clock is gated); more hosts than
the attested topology; that a real deployment's sockets behave like these sockets. An attestation that
reality satisfied the law on these runs is not a proof that it always will. `integrity ≠ truth`.

## Falsifier

This brief cites `meshattest:laws`: the synthetic handoff and the A→B→C relay replaying lawful under
the unmodified `migrate` law, deterministically, with the re-minted migration certificate matching
reality's record. If a real-socket run ever diverged from the in-process law, or a re-minted
certificate failed to match the recorded one, that row reddens and this brief's central claim dies
with it.
