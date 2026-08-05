<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: buoyancy-properties -->
# `buoyancy` — design brief (URDRBUOY1, T3.5, the wave seam's measured consumer)

**Read**: 2026-08-05, the READ pass under the SUCCESSOR selector (pure lex — centrality exhausted) —
P34 of batch 9 (`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-INV**; the author's leading credence
(C-EQ 30) lost to its second call (C-INV 25). Reading grade: **CONFIRMATION**.

## What it is

**The gameplay consumer of the certified sea.** `wavefield` (T3.3) certifies an exact traveling height
field and the WebGL2 view is its DECLARED consumer; this is the other consumer the wavefield docstring
named and never built — the one that turns a certified field into a certified *effect*. A rigid flat
raft floats on the field, and at each tick settles to the integer waterline z\* where displaced
measure balances weight (a discrete Archimedes):

    Δ(z) = Σ_cells max(0, h(x,y,t) − z)        z* = the LARGEST z with Δ(z) ≥ weight

Δ is non-increasing in z, so z\* is found by integer **bisection** — division-free (`<<`, `>>`, `+`,
`−`, comparisons; midpoint `lo + ((hi−lo) >> 1)`), so the result is EXACT and cross-placement is a
clean next step.

## The core law (what `buoyancy-properties` certifies)

**The exact Archimedes bracket**: `Δ(z*) ≥ W > Δ(z*+1)` — the characterizing property of the
waterline, not an approximation of it. Plus Δ's monotonicity (which is what licenses the bisection at
all), and the behavioural pair that keeps the law non-vacuous: the raft **heaves on swell and rests on
still** water. `buoyancy-selftest` makes the clamp load-bearing — an unclamped-displacement defect
diverges from the heave — and `buoyancy-refusal` holds a total typed battery (6/6 `BUOY-REFUSE`:
empty · out-of-grid · duplicate · weight ≤ 0 · bool · non-int cell).

## The seam (P34's finding)

**The question/answer split, third carrier — and the reason the leading call missed.** The prediction
read "exact integer flotation" as naming an identity (C-EQ, the `wavefield` exact-arithmetic pattern).
The rows certify something else: a *bracket* that characterizes a measured answer. Blocking is not
refused here — z\* is a MEASURED EVENT, and the typed refusals guard only the DOMAIN boundary
(malformed footprint, impossible weight). That is exactly `stance`'s residual (P3: this repo separates
ADMISSION OF THE QUESTION, which refuses, from THE ANSWER, which is measured), now on its third
carrier — `stance` measures where terrain blocks, `traj` measures innovation, `buoyancy` measures
where water holds. "Exact" described the ARITHMETIC; it said nothing about the law's semantics, and
the freeze mistook the one for the other.

## does_not_show

Real hydrostatics — the buoyancy LAW is a **DECLARED model** (a discrete Archimedes), walled off from
the D5 ledger exactly as the D20–D23 budget laws are; only the *computation* of z\* is MEASURED.
Non-rigid or non-flat bodies (a rigid flat raft is the certified case); rotation, list, or capsize;
wall-clock; the rendered water (pixels stay behind the D15 firewall). A reproducible waterline is not
a REAL one — it is what this declared model says, computed exactly. `integrity ≠ truth`.

## Falsifier

This brief cites `buoyancy-properties`: the exact Archimedes bracket Δ(z\*) ≥ W > Δ(z\*+1), Δ
monotone, and the heave/rest behavioural pair. If a computed waterline ever fell outside its own
bracket, or Δ were non-monotone (which would silently invalidate the bisection), or the raft failed to
heave on swell, that row reddens and this brief's central claim dies with it.
