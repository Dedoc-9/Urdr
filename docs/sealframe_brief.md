<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: sealframe-envelope -->
# `sealframe` — design brief (URDRSFR1, T3.55, V4 — the sealed frame)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P54 of batch 16
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**; the author priced C-R 32 against C-EQ 26 and
missed. Reading grade: **CONFIRMATION**.

## What it is

**The frame budget, sealed to the work that actually happens.** A renderer's performance claim is
usually a model of cost sitting beside the code that pays it, and the two drift. This rung binds them:
the op envelope is not a *model* of the loop's work, it is a count of the loop's work.

## The core law (what `sealframe-envelope` certifies)

**MODEL == EXECUTION.** The op envelope IS the loop's actual work — **micro-steps equal the glide
trajectory's own count**, so the budget cannot drift from the thing it budgets. Two consequences ride
on that identity: **sprint costs exactly twice the walk**, and **the envelope FITS the 60Hz budget**
under the measured native tick rate, stated as an inequality — high fps is architecturally cheap, and
cheap for a reason that is counted rather than hoped.

## The seam (P54's finding) — and the honesty boundary MECHANIZED

The prediction read "sealed frame" as something policed (C-R 32) and the row certifies an identity.
But the module's most striking row is the one beside it. **`sealframe-honesty` turns this repository's
own claim-grading ladder into a gate row:** every MEASURED frame-budget entry must cite a **named-host
log** (the unlogged-MEASURED defect is caught); **`input→photon` stays NOT_MEASURED** until a §3 run
exists; and a host log **graduates a claim to MEASURED only when it NAMES a host AND its input→photon
is under target**. `sealframe-selftest` makes it bite — a tampered host log refuses on its self-digest,
and an anonymous log cannot graduate a MEASURED claim.

That is the discipline this whole arc is written under — MEASURED vs DECLARED vs NOT_MEASURED, no
claim exceeding what its evidence licenses — **enforced by the gate rather than by the author's
care.** Elsewhere the ladder is a convention the prose obeys; here it is a row that reddens. It is the
strongest instance in the arc of `attestation ≠ authority` made executable, and it is the reason a
performance claim in this module can be trusted in a way performance claims usually cannot.

## does_not_show

`input→photon` latency — explicitly NOT_MEASURED and structurally prevented from being claimed
otherwise until a named-host §3 run exists; GPU or driver behaviour; frame budgets on unnamed hosts
(the whole point of the honesty row); visual output (behind the D15 firewall); that 60Hz is achievable
in a real deployment rather than under the measured native tick rate. An envelope that fits a budget
is a counted claim about work, never a promise about a user's screen. `integrity ≠ truth`.

## Falsifier

This brief cites `sealframe-envelope`: the op envelope being the loop's actual work (micro-steps ==
the glide trajectory's own count, model == execution), sprint costing exactly twice the walk, and the
envelope fitting the 60Hz budget under the measured native tick rate. If the envelope ever diverged
from the trajectory's own micro-step count — the budget becoming a model again — that row reddens and
this brief's central claim dies with it.
