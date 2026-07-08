<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# world_host — shared-world runtime reference (Milestone 7, Steps 1–3)

An **executable specification** of the host enforcement loop — NOT a production runtime. It
keeps Milestone 7 on the same proof discipline that got the kernel to D10: build the model in
Python, run it, falsify it, freeze it, and only then port to Rust (Step 4).

## What it CONSUMES (it extends nothing)

- **Authority** = the kernel's content digest (`urdr.canon.digest`, canon → SHA-256, D1 §7) —
  the exact digest the ☉ reference and `urdr-core-rs` already agree on (D8 conformance).
- **Admissible observer** = a COVERING (injective) chart atlas — Milestone 6 / D10 §2.
- **Frame binding** = a frame is admitted iff it reconstructs to the authoritative state —
  Milestone 6.5 / D10 §3.

## Step 1 — static world views (`world_host.py`, `test_world_host.py`, 7/7)

Many observers render DIFFERENT images of one authoritative world while every ADMITTED frame
stays bound to the SAME authority digest; a laundered frame (mutated source, claimed authority)
and a non-covering atlas are REFUSED, not repaired. Non-vacuity: a broken admit-everything host
fails the harness.

## Step 2 — witnessed transition history (`transition_history.py`, `test_transition_history.py`, 9/9)

Many views of one EVOLVING history → one authoritative digest CHAIN. The chain digest is
path-dependent, `D_{n+1} = H(D_n, op_n)` (kernel canon → SHA-256; genesis `D_0 = ᛝ(S_0)`) — it
is STRONGER than the content digest: a reordering that lands on the same final value still
breaks the chain. Green: replay reproduces the authoritative head; a second observer replaying
the same list reaches the same head; views differ but final-state authority agrees. Red:
**reordered** history, **missing** transition (broken parent), and a **fork** (two candidate
heads, no merge rule) are all REFUSED — the runtime analogue of the witness firewall.
Non-vacuity: a broken accept-any-history host fails the harness.

## Step 3 — deterministic multi-actor scheduling (`scheduler.py`, `test_scheduler.py`, 9/9)

Many actors propose transitions concurrently; the scheduler canonicalizes them into ONE
ordering that is a pure function of the proposal MULTISET — sort by proposal content digest
(the kernel `weave` rule) — so arrival order cannot change the authoritative history. Green:
the canonical head and final state are invariant under arrival order, the committed segment is
a valid Step-2 history, and the commit is deterministic. Red: a non-canonical / speculative
branch has a different head and CANNOT be promoted (`branch != authority`). It consumes the
measured convergence property (kernel `weave` / `parallel_runtime`), it does not re-prove it.
Non-vacuity: an arrival-order scheduler is order-DEPENDENT and fails invariance.

```
python3 tools/world_host/test_world_host.py
python3 tools/world_host/test_transition_history.py
python3 tools/world_host/test_scheduler.py
```

## Grade

`IMPLEMENTED (host track)` — integration-test green on the Python sandbox host. This is **not**
a URDR-gate `MEASURED` result: it is host code that *consumes* the measured kernel, graded by
its own tests. `the runtime consumes the theorem; it does not re-prove it`.

## NOT here (Steps 4–5, deliberately)

Step 4 Rust port against these same fixtures ·
Step 5 networking, persistence, replication, renderer/GPU, spatial streaming. Steps 1–3 have no
networking, no graphics, no optimization, and no concurrent EXECUTION (Step 3 is deterministic
single-threaded scheduling, not threads) — by design.
