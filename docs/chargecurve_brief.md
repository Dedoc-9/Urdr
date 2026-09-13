<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: chargecurve-scoring -->

# `chargecurve` (URDRCHG1) — design brief

*The shipped falsifier, taken at its word, would have adopted the peak.*

## Observe

`cohort` ships the budget charge `B // max(k, 1)` — monotone, not peaked at `k = 1` — and has been
honest about it for several rungs. The criticality peak borrowed from statistical mechanics is *not
adopted*, and the stated reason is that it was never measured: "the measurement ruled out the peak"
would be an inflation, monotone is the conservative default in the absence of the measurement, and
the falsification protocol is written down.

> Measure end-to-end verification cost against `k` on a real corpus; if cost is maximal at `k = 1`
> rather than at `k = 0`, the peaked charge is the correct schedule and this constant is wrong.

Stated, and **unrun**, for several rungs. One commit ago `cohort` registered C1–C5 against it, with
the classifier, so the rule could not be chosen once the numbers arrived. This is the measurement.

## Orient

**The measurand is counted, never timed.** Wall clock is MEASURED-on-named-host here and ungated by
rule, so a timing curve could not enter a gate at all. Two components, and they are *not* summed:

| component | what it counts | instrument |
|---|---|---|
| decision cost | `free_reaches` evaluations `min_cut` performs | the shipped `free_reaches` is wrapped and counted |
| protocol cost | peers `verify_cohort` fetches | `verify_cohort`'s own return value |

Fusing them would need a weight, the weight would be chosen, and **the chosen weight would decide
the shape**. Both instruments run the shipped procedure rather than a re-implementation of it: a
falsifier that does not run the thing it measures guards a copy.

**The peer fixture is derived, not invented.** `cohort.peer_population` takes a *thickness*, so it
cannot express a breached submitter — the `k = 0` point. `peers_for` takes an *occupancy* and applies
the same construction, proved identical on every wall where both are defined. That extension is what
exposed C2.

## Decide

**What the panel says.**

| k | decision | protocol | outcome | schedule |
|---|---|---|---|---|
| 0 | 1 | 5 | `COHORT_VERIFIED` | 12 |
| 1 | 2 | **6** | `COHORT_FAILED` | 12 |
| 2 | 49 | 5 | `COHORT_VERIFIED` | 6 |
| 3 | 1778 | 5 | `COHORT_VERIFIED` | 4 |

Through the frozen classifier: decision `NEITHER`, protocol `PEAKED`, schedule `MONOTONE`.

**And there is the trap.** The protocol component *is* maximal at `k = 1`. The shipped one-line
protocol, read with these numbers in hand and nothing to answer to, adopts the peaked charge. It
should not, for two reasons that a committed prediction makes natural to state and a post-hoc reading
makes easy to skip:

- the component that peaks is **not the one the schedule is a schedule for**; and
- the `k = 1` reading is a **failed verification exhausting the peer list**, not a dearer success.

Restricted to the members whose outcome is the same, the protocol cost is flat — 5, 5, 5.

> The inflation was available, cheap, and one sentence away. That is the whole value of having
> registered a family rather than the metaphor.

**The dispositions.**

| id | verdict | why |
|---|---|---|
| C1 | HELD | decision cost rises, classified `NEITHER`; `min_cut` returns at the first opening size, so certifying gap `k` contains refuting every smaller one |
| C2 | **MISSED** | protocol cost is not constant — 6 at `k = 1` |
| C3 | HELD | the two components land in different registered classes |
| C4 | HELD | the schedule matches neither; it is a **policy**, not a model |
| C5 | HELD | holding `k = 2` and moving the world 4 → 5 moves the decision cost 49 → 76 |

**C2's miss is the useful one.** It registered a constant protocol cost *because the population's
capture noise lies below the gap*. At `k = 1` there is no below-gap noise to have: the sub-gap set is
empty (`cohort`'s census runs over `range(1, max(k, 1))`), all 16 one-cell peers sit **at** the gap
where that module's own law says disagreement is possible, all 16 disagree, agreement never reaches
the threshold, and the loop exhausts the list. The record flagged C2 as most likely a fixture
artifact — and it is one, in the direction of the fixture being *under-specified* rather than
over-tuned, which is not the direction that was feared.

**C4 was the arm that could refute the registration, and it did not.** The schedule matches neither
measured component, so `B // max(k, 1)` is a policy rather than a model of cost. That licenses
**relabelling** it and nothing more. `BASE_CHARGE` is untouched by this rung: the measurement says
what the charge is *not*.

## Act

Register → interval → measurement → disposition, in consecutive commits, with the classifier frozen
in the registering commit. That is the instrument running once end to end, and it is what
`disposition` v1.1 and `ratchet` were repaired to permit rather than merely to tolerate.

`does_not_show`. That the charge is the **right** policy — C4 says what it is not and leaves what it
ought to be untouched. That these are the **only** costs that matter: a deployment's are latency and
bytes, and neither is countable in a byte-identical gate. That the peak is absent in any system other
than this one — the corpus is synthetic and `k` is confounded with wall volume **by construction**,
which C5 measures rather than waves away. And nothing at all about whether a **different peer
fixture**, one carrying genuine below-gap noise at `k = 1`, would leave the protocol cost flat. That
is the obvious next question and it is not answered here.
