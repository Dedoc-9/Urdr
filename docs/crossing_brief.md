<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: crossing-properties -->
# `crossing` — design brief (URDRCROSS1, T3.7, wave-crossing timing)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P38 of batch 10
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 11**. Outcome: **C-EQ**; the
author's leading credence (C-INV 32) lost to C-EQ at 30 — a two-point miss, and one whose cause is
recorded below because it cuts against cross-joint learning. Reading grade: **CONFIRMATION**.

## What it is

**When does a traveller crossing a live sea get overtopped?** An agent moves across the certified
wave field on a fixed velocity, and the question is the TICK at which the water first comes over it.
The field is not a backdrop: it evolves while the agent travels, so the answer depends on the
interaction of two motions — the wave's and the walker's.

## The core law (what `crossing-properties` certifies)

**The trace IS `wavefield.height` at the MOVING cell and tick.** That identity is the whole
correctness claim: the agent samples the field along its trajectory, at the tick it is actually there
— not a snapshot, not the field at the start cell. The result is then the **FIRST overtop**, and
**clearance is load-bearing** (one path clears at a high threshold and swamps at a low one, so the
predicate distinguishes something — L61's non-vacuity discharged inside the row).

`crossing-selftest` is what pins the identity down: **freezing the wave (every tick evaluated at
t = 0) changes when the agent is overtopped**, so TRAVEL is load-bearing and a static-field
implementation is a detectably different module. `crossing-refusal` is total and typed (6/6
`CROSS-REFUSE`: zero velocity · leaves grid · window ≤ 0 · bool · non-int start · bad velocity).

## The seam (P38's finding, and an honest negative about learning)

**The prior was updated from a resolved joint, and the update hurt.** The freeze explicitly moved
weight toward C-INV because P34 (`buoyancy`) had just taught that this foundation layer certifies
*brackets characterizing measured answers* rather than identities, and that "exact" names the
arithmetic rather than the semantics. That lesson was real and it transferred badly: `buoyancy`'s
central row is a two-sided inequality (Δ(z\*) ≥ W > Δ(z\*+1)); `crossing`'s is an **equality** (the
trace equals the field sampled along the moving path). Same layer, same "exact integer" vocabulary,
genuinely different shape. The disclosure stands as recorded — using a closed joint to price a later
freeze is legitimate learning, not contamination — but here it moved the credence the wrong way, which
is a datapoint about the *value* of that learning rather than about its propriety. What both modules
DO share is the question/answer split: the answer (a tick, a waterline) is MEASURED and never refused;
the typed refusals guard only the domain.

## does_not_show

Real hydrodynamics or wave physics — the field is `wavefield`'s DECLARED model and this is its
consumer; the agent's survival, buoyancy or swimming (that is `buoyancy`'s territory, a sibling not a
dependency); non-linear paths or variable velocity (a fixed velocity is the certified case);
sub-cell positions; wall-clock. A certified overtop tick is what this model says, computed exactly —
never a claim about a real crossing. `integrity ≠ truth`.

## Falsifier

This brief cites `crossing-properties`: the trace equalling `wavefield.height` at the moving cell and
tick, the result being the FIRST overtop, and clearance being load-bearing. If the trace ever sampled
a static or start-cell field, or the result returned a later overtop than the first, or the clearance
threshold distinguished nothing, that row reddens and this brief's central claim dies with it.
