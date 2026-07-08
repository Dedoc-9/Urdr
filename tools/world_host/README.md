<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# world_host — shared-world runtime reference (Milestone 7, Step 1)

An **executable specification** of the host enforcement loop — NOT a production runtime. It
exists to keep Milestone 7 on the same proof discipline that got the kernel to D10: build the
model in Python, run it, falsify it, freeze it, and only then port to Rust.

## What it CONSUMES (it extends nothing)

- **Authority** = the kernel's content digest (`urdr.canon.digest`, canon → SHA-256, D1 §7) —
  the exact digest the ☉ reference and `urdr-core-rs` already agree on (D8 conformance).
- **Admissible observer** = a COVERING (injective) chart atlas — the trivial-kernel condition
  measured in Milestone 6 / D10 §2.
- **Frame binding** = a frame is ADMITTED iff it reconstructs to the authoritative state —
  the view-laundering refusal measured in Milestone 6.5 / D10 §3.

## The one question Step 1 answers

> Can multiple observers render DIFFERENT images of one authoritative world while every
> ADMITTED frame stays bound to the SAME authority digest, and is a laundered or inadmissible
> frame REFUSED (not repaired)?

`tools/world_host/test_world_host.py` answers it: 7/7 green, including a **non-vacuity** check
(a deliberately broken "admit everything" host FAILS the harness). Run:

```
python3 tools/world_host/test_world_host.py
```

## Grade

`IMPLEMENTED (host track)` — integration-test green on the Python sandbox host. This is **not**
a URDR-gate `MEASURED` result: it is host code that *consumes* the measured kernel, graded by
its own test. `the runtime consumes the theorem; it does not re-prove it`.

## NOT here (Steps 2–5, deliberately)

Step 2 transition history (replay / reorder / fork rejection) · Step 3 deterministic
concurrency · Step 4 Rust port against these same fixtures · Step 5 networking, persistence,
replication, renderer/GPU, spatial streaming. No networking, no graphics, no optimization
exists in Step 1 by design.
