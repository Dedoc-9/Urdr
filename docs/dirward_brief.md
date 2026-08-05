<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: dirward-insufficient -->
# `dirward` — design brief (URDRWARD3, T3.26, directed-reachability anti-cheat)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P40 of batch 11
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-R**, the author's leading credence (38) correct.
Reading grade: **CONFIRMATION**.

## What it is

**The deferred boundary, closed.** `warden`'s own `does_not_show` named this rung at P4: its
topological certificate used UNDIRECTED (mutual-reachability) connectivity, and directed reachability
was explicitly deferred. Terrain is not symmetric — an agent can descend a cliff it cannot climb — so
an undirected model necessarily conflates "you cannot get there" with "you cannot get *back*".

## The core law (what `dirward-insufficient` certifies)

**The undirected warden fails in BOTH directions at once, and this rung separates them.** It
**FALSE-REFUSES the legal descent** — a legitimate move rejected, which is worse than a miss — and it
returns **one `WARD-UNREACH` for both a one-way cliff and a genuine wall**, conflating two physically
different situations. `dirward` admits the descent and **separates `WARD-ONEWAY` from `WARD-UNREACH`**.
`dirward-admission` holds the law: the descent admits, the climb-back is `WARD-ONEWAY`, a genuine wall
is `WARD-UNREACH`, an honest glide descent admits kinematically. `dirward-asymmetry` supplies the
structure underneath: directed reach is genuinely asymmetric on the cliff, and **collapses to 0 with
`num_scc == betti0` on flat terrain** — the directed measure reduces exactly to the undirected one
where the terrain is symmetric, so the refinement is a strict generalization rather than a rival.

## The seam (P40's finding)

**A refusal that says WHICH KIND — the discriminability-of-refusal axis's SECOND SIGHTING.** `geoquorum`
(P21) resolved C-SPLIT on exactly this shape: two refusals that are categorically distinct
(UNAVAILABLE for coverage vs FAILED for integrity), recorded then as a candidate axis to WATCH rather
than mint. `dirward` carries it again — `WARD-ONEWAY` vs `WARD-UNREACH` is the same move, a typed
sub-reason that turns one verdict into two. **It is recorded here as a SIGHTING, not a mint**: the
axis was not named in this joint's frozen partition, so under L3 a post-hoc recurrence cannot promote
it. A mint requires a FUTURE FROZEN prediction that names the axis in advance — the same bar the
approximation axis had to clear at checkpoint 4. The other recurrence is the **insufficiency proof**,
the second in two rungs (`crosswarden`, `dirward`): the weaker predecessor is run against the same
cases and shown failing, so necessity is measured rather than argued. And the flat-terrain collapse is
the `clslo` move again — a refinement that reproduces its predecessor at the degenerate case, checked
rather than claimed.

## does_not_show

Intent or attribution (structural, as everywhere in this family); dynamic terrain (the reachability
graph is computed on a fixed field); wall-clock; the cost of the SCC computation at scale; anything
about an exploit inside a single strongly-connected component (there, directed and undirected agree by
construction, and this rung adds nothing). Separating ONEWAY from UNREACH says which *kind* of
impossibility holds, never that the claimant was honest. `integrity ≠ truth`.

## Falsifier

This brief cites `dirward-insufficient`: the undirected warden false-refusing the legal descent and
returning one `WARD-UNREACH` for both a one-way cliff and a wall, while `dirward` admits the descent
and separates the two codes. If the undirected check ever handled both cases correctly — removing the
reason this rung exists — or `dirward` conflated ONEWAY with UNREACH, that row reddens and this
brief's central claim dies with it.
