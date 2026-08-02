# Glide resumption (URDRSPLICE1, Stage B): a design pass

<!-- brief-falsifier: splice-equivalence -->

`splice` proves `glide` is ROLLBACK-ABLE: a glide's future depends only on its current Q32.32 pose, not on the
history that produced it. That memorylessness is the primitive continuous rollback-replay is built on — and it
is the exact law `resurrect` and `rollstore` carry through death, so a dead process can keep an agreed prefix and
re-simulate only the tail.

## OODA

**Observe.** `glide` certifies the full trajectory from a cell-aligned start, but a rollback needs to RESUME from
a mid-trajectory point — keep the agreed prefix, re-simulate only the tail. That is sound only if a boundary pose
fully determines the future; if it does not, a resume has to replay from the start, and continuous rollback is
not a primitive but a full re-glide.

**Orient.** The fold's invariant is `cx = fx >> 32` — the current cell is re-derived from the pose, so a glide
folded from an arbitrary `(fx, fy, facing)` is fully defined without the path that reached it. The future is a
pure function of the pose. That is the memoryless property, and it is what makes a mid-trajectory boundary a
legitimate place to cut.

**Decide — splice equivalence.** For every log, every interior split `at`, and every subdivision,
`splice` — glide the prefix `cmds[:at]`, then RESUME the suffix `cmds[at:]` from the boundary pose — reproduces
`glide_cells(full)` BIT-FOR-BIT: `glide(start, cmds) == glide(start, cmds[:at]) ++ resume(boundary_at,
cmds[at:])`. At continuous sub-cell resolution, and crucially including a resume from a SUB-CELL wall-stopped pose
mid-cell, not only cell-aligned cuts.

**Act.** Rows: `splice:scenes`, `splice-equivalence`, `splice-memoryless`, `splice-refusal`.

## The laws

1. **Splice equivalence, exact and sub-cell** (`splice-equivalence`): `splice == glide_cells(full)` over every
   three-command log crossed with every interior split across two fields — hundreds of cases — and the sweep is
   NON-VACUOUS: a measured, nonzero number of those resumes begin from genuinely FRACTIONAL wall-stopped poses
   (fx or fy not cell-aligned). Resumption is not limited to cell boundaries, which is exactly what a continuous
   rollback needs. This is the falsifier the whole recovery chain leans on.
2. **The future is a function of the pose** (`splice-memoryless`): two different histories that reach the SAME
   pose share their future exactly, and the spliced continuous trajectory still floors to `drive` — resumption
   composes with `glide`'s refinement bridge. The pose is a sufficient statistic; the path is discarded without
   loss.
3. **Refuse, never invent a boundary** (`splice-refusal`): a moved split moves the digest (the cut is bound);
   an off-grid or non-integer resume pose, a bad facing, and a non-interior split (at 0 or at `len`) are typed
   `SPLICE-REFUSE`. `splice` speaks with one voice — it reuses `glide`'s grammar checks but converts their
   `GLIDE-REFUSE` — refusing rather than clamping the pose or inventing a boundary.

## The glyph verdict: NO new glyph (kernel frozen)

`splice` reuses `glide`'s FROZEN fold (`_fold_from`); it adds no movement rule, only the resume ENTRY point.
URDRSPLICE1 binds the resumed trajectory to its cut, and correctness is witnessed by equality to `glide` — no new
semantic witness class, no core touched. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It does not show the client-prediction RECONCILE itself: localizing the mispredict tick and choosing the rollback
point is `glide ∘ predict`, a later slice deferred to `cpredict`. This rung certifies only that the rollback,
once chosen, reconstructs exactly. It inherits `glide`'s own boundaries unchanged — no smooth interpolation, no
continuous facing (the `fpquat`/`fpface` regime). And it makes NO timing claim.

## Where this sits

Directly above `glide` (the mover it resumes) and below `cpredict` (continuous prediction reconcile, which
chooses the rollback point) and the whole recovery chain: `resurrect`'s `resume_from` and `rollstore`'s replay
ARE this memoryless property carried through a process death. `splice` is the law that makes "keep the prefix,
re-simulate the tail" exact rather than approximate.
