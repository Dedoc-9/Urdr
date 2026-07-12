<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/netcode/` — the deterministic lockstep spine (rung N1)

The smallest honest demonstration of the property IEEE floats cannot promise across
CPUs/GPUs/compilers, and the one this whole engine is built to have: **two peers that begin
from the same canonical world and exchange only inputs — never state — independently
reproduce the same simulation, witness for witness.**

## What's here

- **`lockstep.py`** — the authority (not a game). `simulate(world, log) -> (frames, final)`
  steps the frozen Q32.32 substrate ([`../physics/field.py`](../physics/field.py)); each tick
  applies that tick's inputs (additive control impulses) in a canonical `(peer, seq)` order,
  then integrates under gravity in an elastic box. Every tick emits a `URDRLST1` state witness;
  `trace_digest` folds the run into one `URDRLSTT` digest. `first_desync(a, b)` returns the
  first tick two chains differ — the *explanation* of a desync.
- **`conformance_netcode.txt`** — the frozen `arena3` trace golden the gate pins.

## The two behaviours, split honestly

- **Delivery is robust.** The same logical log delivered *reordered* or *duplicated* yields
  the same chain: exact-duplicate deliveries are deduped (load-bearing), and additive impulses
  commute (so per-tick order doesn't matter). The canonical sort is a canonical-form nicety
  here, **not** the property relied on — stated, not overclaimed.
- **Corruption diverges, detectably.** A *dropped*, *modified*, or *tick-moved* event changes
  the log, so the chains diverge — and `first_desync` localizes it to the first mismatching
  tick. Never a silent divergence.

## Gate + grade

`verify.py` stage `netcode_lockstep`: the `arena3` trace reproduces twice and matches its
golden; two peers assembling the input union in different arrival orders agree; and a
`netcode-desync-selftest` requires a dropped input to be caught while the clean run is not
(non-vacuity — the detector can redden). Falsifiers: [`../../tests/test_lockstep.py`](../../tests/test_lockstep.py).
Runnable: [`../../demo/lockstep_demo.py`](../../demo/lockstep_demo.py).

**Grade: `IMPLEMENTED / MEASURED`** (reproducibility, on the already cross-placed FixedPoint
substrate). **Second placement — written + C-cross-checked, `SPECULATIVE` pending host:**
[`lockstep_rs/lockstep.rs`](lockstep_rs/lockstep.rs) (std-only Rust, hand-rolled SHA-256,
`i128` intermediates) reproduces the `arena3` `URDRLSTT` golden and diverges under `--defect`;
its logic was cross-checked bit-identical by an independent C99 port (`__int128`, own SHA-256).
Build `rustc -O lockstep.rs` and run — `URDR-NETCODE-RS: ADMITTED` flips N1 to **MEASURED (both
placements)**. **Declared:** *authenticated* inputs — `digest ≠ MAC`, so the witnesses catch
accidental divergence, not a signing adversary.
