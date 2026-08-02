# Continuous fixed-point movement (URDRGLIDE1, Stage B): a design pass

<!-- brief-falsifier: glide-refinement -->

`glide` is the continuous mover under the whole snapshot/storage/recovery chain — the module three later
briefs cite as their "never-died reference." Where `drive` folds an input log into whole-cell integer poses,
`glide` folds the SAME log into Q32.32 sub-cell poses (the actor glides between cells instead of snapping),
division-free — and its command-boundary poses, floored to cells, reproduce `drive`'s certified trajectory
BIT-FOR-BIT. The continuous regime provably CONTAINS the discrete one: `drive ⊑ glide`.

## OODA

**Observe.** `drive` certifies whole-cell movement, but the actor needs a SUB-CELL position to render between
cells. The naive refinement introduces floating point and a NEW source of truth that can drift from `drive`'s
certified grid — a second movement authority that has to be reconciled with the first. The question: can the
resolution be refined below the cell WITHOUT leaving the certified regime and WITHOUT introducing division?

**Orient.** Fixed-point, radix `ONE = 2^32` (the FIELDFP substrate). A subdivision `sub = 2^k` makes one
micro-step `ONE >> k` — an EXACT shift — so `sub` micro-steps sum to EXACTLY one cell: no rounding, no `/`,
`//`, or `%`. Position floors to a cell by `fx >> 32`; the ground under the actor is the exact floor-sampled
cell height. The refinement is a strict CONTAINMENT — the fine regime may visit only cells the coarse one did.

**Decide — the refinement bridge (`drive ⊑ glide`).** `glide`'s command-boundary poses, floored to cells,
reproduce `drive`'s certified trajectory bit-for-bit, for EVERY input log and EVERY subdivision. At `sub = 1`
`glide` IS `drive` lifted to fixed-point (it floors to the identical path); at `sub = 2^k` it interpolates k
levels finer without ever leaving a cell `drive` did not visit. The continuous regime inherits every certified
fact about the grid transcript rather than re-proving it.

**Act.** Rows: `glide:scenes`, `glide-refinement`, `glide-subcell`, `glide-refusal`.

## The laws

1. **The refinement bridge, exact and exhaustive** (`glide-refinement`): floored `glide` cell-samples EQUAL
   `drive` over a grid of every two-command log (64 per field) across two fields at all five subdivisions —
   hundreds of cases, not a spot check. The continuous regime contains the certified discrete one, so `glide`
   INHERITS `drive`'s certification instead of re-earning it. This is why the storage chain can treat a glide
   boundary pose as authoritative state.
2. **Division-free by construction.** One micro-step is `ONE >> k`, an exact shift; `sub` of them sum to exactly
   one cell. There is no `/`, `//`, or `%` anywhere in the fold, so the refinement cannot introduce a rounding
   drift — it never rounds.
3. **The sub-cell wall** (`glide-subcell`): a glide into a too-high ridge stops one micro-step short and floors
   to `drive`'s wall stop — `glide` cannot vault a wall `drive` refused — and a 16×-finer subdivision reaches no
   cell the coarse traversal did not. The wall is the continuous echo of the grid wall, measured.
4. **Determinism and tamper-evidence, with the subdivision bound** (`glide-refusal`): replaying `(start, log,
   sub)` reproduces the trajectory bit-for-bit, and the digest binds `(start, log, sub, trajectory)` — so a
   forged or reordered command, OR a changed subdivision, moves it. Domain violations are typed `GLIDE-REFUSE`
   (unknown command, empty log, off-grid start, non-power-of-two subdivision): refuse, never clamp the path or
   invent a footing.

## The scar it keeps (why the type guard is a law)

`glide`'s `_shift` records a fixed defect, and the brief keeps it because it explains a law. A membership test
alone admitted `True`, because `True == 1` and `1 ∈ SUBDIV`; measured before the fix, `sub = True` produced a
trajectory IDENTICAL to `sub = 1` but a DIFFERENT digest — one behaviour with two content identities, which is
content-identity (L1) broken at the exact point the module claims tamper-evidence. The load-bearing fix is a
type guard that excludes `bool`. The tamper-evidence law is only as strong as the type discipline beneath it,
and this module names the place that was once true.

## The glyph verdict: NO new glyph (kernel frozen)

`glide` folds over the FROZEN field (the FIELDFP radix `ONE`), `stance`'s step law, and `heightfield`'s
authority. URDRGLIDE1 is a content-address digest that binds `(start, log, sub, trajectory)`, not a new semantic
witness class — correctness is witnessed by equality to `drive`'s frozen certification. No core is touched; D1
§20 is not engaged.

## Honest scope & boundaries (does_not_show)

It makes NO timing claim: the movement MODEL — constant sub-cell speed, turn-then-advance, floor-sampled ground,
a rise above MAX_STEP walls — is DECLARED, like `drive`/`stance`. It does not show SMOOTH height interpolation
(bilinear over the four corner cells is the DECLARED presentation regime; the floor-sample is the measured
authority here). It does not show CONTINUOUS facing (mouse-look is the Q32.32 `fpquat`/`fpface` rotation, a
separate regime, not this discrete turn), nor sub-cell START poses (the actor begins cell-aligned), nor diagonal
movement. Continuous PREDICTION reconcile (`glide ∘ predict`) is a later slice, deferred to `predict`, not
claimed here.

## Where this sits

The foundation of Stage B: above `drive` (the certified discrete transcript it refines), `stance` (the step
law) and `heightfield` (the authority); below `splice` (glide RESUMPTION — the memoryless property that a
boundary pose fully determines the future) and the whole snapshot/storage/recovery chain. `storecost` serializes
`glide`'s boundary poses; `persist` makes them durable; `resurrect` and `rollstore` resume from them. `glide` is
the pure function of `(start, log, sub)` that a dead process and its successor compute identically — the
"never-died reference" those briefs measure against.
