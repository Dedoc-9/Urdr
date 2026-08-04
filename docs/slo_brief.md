<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: slo-soundness -->
# `slo` — design brief (URDRLAT2, T3.33, MMO Stage H)

**Read**: 2026-08-04, the centrality-ordered READ pass — P29 of batch 7
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 8**. Outcome: **C-PRICE** — the
Stage-H latency closer, the cost/latency family's fourth preregistered instance. Reading grade:
**CONFIRMATION**.

## What it is

**The end-to-end latency guarantee as ONE certified number.** This is where the Stage-H arc closes:
`opcost` measured the work, `govern`/`priogov` enforced a per-tick budget, `horizon` bounded the
rollback window — `slo` composes them into a single worst-case latency and a `SLO-REFUSE` for a config
that would over-promise. An actor's end-to-end latency in ticks has two bounded parts: the ADMISSION
WAIT (from the governor: under budget B and per-actor cost c, each tick admits `floor(B/c)` actors, so
N drain in `ceil(N / floor(B/c))` ticks) and the RECONCILE WINDOW (the rollback horizon H). Their sum
is the worst-case, and it is an UPPER BOUND that is SOUND.

## The core law (what `slo-soundness` certifies)

**The bound is a real guarantee, not an optimistic estimate.** `slo-soundness` checks the governor's
ACTUAL maximum drain-wait against the `admission_wait` formula over a config corpus and confirms the
formula never under-bounds it — the number is sound over-approximation, so a client can be promised it.
`slo-composition` certifies the exact identity `worst_case_latency == admission_wait + rollback
window`; `slo-refuse` makes `slo_admit(config, target)` ADMIT iff `worst_case ≤ target`, else
`SLO-REFUSE` — a config that cannot meet its target is declined, never quietly accepted. A promise is
kept or declined, never broken. Reduce N, raise the budget, or shrink the horizon until it fits.

## The seam (P29's finding)

A composite worst-case BOUND with a refuse — the cost/latency family's fourth preregistered instance
(`opcost`, `horizon`, `govern`, `slo`), v_D=0, no new family. Two supporting characters, neither
minting: the composition is an EXACT identity (a C-EQ-flavored assembly — the worst case is exactly the
sum of its two bounded parts), and the soundness is the APPROXIMATION axis touched a fourth time
(`admission_wait` over-approximates the actual drain, so it never promises too little). Notably `slo`
uses the FIFO governor's UNIFORM bound, NOT `priogov`'s per-class order (stated in its does_not_show) —
so it is NOT a scheduling-ORDER carrier, and the run-8 census reads v_D = 1,0,0 with priogov the sole
mint.

## does_not_show

WALL-CLOCK latency (this is in TICKS; wall-clock per tick is `bench.py`, MEASURED-on-named-host —
multiply to get seconds); jitter / variance (this is the WORST-CASE bound, not a distribution);
priority-class latency (uses the FIFO governor's uniform bound, not `priogov`'s per-class one — a
follow-on); any guarantee under an adversarial OS scheduler. A sound worst-case bound is not a typical
latency — it is the ceiling a config will never exceed, not the time a tick usually takes.
`integrity ≠ truth`.

## Falsifier

This brief cites `slo-soundness`: the `admission_wait` formula upper-bounds the governor's actual drain
over the config corpus, and a within-target config admits. If the actual drain ever exceeded the
formula (the bound under-promising, so the guarantee is a lie), that row reddens and this brief's
central claim dies with it.
