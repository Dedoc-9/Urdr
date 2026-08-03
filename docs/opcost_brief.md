<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: opcost-budget -->
# `opcost` — design brief (URDROPC1, T3.29, MMO Stage H opener)

**Read**: 2026-08-03, the centrality-ordered READ pass — and the first brief written **blind against a
frozen pre-registration** (P1, `../exe_epistemics/PREDICTIONS.md`): the seam hypothesis was committed
before this module was read, and the classification below was made from the live gate rows per the
frozen success_rule. Outcome: **CONFIRMED-MODEL**. Reading grade: **CONFIRMATION** — the module is what
its rows certify.

## What it is

The **certified integer-work envelope**: the deterministic, EXACT count of primitive integer operations
each core operation performs, as a pure function of its input. "Latency" is split into two honestly
separable halves, and the module is the certifiable one:

- **WORK** (here) — exact op-counts: `glide_micro_count` (micro-steps, wall-stopped), `warden_edge_checks`
  (the closed form `(W-1)H + W(H-1)`), `admit_substeps` (Σ|dx|+|dy|), `wardhom_columns` (F2 columns),
  `tick_envelope` (per-tick total). Deterministic, byte-exact, digest-pinned (URDROPC1 over the sorted
  cost vector) — gate-certifiable because it reproduces bit-for-bit.
- **WALL-CLOCK** (`bench.py`) — the per-op cost on a NAMED host. Non-deterministic, host-tagged,
  **never in the gate**. The latency envelope is the product of the two: time ≤ op_count × per-op cost.

## The core law (what the rows certify)

**Cost ≤ envelope, refuse otherwise** — two inequalities, both live:

1. **Envelope** (`opcost-bound`): `glide_micro_count ≤ glide_micro_bound` always, and STRICTLY below on
   the wall scene — the bound is non-vacuous, witnessed by a wall that stops the glide early.
2. **Budget** (`opcost-budget`): `within_budget(cost, budget)` admits work at/under the ceiling and
   raises a typed `OPCOST-REFUSE` over it — the FIELD-REFUSE / TOPOLOGY-REFUSE discipline lifted from
   arithmetic overflow to a tick's work ceiling. A tick that would exceed its budget refuses; it never
   silently overruns.

Exactness is itself gated (`opcost-exact`: each count equals the real work it claims to count, checked
against the actual adjacency enumeration and the real micro-step trace) and the five scene vectors are
digest-pinned (`opcost:scenes`). Downstream, the envelope becomes live enforcement in `govern`
(URDROPC2: FIFO prefix within budget, defer the rest) — the Stage-H arithmetic family this module opens
(opcost → govern → priogov → slo → clslo, re-verified cross-placement in `latarith_rs`).

## The seam (P1's finding)

A **cost seam**, distinct from the admission seam: `jurisdiction` refuses on *where truth lives*
(canonical lattice state, regardless of certificate); `opcost` refuses on *how much work the operation
performs* (a measured resource quantity of the operation itself). Same refusal discipline — typed,
fail-closed — different measured object. And cost is **bounded, not conserved**: count < bound exactly
when a wall bites. Both of P1's pre-registered refutation risks (admission-in-disguise; conservation)
measured false from the rows.

## does_not_show

Wall-clock time (that is `bench.py`, MEASURED-on-named-host); the constant factor per op-count unit
(host- and compiler-dependent); cache and memory effects; any guarantee under an adversarial scheduler —
the op-count bounds the WORK, not the OS's willingness to run it. And the brief does not upgrade the
digest pins: a green `opcost:scenes` certifies the vectors reproduce, never that the scenes span all
workloads. `integrity ≠ truth`.

## Falsifier

This brief cites `opcost-budget`: the row that certifies the work-budget law (admit at/under, typed
refuse over). If `within_budget` stopped refusing over-budget work — or refused with an untyped error —
that row reddens and this brief's central claim dies with it.
