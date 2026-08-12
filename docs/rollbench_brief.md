<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: rollbench-log -->
# `rollbench` — design brief (URDRRBN1)

## The instrument `measure` could not contain

`measure` fixed the terms of the rollback question and structurally could not answer it: a clock in
that module would let a wall-clock figure be asserted from a gate run, and a falsifier forbids one.
So the stopwatch lives here. **The separation is the point, not an inconvenience.** This module
produces *evidence*. It never produces a *verdict*.

## Driven by the plan, proved by severance

The representations, workloads, depth ladder, denominators and baseline are **read** from
`measure.bench_plan()`. Sever it and the harness dies — that is how "reads the plan" becomes a
measurement rather than a claim. A benchmark that chose its own terms could report against a
denominator picked after seeing the numbers, which is exactly what naming them in advance prevents.

84 cells: 3 representations × 4 workloads × 7 depths.

## Two questions, kept apart

    measure.admit_claim        is the CLAIM well formed?    workload, host, denominator, baseline
    rollbench.evidence_grade   is the LOG admissible?        was it produced on the NAMED host?

A log from an unnamed machine is a **perfectly well-formed log and inadmissible evidence**, and those
are different findings. A falsifier asserts both halves of that on the same log, because if either
check could stand for the other, one is redundant and the wrong one would be dropped.

`evidence_grade` reads `sealframe.NAMED_HOST` — the operator's own declared machine, conditions and
all — rather than restating a host law this module has no standing to write.

## Nothing this container produces can be cited

A `--bench` run here emits a log whose grade is `NOT_MEASURED`, and **the gate asserts it**. The
harness is exercised, its shape is verified, and its numbers remain uncitable. That is the honest
state of a benchmark written on a machine that is not the one the claim is about.

## The seal

Host, interpreter, the digest of the plan that was run, then one row per cell:

    representation  workload  depth  n  p50_ns  p95_ns  p99_ns

Quantiles rather than a mean, because rollback latency is exactly the shape where a mean hides the
tail — and **ranks rather than interpolations**, so a quantile is always an observed sample and `n`
travels beside it. With five samples a p99 cannot reach the maximum, which is the rank being honest
about what `n` supports.

A single byte changed anywhere in the body breaks the digest. Proved at three places — the host
line, a row, and the plan digest — because a seal covering only the tail would pass a forged header.

## No verdict is emitted

There is no field in a row where "faster" could live, and no callable here that compares two
representations. The guard excludes exactly one name — its own, since a predicate that forbids a word
cannot state what it forbids without naming it — and a planted `compare_representations` is proved to
redden it.

This is the third time in this arc a guard has matched itself, after `measure`'s clock scan and
`lift`'s `exp(`. The pattern is now worth recognising on sight.

## What is and is not on the gate

The log format, the digest, the provenance law, the plan-severance and the refusal to grade are
deterministic and gated. **The timings are not run on the gate at all** — a timing assertion inside a
gate is a threshold that gets loosened until it cannot fail.

    python3 tools/terrain/rollbench.py --bench spec/attest/rollbench.txt "Turbo-35W AC"

## Grade

**MEASURED**: the log round-trip and its seal; the provenance law in both directions; the
plan-severance; the claim handed to `measure.admit_claim`; the structural absence of any comparison.
**NOT_MEASURED**: every timing this container could produce, by this module's own provenance law.

`does_not_show`: which representation is faster — that is what the log is *for* and it is
deliberately not decided here; that the sampling is statistically sufficient; that `perf_counter`
resolves what the differences require — the log carries the interpreter and platform so that question
can be asked of the numbers rather than of a docstring.

Rows `rollbench-log`, `rollbench-provenance`; falsifiers in `tests/test_rollbench.py`.
