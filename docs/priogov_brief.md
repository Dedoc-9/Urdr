<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: priogov-priority-fair -->
# `priogov` — design brief (URDROPC3, T3.31, MMO Stage H)

**Read**: 2026-08-04, the centrality-ordered READ pass — P27 of batch 7
(`../exe_epistemics/PREDICTIONS.md`), **the convergence-gating joint**. Outcome: **C-ORD** — a
certified priority ORDER, not a govern-variant, and the frozen mint condition fired: **the scheduling
axis MINTS** (govern carrier 1 + priogov carrier 2), the arc's second minted seam family after
approximation. Reading grade: **CONFIRMATION**.

## What it is

**The priority work governor** — the OPC family's third member (`opcost` measured the work, `govern`
enforced a FIFO per-tick budget, `priogov` admits a PRIORITY prefix). Each actor carries a base
priority; per tick the effective priority is `base + age_step * wait`, so a deferred actor climbs the
order the longer it waits. The tick admits the highest-effective-priority prefix that fits the
op-budget and defers the rest. Priority decides WHO goes first; aging guarantees EVERYONE goes.

## The core law (what `priogov-priority-fair` certifies)

**Priority buys order, never exclusion.** With fresh priorities the top actor is served on tick 1 and
the lowest last, in a priority-ordered PREFIX — no lower-priority actor ever jumps a deferred higher
one. And NO-STARVATION: because aging raises a waiter's effective priority without bound, every actor
is served in ≤ N ticks (each tick admits ≥ 1, so `drain_prio` serves N actors in ≤ N ticks). The
`priogov_digest` binds the per-actor served schedule, so a defect in the ORDER moves it — the order is
MEASURED, not an uncertified policy knob. `priogov-never-overrun` preserves govern's cost law (every
admitted tick's work ≤ budget); `priogov-refuse` makes a single over-budget actor a hard
`OPCOST-REFUSE`. Refuse-or-defer, never overrun; prioritise, never starve.

## The seam (P27's finding, and the mint)

A CERTIFIED ORDER with a bounded wait — distinct from `opcost`'s cost-ENVELOPE (a bound on total
work) and `govern`'s CONSERVATION (admitted + deferred == all). This is exactly what the frozen mint
condition required: work admitted in a certified order (priority provably honoured, digest-bound), not
merely bounded or conserved. `govern` (P10, the scheduling-axis first sighting) and `priogov` (the
certified-order carrier) are the two independent preregistered carriers the approximation axis's mint
rule demanded — so **the scheduling axis mints**, the arc's second seam family. The unnamed gem is
that aging converts a priority *preference* into a liveness *guarantee* structurally — the fairness is
not a tuned anti-starvation patch but a consequence of unbounded effective-priority growth — and the
clean-PREFIX discipline (a non-fitting actor stops the tick, it is not skipped for a lower one) keeps
the schedule a priority prefix rather than a budget-filling packing.

## does_not_show

WALL-CLOCK (this bounds WORK per tick; the time bound is `bench.py`'s, MEASURED-on-named-host);
strict priority WITHOUT aging (that CAN starve — this deliberately ages to bound the wait);
pre-emption mid-actor; a budget-filling (skip-and-continue) packing (this keeps the clean priority
prefix). A certified order is not a *fair* policy — priority is DECLARED per actor; priogov certifies
only that the declared priority is honoured and no one starves. `integrity ≠ truth`.

## Falsifier

This brief cites `priogov-priority-fair`: the fresh priority order (top served tick 1, lowest last, a
priority-ordered prefix) plus no-starvation (all served ≤ N via aging). If a lower-priority actor ever
jumped a deferred higher one, or any actor's wait exceeded N ticks under aging, that row reddens and
this brief's central claim — and the scheduling axis's second carrier — dies with it.
