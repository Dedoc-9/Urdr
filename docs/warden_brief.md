<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: warden-refusal -->
# `warden` — design brief (URDRWARD1, T3.24, MMO Stage E opener)

**Read**: 2026-08-04, the centrality-ordered READ pass — the **fourth brief written blind against a
frozen pre-registration** (P4, `../exe_epistemics/PREDICTIONS.md`), the first frozen under an
exhaustive outcome partition (L60). Outcome: **CONFIRMED-MODEL (W-C0)**, meta **M-0** — the first
decidable second-order verdict. Reading grade: **CONFIRMATION** — the module is what its rows certify.

## What it is

**Structural anti-cheat**: a claimed trajectory or position is ADMITTED or typed-REFUSED —
reconstruct-or-refuse turned against the cheater. A claim that could not have happened is not smoothed
or flagged with a heuristic; it is a certified refusal. Two orthogonal certificates, both exact and
division-free:

- **KINEMATIC** (certifies claimed *paths*; composes the mover): each claimed step must be a legal
  move — cardinal, one or two cells (walk/sprint gait), every sub-step enterable under the step law
  (`Δground ≤ MAX_STEP`, matching `drive`/`glide`). A diagonal or >2-cell jump is `WARD-TELEPORT`; a
  step that climbs a wall is `WARD-TUNNEL`. An honest `glide` trajectory always admits.
- **TOPOLOGICAL** (certifies claimed *states*; composes the homology witness): the walkable field
  decomposes into connected components — β₀ = rank H₀, the same invariant `URDRPD1` computes as
  persistent homology, here taken directly over the walkable graph (an undirected edge joins adjacent
  cells iff the step is legal both ways). A bare position claim in a different component from the
  anchor is `WARD-UNREACH` — refused **from the field alone, with no trajectory to inspect**: the
  cheat a per-tick replay cannot cheaply catch.

## The core law (what the rows certify)

Admit-or-typed-refuse, in both certificate axes: `warden-kinematic` (honest walk + honest glide admit;
tunnel and teleport refused), `warden-topological` (β₀ = 3 on the barrier world — the wall genuinely
splits it, the refusal is non-vacuous; a same-side position stays reachable), and `warden-refusal` —
the total typed battery: 4/4 sub-codes (`WARD-TUNNEL` · `WARD-TELEPORT` · `WARD-UNREACH` ·
`WARD-MALFORMED`) under the single `WARD-REFUSE` code. `warden:scenes` pins the honest and
teleport-across scenarios to URDRWARD1 digests binding β₀ and the verdict.

## The seam (P4's finding)

**Admission-of-claims, confirmed — and the refuse/measure split's first predictive success.** P3's
residual (walls *measure* an honest walk; refusal guards only the domain) was used predictively in
P4's freeze: warden polices *claims*, so violations must *refuse*, typed. The rows confirm it exactly.
The pair is now sharp: `stance` measures where terrain blocks a walk it admitted; `warden` refuses a
claim the terrain could never have produced. Same step law, two epistemic roles — the answer is
measured, the question is policed. What the freeze did not name (the M-0 half): the two certificates
are *orthogonal by claim type* — kinematic for paths, topological for bare states — so the anti-cheat
covers the claim a replay can check and the claim it cannot.

## does_not_show

DIRECTED reachability (components are undirected mutual-reachability; a one-way descent off a cliff is
a strongly-connected refinement, a named follow-on); gaits beyond sprint (moves > 2 cells/tick); the
URDRPD1 homology cross-placement (β₀ is computed directly here; wiring `homology_c/rs` to the warden
is a named follow-on); wall-clock cost (`bench.py`). And the brief does not upgrade the model: WHO is
honest is never certified — only whether a *claim* is consistent with the terrain's law. A green
warden certifies refusal of the impossible, not detection of all cheating. `integrity ≠ truth`.

## Falsifier

This brief cites `warden-refusal`: the total typed battery. If a tunnel, teleport, unreachable
position, or malformed claim stopped refusing — or refused untyped — the anti-cheat would be admitting
cheats, that row reddens, and this brief's central claim dies with it.
