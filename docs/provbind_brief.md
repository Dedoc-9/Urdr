<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: provbind-law -->
# `provbind` — design brief (URDRPRV1, S3, provenance binding)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P51 of batch 15
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-R**, the author's leading credence (42) correct.
Reading grade: **CONFIRMATION**.

## What it is

**Stopping a certificate from being stapled to geometry it never covered.** A provenance certificate
says something about a capture — who made it, under what licence, at what buffer distance. If that
certificate can be lifted off one block and attached to another, the whole provenance layer is
decoration: the attacker takes a permissive certificate from a public-domain block and staples it to a
restricted capture.

## The core law (what `provbind-law` certifies)

**The certificate is BOUND to the geometry it certifies, by `H(cert | lattice_digest)` with the
lattice digest RECOMPUTED AT SERVE TIME** — so the binding **cannot be asserted by whoever supplied
it**. Every carried field, including the capture-time buffer distance, enters the digest, so a
certificate that says anything different about the capture is a different certificate.

`provbind-selftest` bites two plants, and the first is the whole reason the rung exists: **the
metadata-only digest — the handed-down form — matches a DIFFERENT block's geometry**, so a permissive
certificate lifted off a public-domain block and stapled to a restricted capture is **ADMITTED**. The
inherited design is not merely weaker; it admits exactly the attack the layer is for.

## The seam (P51's finding)

**Recompute rather than trust — the neutral-ruler pattern's eighth instance.** The load-bearing phrase
is *recomputed at serve time*: the checker derives the lattice digest itself rather than accepting the
one that arrived with the certificate, so the supplier is structurally denied the ability to assert its
own binding. That is the same move `mesh` makes with its monolith oracle, `traj` with its
locally-derived truth, `cayley` with two mutually-checking algorithms, `commuteprop` with a
brute-permutation oracle, and `horn` with an independent brute-force sweep. And the selftest is
**grade-what-you-inherit** again (after `divergence`'s rate metric, `horn`'s continuous bound and
`magicdiv`'s Hausdorff corollary): the handed-down metadata-only digest is refuted by exhibiting the
admission it permits, not by argument.

## does_not_show

That the certificate's CONTENTS are true — binding proves a certificate belongs to this geometry, never
that its licence claim, attribution or buffer distance is honest (that is `tilecert`'s territory, and
its answer is attribution, not verification); who issued it; revocation or expiry; wall-clock or serve
cost. A bound certificate is one that cannot be moved. `integrity ≠ truth`.

## Falsifier

This brief cites `provbind-law`: the certificate bound by `H(cert | lattice_digest)` with the lattice
digest recomputed at serve time, every carried field entering the digest. If a certificate ever
verified against geometry it did not cover — most sharply, if the lifted public-domain certificate were
admitted against a restricted capture — that row reddens and this brief's central claim dies with it.
