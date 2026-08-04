<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: govern-never-overrun -->
# `govern` — design brief (URDROPC2, T3.30, MMO Stage H)

**Read**: 2026-08-04, the centrality-ordered READ pass — P10 of the first batch freeze, declared
**NON-SCORING** before the seal broke: this module's gate-stage docstring had been read during an
earlier rung (it sits directly below `opcost`'s), so its core law was already exposed and its
resolution moves no tournament weights. The brief pass proceeds; the epistemics abstain. Reading
grade: **CONFIRMATION**.

## What it is

**The per-tick work governor**: the `opcost` envelope turned into live enforcement. Given a
per-tick op-budget, `admit_tick` admits a FIFO prefix of the actors whose cumulative work fits the
budget and defers the rest to the next tick — no network, no chunking, no external infrastructure;
the self-contained sequel to the latency envelope. `actor_cost` is one actor's exact `opcost`
contribution (glide micro-steps + admit sub-steps); `drain` iterates admission to completion. All
exact integer op-counts; the whole governor reproduces bit-for-bit.

## The core law (what the rows certify)

**Refuse-or-defer, never overrun; serve-in-order, never starve.** `govern-never-overrun`: every
admitted tick's spent work ≤ budget across budgets a…100a — the live latency guarantee (wall-clock
follows only via `bench.py`'s host-tagged per-op cost). `govern-refuse`: a single actor whose cost
alone exceeds the budget is a hard `OPCOST-REFUSE` — an impossible request refused outright, never
left to starve a queue — and admitted + deferred == all actors, in order (conservation: none lost,
duplicated, or reordered). And `govern-progress-wait` certifies genuine **scheduler laws**:
progress (with the over-budget filter, the first queued actor always fits, so every tick admits
≥ 1 — no deadlock) and bounded-wait (drain serves N actors in ≤ N ticks; an actor at queue position
p waits at most p ticks — FIFO fairness, no starvation). `govern:scenes` pins three schedules to
URDROPC2 digests.

## The seam (P10's finding — recorded, not scored)

The envelope-enforcement half is the cost pattern, as the contaminated prediction expected. The
notable content is `govern-progress-wait`: progress, bounded-wait, and fairness are **scheduling
laws** — liveness properties of an allocator — and no basis in the tournament carries a scheduling
axis. First sighting recorded for checkpoint 3; a second independent sighting would make the axis
mintable (L3). Conservation (admitted + deferred == all) echoes budget's descent bookkeeping — the
composition signature again, on actors instead of cells.

## does_not_show

Wall-clock enforcement (this bounds the WORK a tick issues, not the time the OS gives it — no
guarantee under an adversarial scheduler). Priority / weighted fairness (this is FIFO; `priogov` is
the follow-on). Pre-emption mid-actor (an actor is admitted whole or deferred whole).
`integrity ≠ truth`.

## Falsifier

This brief cites `govern-never-overrun`: the live latency guarantee. If an admitted tick's work
ever exceeded its budget, that row reddens and this brief's central claim dies with it.
