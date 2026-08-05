<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: wireattest:laws -->
# `wireattest` — design brief (URDRWAT1, T3.51, W5 — the reality attestation)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P63 of batch 18, **the final
joint of the pass** (`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**, the author's leading
credence (42) correct via a prior transferred from `meshattest` and disclosed at the freeze. Reading
grade: **CONFIRMATION**.

## What it is

**The wire phase's laws, run against a real transport instead of a model of one.** `wire` certifies
equal-or-refuse replication in-process; `storm` models adversarial transport deterministically. Both
are simulations of the hostile world. This rung runs the same unmodified law across **real sockets**,
where loss, stalling and malice are not scripted by the harness.

## The core law (what `wireattest:laws` certifies)

**Reality replays LAWFUL under the UNMODIFIED wire law.** Three runs: the **synthetic gale** (chaos +
malice, zero stalls), the **tempest** (real loss, with a verified repair fetch), and the **stalled
no-repair variant** — each replaying deterministically, with the decisive clause: **the checker accepts
exactly what the law admits.** Not a relaxed law for real conditions, and not a checker tuned until
reality passes; the same law, and reality satisfying it.

`wireattest:forges` supplies the adversarial half under the principle the attestation family shares —
**reality may not overrule the law on any axis**: a forged admission, a drifted witness, a double
admission, an untyped outcome, a corrupt delivery claiming admission, **a stalled client claiming the
authority's witness**, and a consistent wrong-address fetch each refuse typed. `wireattest-selftest`
seals the trace itself — a single byte flip refuses on the self-digest, an anonymized re-seal refuses
on the named-host law.

## The seam (P63's finding)

**The attestation pattern, confirmed on its second carrier — and the transfer paid a third time.** The
freeze disclosed the prior from P47 (`meshattest`, the Phase-M sibling, C-EQ on exactly this question)
and priced it ahead without confidence. It held: **an attestation in this arc is an EQUIVALENCE, not a
certificate.** Both modules phrase it the same way — real transport, *unmodified* law, replay lawful,
re-derived evidence matching the record — and in both the refusal battery is the guard rather than the
law. Cross-joint transfer closes the pass at **1 hurt / 3 helped**, small enough to state honestly and
not large enough to license the practice.

The stalled-client forge is the sharpest single case: a client that received nothing claiming the
authority's witness is exactly the attack a naive attestation would admit, since its *claim* is
well-formed and its *evidence* is absent.

## does_not_show

That the network is HONEST — the forge battery is an enumerated set, not an exhaustive one; throughput,
latency or bandwidth over the real transport (no wall-clock is gated); hosts or topologies beyond those
attested; that a production deployment's sockets behave like these. Reality having satisfied the law on
these runs is not a proof that it always will — this module is one of the arc's four true conformance
gaps for a structural reason: **an attestation whose subject is a live run cannot have its evidence
pinned in advance without ceasing to be an attestation.** `integrity ≠ truth`.

## Falsifier

This brief cites `wireattest:laws`: the gale, tempest and stalled no-repair runs each replaying lawful
under the unmodified wire law, deterministically, with the checker accepting exactly what the law
admits. If a real-socket run ever required the law to be relaxed to admit it — or the checker admitted
something the law does not — that row reddens and this brief's central claim dies with it.
