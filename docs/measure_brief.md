<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: measure-law -->
# `measure` — design brief (URDRMSR1)

## The law

> A performance claim is valid only when its **workload**, **host**, **denominator** and **baseline**
> are named — and a *timed* claim must additionally cite a host log.

A claim missing one of the four is not a weak claim. It is not a claim: there is nothing to reproduce
and nothing to compare against. Each omission refuses separately, and a complete claim is admitted —
a law that refused everything would be a wall, not a rule.

## Why this rung is not "optimize"

`mould` made the snapshot smaller by a type. The tempting next sentence is *and therefore rollback is
faster*, and it is not available. **Moulding trades something for something.** Restoring a moulded
record must read `x, y, z`, ask `contact` what state that is, derive the width, and only then take
the optional fourth integer. The flat record just takes four integers. Fewer integers, more work per
integer — and which wins is a wall-clock question elegance is not entitled to answer.

**This container is not a named host**, so no time is measured here and none is claimed. There is no
clock in the module — checked by walking the AST, because a text scan would find its own guard list,
which is the `authority-reads-code` defect inside the checker that forbids it.

## What op counts already settle

    MOULDING MOVES THE INTERCEPT AND CANNOT MOVE THE SLOPE.

A rollback of depth *R* costs `restore + R × tick`. The three representations differ **only** in the
restore — the per-tick replay is identical work, because `to_vouch` hands `stride` the same flat
state either way. Measured, at a grounded tick:

    flat        intercept  4 ints, 0 reads      slope 2 reads/tick
    moulded     intercept  3 ints, 1 read       slope 2 reads/tick
    narrowed    intercept  3 ints, 0 reads      slope 2 reads/tick

So a host measurement that reports **different slopes** for the two representations is measuring
something other than the record. That is now a falsifiable statement about the benchmark rather than
a hope about the result.

## The exact trade

    grounded actor    −1 integer stored    +1 terrain read
    airborne actor     0 integers stored   +1 terrain read

An airborne actor pays the derivation and saves nothing. That is not a defect — it is the price of
having a shape rather than a policy — and it means **the benefit is a function of the workload**,
which is exactly why a claim must name one.

## Three controls, and the third is what makes the experiment mean anything

`flat` is the conventional slot. `moulded` is the shipped representation. **`narrowed`** stores the
*same integers as moulded* and derives nothing — its widths arrive through a side channel that is
deliberately **not counted**. It is an unfair control by construction and says so: an upper bound on
the memory-only benefit, with the gap between `narrowed` and `moulded` being exactly what the
derivation costs.

Without it, a host result showing moulded faster could not distinguish *fewer integers helped* from
*the derivation was free*.

## Four workloads, proved to differ

    all_grounded       grounded 12
    all_airborne       airborne 9, grounded 3
    alternating        airborne 8, grounded 8
    frequent_landing   airborne 10, grounded 5

Their contact-state censuses are required to be **distinct**. A family whose members exercise the
same states is one workload wearing four names, and the saving would then be a property of the
fixture — `retain`'s lesson, one layer up.

## What the operator runs

`python3 tools/terrain/measure.py --plan` emits the plan and the op counts as JSON: the
representations, the workloads, the depth ladder (1, 2, 4, 8, 16, 32, 64), the denominators
(`snapshot_ints`, `snapshot_bytes`, `ms_per_rollback`, `ms_per_replayed_tick`), the quantiles
(p50/p95/p99) and the baseline — **named in advance**, so a result cannot be reported against a
denominator chosen after seeing it. Status: `NOT_MEASURED — requires a named host log`.

## Grade

**MEASURED**: the admission law in all six of its clauses; the op-count decomposition; the exact
per-actor trade; the shared-slope result; the four workloads proved distinct; the three
representations proved to store what they claim. **NOT_MEASURED**: every wall-clock figure,
structurally.

`does_not_show`: that moulding is faster *or* slower — that is the question this rung exists to hand
to a host with its terms fixed; that op counts predict time (they bound what can differ, which is a
weaker and true claim); that these four workloads are representative of play.

Rows `measure-law`, `measure-shape`; falsifiers in `tests/test_measure.py`.
