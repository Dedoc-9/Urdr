<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: fpface-exact -->
# `fpface` — design brief (URDRFACE1, T3.15, the exact-integer facing seam)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P43 of batch 12
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**, the author's leading credence (32) correct —
the batch's only clean leading call. Reading grade: **CONFIRMATION**.

## What it is

**Where an integer facing becomes a direction.** The world's movement authority stores facing as an
integer (`drive`'s facing map); anything that points, aims or looks needs a direction vector. That
conversion is a seam, and a seam that rounds silently is where exactness dies — so this rung
establishes exactly how far exactness reaches and states plainly where it stops.

## The core law (what `fpface-exact` certifies)

**The four cardinal facings lift to their exact direction vectors at ZERO ulp, and the cyclic group
E→N→W→S→E permutes EXACTLY over `drive`'s facing map — the exact embedding.** Not "accurate to
tolerance": zero error, and the group structure preserved under the lift, so rotating four times
returns identically rather than approximately. `fpface-refusal` is total and typed (5/5 `FACE-REFUSE`:
out-of-range · negative · bool · str · float facing).

## The seam (P43's finding)

**The exactness boundary is measured, not asserted — and that is the module's real contribution.**
`fpface-boundary` states where the exact embedding ends: mouse-look interiors are continuous rather
than cardinal, so they **round** — deterministically, but they round — and **accumulation drifts a
bounded non-zero ulp count**. The module measures its own imprecision rather than claiming it away,
and pins the one constant that could have hidden a dependency: **√2/2 is a trig-free frozen `isqrt`**,
so no transcendental function enters the authority path. That matters beyond elegance, and it is the
same reasoning `cayley` gave for its division-free Leibniz expansion: a seam that avoids `sin`/`cos`
is a seam that cross-places without a rounding question to answer.

This is also the joint where "exact integer" in a role line *did* predict the semantics — the freeze
noted that P34 had shown such vocabulary is weak evidence and priced C-EQ only narrowly ahead. It led
anyway. One joint does not overturn the caution; it is recorded as the counter-instance.

## does_not_show

Continuous facing exactness (explicitly rounded, with a bounded drift — the module's own boundary);
pitch (that is `fpcap`'s seam); the rendered view (behind the D15 firewall); angular velocity or
turn-rate limits; whether a claimed facing is HONEST (that is `warden`'s territory — this certifies the
conversion, not the claim). An exact embedding of a facing is not a true facing. `integrity ≠ truth`.

## Falsifier

This brief cites `fpface-exact`: the four cardinal facings lifting to their exact direction vectors at
0 ulp, and the E→N→W→S→E group permuting exactly over `drive`'s facing map. If a cardinal lift ever
carried non-zero error, or the four-fold rotation failed to return identically, that row reddens and
this brief's central claim dies with it.
