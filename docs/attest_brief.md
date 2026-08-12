<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: attest-record -->
# `attest` — design brief (URDRATT1)

## The endpoint of the arc

`measure` fixed the terms of a performance claim eight rungs ago and structurally could not answer
it. `rollbench` built the instrument. `confound` found the schedule was measuring run position.
`repeat` found the numbers were never sampled at the level a comparison needs. `deeper` asked what
the op model could not see.

Here the answer stops being a paste in a conversation and becomes an artifact the gate re-reads on
every run.

## The law

> **A graduated claim cites a committed log that still seals, still grades admissible, and still
> supports the numbers the claim states — with those numbers derived from the log at claim time.**

Two halves, because a claim rots in two directions. Without the first it cites nothing and is a
sentence. Without the second the numbers are **typed**, and a typed number is a copy that drifts
from its source the first time anyone edits either — L64, the defect that turned a worked example
into a forgery under maintenance.

Nothing in the module states a figure. Every figure is recomputed from the sealed bytes when the
gate runs, and a falsifier asserts that no derived value appears as a literal in the source.

## The record is not the scratch path

`--bench` writes to `spec/attest/rollbench.txt` **and overwrites it every run**. A record kept at the
path its own producer clobbers is one command away from being replaced by a different measurement
under the same name.

So the sealed artifact carries an immutable name — host, execution count, iteration count — and the
runner's output path stays scratch. The separation is checked, not remembered.

## The format outlived it, on purpose

The archived record is `v1`. The runner now writes `v2`, with a counter `v1` never had, **in the same
commit**.

That is deliberate. A format-versioning law never met by a real successor is inherited rather than
tested (L67), so the successor ships beside it and the sealed log must still read. An unknown format
refuses rather than being guessed at: a row read against the wrong field list is a table of numbers
under the wrong names.

## The result

`measure` predicted, from exact op counts before any host ran anything, that **moulding moves the
intercept and cannot move the slope**.

Measured across five independent executions on the named host: the penalty `moulded` pays against
`flat` is a constant, flat across a depth axis over which the replay work itself grows by nearly an
order of magnitude. The intercept moved; the slope did not. Predicted in integers, confirmed in
nanoseconds, on a different machine, months later.

Graded honestly in both directions: some distinct experiments `SEPARATE` under `repeat`'s
between-execution floor and the rest read `INDISTINGUISHABLE` — **those are not upgraded here** —
while the direction is reported separately, because separation and direction are different facts and
neither stands alone.

## `does_not_show`

**One machine, one interpreter, one set of declared conditions.** Five executions sample what a
process fixes at startup. They do not sample the machine, the interpreter build, the working
directory or the environment size, and Mytkowicz et al. measured factors of that class at 2–8% on
their own.

The declared conditions are **gameplay** conditions — a turbo power profile with game mode on —
rather than measurement conditions. That is defensible for a game engine and it is not a quiet
choice.

A constant measured over ticks 1 to 12 is not a claim about ticks 100.

## Grade

**MEASURED** — the sealed log parses under a format that has already superseded it, its digest still
verifies, it grades admissible against `sealframe`'s live door, and the claim's numbers are
recomputed from its bytes at gate time. **DECLARED** — which log is the record.
