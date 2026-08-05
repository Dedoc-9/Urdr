<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: tilecert-taxonomy -->
# `tilecert` — design brief (URDRTIL1, the tile certificate and what it actually proves)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P62 of batch 18.
**NON-SCORING: contamination declared at the freeze** — the README states this module's finding, the
P33/P49 situation. Read and briefed; enters no census and no meta. Reading grade: **CONFIRMATION**.

## What it is

**The rung that says what a signed certificate is worth — and it is less than the name suggests.**

## The core law (what `tilecert-taxonomy` certifies)

**Necula's proof-carrying code has one defining property: the consumer CHECKS the proof against the
artifact and trusts the producer for nothing.** Measured against that definition, **a certificate
asserting a property of data the verifier does not have is NOT A PROOF but a SIGNED CLAIM** — a
signature establishes *who said it*, never *whether it is true*. The taxonomy is the law: the rung
refuses the borrowed prestige of "proof-carrying" and names the object correctly.

`tilecert-attribution` states what survives. **What the certificate buys is not pre-download
verification of content — that would require the content — but ATTRIBUTION:** a bound, signed
certificate whose recomputable field later disagrees with the lattice is **NON-REPUDIABLE EVIDENCE of
server misbehaviour, reproducible by any third party.** The value is real; it just arrives *after* the
fact and is evidentiary rather than preventive.

## The seam (P62's reading, unscored)

**An inherited claim refuted, and the estimator refuted TWICE.** `tilecert-selftest` is unusually
thorough about killing its own attractive idea. The predictive estimator **saves no work** — reading
every occupied cell's prefix depth *is* the same single pass `charge_for` already makes, measured at
equal visits and a saving of **0**, so "refuse before processing" processes. And **it predicts nothing
about the charged defect.** Two independent refutations of one appealing mechanism, kept in the record
rather than deleted.

This is the `ashdepth`/`recirc`/`divergence`/`horn` shape at its most self-directed: the module's own
first idea is the thing measured and rejected. And the taxonomy half is the arc's clearest instance of
refusing a borrowed word — "proof" — because the borrowed word would have imported guarantees the
mechanism does not provide.

## does_not_show

Pre-download verification of tile CONTENT (structurally impossible without the content — that is the
finding, not a gap); who the signer is beyond the registry (`sealwrit`'s territory); that attribution
deters anything (non-repudiable evidence is useful only where someone will act on it); revocation. A
signed claim is a claim with an author. `integrity ≠ truth`.

## Falsifier

This brief cites `tilecert-taxonomy`: that a certificate asserting a property of data the verifier does
not have is a signed claim rather than a proof, measured against proof-carrying code's defining
property. If a verifier could ever check such a certificate against the artifact without possessing the
artifact — making it a proof after all — that row reddens and this brief's central claim dies with it.
