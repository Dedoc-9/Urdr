<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: deeper-verdicts -->
# `deeper` — design brief (URDRDPR1)

## The instance

Under a balanced schedule the named host showed `moulded` beating `flat` at exactly one work level:

| workload | ticks | moulded vs flat |
|---|---|---|
| `all_grounded` | 8 | −5.2% |
| `alternating` | 8 | −2.9% |
| `frequent_landing` | 8 | −5.6% |

`flat` wins again at 11 and 12 ticks. Three independent workloads agreeing at one point is too
orderly to file as noise and too narrow to explain by hand.

And `measure` had already proved, **in exact counts**, that the three representations share a slope
and differ only in the intercept. A band that appears at one tick count and vanishes on either side
is a difference the op model says *cannot exist*.

That leaves two honest possibilities: something below the op model differs there, or the band is not
real. What is not available is a story.

> **Measure one level deeper, or record that you did not.**

## The law

> **A timing difference between two arms at the same condition is explained only if some counted
> quantity also differs there. With no counted difference, the verdict is `UNEXPLAINED`.**

## Three verdicts

`EXPLAINED` — a counted quantity moves where the time moves.
`UNEXPLAINED` — none does. The difference is real in the log and unaccounted for.
`NOT_ASKED` — no counts were carried at all.

`NOT_ASKED` is what every log in this repository looked like until now, and it is a **different
finding** from having looked and found nothing. Collapsing them would let an instrument that never
measured anything pass as one that measured and found no cause.

The symmetric case counts too: if the counts differ and the time does not, the model predicted a
difference that never appeared, and that is equally unexplained. An instrument watching only for
unexplained *slowness* would miss it.

## Where the counts live

`blocks`, `gc0`, `gc1`, `gc2` — allocated blocks and the three GC generation counts. These are
**CPython-version dependent**, and this gate runs on more than one interpreter, so digesting one
would redden an operator's gate for a reason unrelated to the tree.

They ride in the **log**, beside the timings, under exactly the rule the timings already obey: the
format and the admission law are gated, the numbers are the operator's. This module grades the
reasoning and never the counts. The gate asserts that no multi-digit run appears in the pinned
payload at all.

## The probe, and the bug its falsifier caught

`sys.getallocatedblocks()` is a **level, not a counter** — it reports what is allocated *now*. The
first draft of `count_delta` discarded the return value before the second snapshot, so every
transient allocation was already freed and the probe read **zero** for a callable allocating five
hundred objects, while reporting it confidently. A dead instrument says "no difference" exactly as
convincingly as a working one says the truth.

Holding the result across the snapshot fixes the reading and fixes the meaning at once: `blocks` is
the **resident** cost of the call, and `gc0` is the **churn** proxy. Reported apart, because they
answer different questions.

## `does_not_show`

**A counted difference is not a cause.** If allocations move where the time moves, that is a
correlation between two quantities in the same run, not a demonstration that one produced the other.
Establishing that needs an intervention — Mytkowicz's second remedy — which is not built here.

Nor is the counter list exhaustive. A difference living in branch prediction, cache residency or
scheduler placement reads `UNEXPLAINED` — correctly, because this instrument cannot see it, and
`UNEXPLAINED` is the accurate statement of that.

## Grade

**MEASURED** — all three verdicts planted separately and proved distinct, both directions covered,
the probe proved to bite, no count reaching a golden. **DECLARED** — the counter list, and that a
count differs when it differs at all: no tolerance, because a tolerance on an exact integer is a
threshold nobody is watching.
