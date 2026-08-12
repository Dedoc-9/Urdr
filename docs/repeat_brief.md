<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: repeat-levels -->
# `repeat` — design brief (URDRRPT1)

## The hole `confound` could not see

`confound` balanced the treatment axis against run position *inside one execution*. It says nothing
about the execution itself.

`rollbench` times each cell 200 times and reports p50, p95, p99. Every one of those is a
**within-execution** quantile: 200 samples of iteration-level variation, and exactly **one** sample
of everything an interpreter fixes at startup — the hash seed, the address-space layout, where the
allocator began, which core the scheduler chose.

> **More iterations inside one execution cannot reduce execution-level variance.**

Not "reduce it slowly". Cannot. The quantity is not being sampled, so `n` grows and the interval
that matters does not move. `pyperf` spawns separate worker *processes* for exactly this reason:
address-space randomisation and hash randomisation vary per process and are invisible from inside
one.

## The law

> **A difference smaller than the between-execution spread is not a difference. With one execution
> the between-execution spread is unknown, and no difference can be claimed at all.**

## Three verdicts

`SEPARATED` — the gap between the per-execution medians exceeds the spread of those medians.
`INDISTINGUISHABLE` — it does not, and reporting it would be reporting the noise floor.
`UNDETERMINED` — fewer than two executions, so the spread **does not exist**.

`UNDETERMINED` is not a polite `INDISTINGUISHABLE`. Answering `INDISTINGUISHABLE` on one execution
would claim to have looked. **Every timing this repository has produced, including both admissible
host logs, is `UNDETERMINED` under this law.** The numbers are real, the schedule has been balanced
since URDRCNF1, and whether any gap survives a second process has never been asked.

## The verdict moves with the spread, not the gap

Same 50 ns gap, two different execution spreads:

| per-execution offsets | spread | verdict |
|---|---|---|
| 0, 1, 2 | 2 | `SEPARATED` |
| 0, 500, 1000 | 1000 | `INDISTINGUISHABLE` |

Without that check this would be a threshold on the difference wearing a statistical name.

## Exact arithmetic

Medians take the **lower** of the two middle values on an even count — declared, not left to a
float. Nothing in the module divides, asserted on the source: a benchmark law that introduced its
own rounding choice would be an odd thing to trust.

## `does_not_show`

**The spread of a few executions is not a confidence interval.** No distribution is computed or
assumed and no p-value is offered. With three executions this is a weak instrument that can only be
more conservative than the truth, never less.

And it grades only what it is handed. A factor constant across every execution — the machine, the
interpreter build, the working directory — is invisible here exactly as run position was invisible
before `confound`. Mytkowicz et al. measured such factors at 2–8% on their own.

## Grade

**MEASURED** — one execution reads `UNDETERMINED` whatever the gap; multiplying iterations by 100
does not change that; effects below and above the floor read `INDISTINGUISHABLE` and `SEPARATED`;
empty and ragged inputs refuse. **DECLARED** — that the between-execution spread is the *range* of
per-execution medians, the most conservative choice available without assuming a distribution.
