<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: clslo-refinement -->
# `clslo` — design brief (URDRLAT3, T3.34, MMO Stage H)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P36 of batch 10
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-PRICE**, the author's leading credence (38)
correct. Reading grade: **CONFIRMATION**.

## What it is

**The per-CLASS worst-case latency SLO** — the follow-on `slo` named in its own `does_not_show`.
Where `slo` (P29) composes ONE certified number from the FIFO governor's uniform admission bound plus
the rollback horizon, this refines that guarantee per priority tier: a premium class and a free class
do not deserve the same promise, and a system that quotes one number for both is either
over-promising the free tier or under-selling the premium one.

## The core law (what `clslo-refinement` certifies)

**The refinement is monotone and it degrades correctly.** A higher-priority class carries a
**tighter-or-equal bound** — premium beats free — and the **one-class case reduces exactly to the
composite `slo`'s uniform number**, so the refinement is a strict generalization rather than a
replacement. `clslo-soundness` makes the bound real rather than optimistic: the per-class bound
**equals `priogov`'s actual per-class drain** over the config corpus (exact for equal-cost actors), so
the promise is derived from the scheduler that will keep it, not asserted alongside it.
`clslo-refuse` keeps the per-tier promise honest: a tier whose worst-case latency exceeds **its own**
target is `CLSLO-REFUSE`, named — a config cannot quietly meet the aggregate while failing a class.

## The seam (P36's finding)

**A price refined by class, not an order certified by class — and that distinction was the batch's
live mint risk.** The freeze recorded C-ORD as the outcome that would have given the scheduling axis a
third carrier and minted nothing otherwise. It did not fire, and the reason is structural: `priogov`
certifies the ORDER in which work is admitted; `clslo` certifies that the resulting BOUNDS respect the
class ordering (tighter-or-equal as priority rises). Monotonicity of prices across classes is not a
certified order, so the scheduling axis stays at two carriers. The reduction-to-`slo` clause is the
quiet gem: a refinement that does not reproduce its predecessor at the degenerate case is a different
guarantee wearing the same name, and this one is checked rather than claimed.

## does_not_show

WALL-CLOCK (ticks, as everywhere in the LAT family — `bench.py` is the host-tagged measurement);
jitter or distribution (this is the WORST case, not a spread); unequal per-actor costs beyond the
corpus (the drain equality is stated exact for equal-cost); starvation dynamics under adversarial
class assignment (who is assigned to which tier is policy, not law); any guarantee under an
adversarial OS scheduler. A per-class bound is a promise about *this configuration*, never a claim
that the tiers are fairly assigned. `integrity ≠ truth`.

## Falsifier

This brief cites `clslo-refinement`: a higher-priority class carries a tighter-or-equal bound, and the
one-class case reduces to the composite `slo`'s uniform number. If a lower-priority class ever carried
a strictly tighter bound than a higher one, or the single-class reduction diverged from `slo`, that
row reddens and this brief's central claim dies with it.
