<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: caustic-refusal -->
# `caustic` — design brief (URDRCAU1)

## What it is

A subsystem with an exact growth law in some countable and a budget has a **scale at which it
dies**. This repository pins a dozen such laws and asks none of them that question; each carries
a *headroom* instead, which is the same fact read from the comfortable end. `caustic` reads it
from the other end and needs no new measurement — only forms that are already pinned.

## Why the refusal is the module

`sealframe`'s first caustic rested on work being "exactly linear in primitives". The equality was
real; the **axis label was not** — the fixture added a fresh patch of frame per primitive, so the
law was linear in *coverage*. Generalizing that pattern across subsystems without carrying the
lesson would have propagated one error into five. So a law declares its kind, and only two of
three can carry a caustic:

- **PROVEN_CLOSED_FORM** — derived and asserted equal to the execution it models, across its axis.
- **ISOLATED_FIXTURE** — measured on a fixture that varies the named axis alone.
- **FITTED** — a slope from a fixture that moves more than one thing. `CAUSTIC-REFUSE`, by name,
  with the confound stated. The class is populated on purpose, by the very slope that caused it.

## Three things the build found

**Affineness is not evidence of a sound axis.** The confounded law is *perfectly* affine — every
added triangle contributes an equal bounding box — and that clean straight line is exactly what
made the wrong x-axis persuasive.

**Most pinned laws are not linear in the axis they name.** The first version divided by a single
slope and refused three of four laws: `warden_edge_checks` is quadratic in grid side,
`raster_samples` sublinear in subdivision level. The mechanism now bisects, and affineness is
reported rather than required.

**And the claim drawn from that was an overclaim — retracted.** It said every `headroom × N`
reading elsewhere was suspect on the same grounds. Searched: there is essentially **one**,
`bench_protocol` §4's frozen-division bridge. `renderbound`'s "thirty-two bits of headroom" is a
magnitude bound and already a cautionary tale; `fpquat`'s "~2× headroom" is slack on an error
bound. One instance is not every reading — the difference between a survey and a flourish.

**That one instance does not survive intact**, so the claim was also not strong enough where it
did apply. §4's bridge is *circular as written*: ns/division is computed as tick-time **divided
by** the count, so multiplying it back returns the number it started from (L23). It carries
information only when transferred to a *different* count, and that transfer drifts 2.2× — ~3276
ns/division at one biped converging to ~1468 by a hundred, fixed per-call cost dominating at small
`n`. The bridge is sound in a converged regime and §4 states it without stating the regime. What
*is* exactly linear is the **count** (132 per biped, proven, counted from an instrumented run).

**The domain is part of the law.** A closed form is known where it was checked against execution
and nowhere else, so a budget that is not binding inside the verified range is refused rather than
answered by extrapolating a formula past its evidence.

## Grade

**MEASURED** — forms checked against execution on the run rather than quoted, monotonicity
verified, the caustic bracketed by its defining property (it fits, one more does not), and the
refusal proved selective. **DECLARED**: that a caustic is *reachable* — it says where a budget is
spent, never that a workload gets there. `does_not_show`: any wall-clock claim (no timing enters
the module); behaviour outside each verified domain; that the registered laws are all of them.

Row `caustic-refusal`; falsifiers in `tests/test_caustic.py`.
