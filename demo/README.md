<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `demo/` — prove the engine reproduces, in one command

Most engines ask you to *trust* that a simulation will behave the same on another
machine. This one lets you **check it in about a second.** The whole project rests on a
single claim — *every admitted output is either bit-identical across independent runs and
implementations, or explicitly refused* — and this folder makes that claim executable.

```bash
# from the repo root
python3 demo/prove_it.py          # PowerShell: $env:PYTHONHASHSEED="0"; python demo\prove_it.py
```

It runs three things and **checks** them (nonzero exit if any check fails), so a green run
means something. Nothing here is a rendering of a game — it is the *authoritative
simulation reproducing itself*, with cryptographic witnesses you can diff.

## What it proves (actual output)

```
========================================================================
1. HEADLINE — the bounded fixed-point rung reproduces its frozen goldens
   MEASURED: gated in CI + cross-placed in Rust; digests are cross-host & cross-language
========================================================================
    stack3  URDRFPT1 b061c760faeec16563979665898bbfb2868868cdfdca0f6b0c0b0d980e0709f5
  [PASS] stack3: deterministic (same digest twice)
  [PASS] stack3: == frozen golden   (also reproduced by fp_dynamics_rs on Windows/rustc)
    swing   URDRFPT1 42e4b2cb8da7dc0d3bc5dc3057a1f03f499e0618c7c8f7f89772e76d52a3e6d6
  [PASS] swing: deterministic (same digest twice)
  [PASS] swing: == frozen golden   (also reproduced by fp_dynamics_rs on Windows/rustc)

========================================================================
2. AUTHOR -> EXPORT -> REPLAY — the authored world replays identically
========================================================================
    highway   ticks=201   contacts_resolved=156   (2 vehicles + 1 static barrier)
    highway   chain head 7514214ff64d2f63536119fb6949c160a7778103b9dcc7783b99b83cae026246
    highway   chain tail 0f6250175cddf6329f1228033f13375f40833c2c6d252327955d6562efac8101
  [PASS] highway: bounded run, no overflow (engine did not refuse)   201 ticks on the Q32.32 substrate
  [PASS] highway: witness chain reproduces bit-for-bit across independent re-runs
    cascade   ticks=73   (built-in exact Newton's-cradle momentum transfer)
  [PASS] cascade: deterministic
  [PASS] cascade: total momentum conserved exactly
  [PASS] cascade: total 2*KE conserved exactly

========================================================================
3. EXACT CERTIFIED SOLVES — a witness or a refusal, never a guess
========================================================================
    stack     lambda (bottom->top) = [3.0, 2.0, 1.0]   URDRLCP1 89666457617a17e0…
  [PASS] stack: LCP complementarity certified
  [PASS] stack: lambda = [3, 2, 1] (each contact carries the weight above it)
  [PASS] stack: URDRLCP1 matches the gated physics-lcp:rest3 digest
    joints    URDRJNT1 f63bcc9995d7b9c3…   (4-ball rod chain)
  [PASS] joints: J.v = 0 certified (rigid links held)

RESULT: ALL CHECKS PASSED
```

## Why each part matters for a game

The three sections map directly onto the properties a production team actually pays for.

**1 — Bit-identical simulation across hosts and languages** is the one thing IEEE floats
cannot promise across CPUs/GPUs/compilers, and it is exactly what deterministic-lockstep
and *rollback* netcode run on. The two `URDRFPT1` digests above are produced by the Python
reference, an independent std-only Rust placement (`tools/physics/fp_dynamics_rs/`) on
Windows, and the CI gate on Linux — the *same 64 hex characters* every time. Peers can
exchange inputs instead of state and treat a digest mismatch as a caught desync.

**2 — A per-tick witness chain that replays identically** is deterministic replay: the
foundation of reproducible bug reports (ship the inputs, replay the exact frame), and of
*replay-based regression testing* (a recorded run whose trace digest is a golden — a diff
in behavior is a diff in one hash). The `highway` world is the shape
[`urdr_designer.html`](../tools/editor/urdr_designer.html) exports; open the written
`urdr_replay.json` in the editor's **▷ Replay** mode to scrub it frame-by-frame with the
contacts/impulses/momentum overlays drawn *from these recorded witnesses*.

**3 — Certified single solves** show the other half of the contract: where an answer can be
exact it carries a checkable certificate (the stack's `lambda=[3,2,1]` satisfies
complementarity; the chain satisfies `J.v=0`), and where it cannot the engine **refuses**
rather than guess. Note the stack's `URDRLCP1` digest is *identical* to the gate's pinned
`physics-lcp:rest3` — the exploratory editor is demonstrably driving the gated solver, not a
private copy.

## Honest scope

| Layer exercised | Grade |
|---|---|
| Fixed-point steppers (`stack3`, `swing`) — the `URDRFPT1` headline | **MEASURED** — gated in `verify.py` + cross-placed in Rust (both placements) |
| Exact LCP / articulated solves (`URDRLCP1`, `URDRJNT1`) | **MEASURED** — gated + cross-placed in `urdr-physics-rs` |
| `replay.py` runtime + `world_highway.json` authoring/export | **exploratory** — the authoring/visualization client; not part of the CI gate |

`admitted != trusted`: a green run certifies *these runs on this host*, plus (for the
fixed-point and exact rows) agreement with a frozen golden that a second language and a
second OS also reproduce. The witnesses are what you diff — the decimals in the replay file
are for drawing only.

## Deterministic lockstep — `lockstep_demo.py`

```bash
python3 demo/lockstep_demo.py
```

The architecture's one unusual advantage, made executable. It stages a **two-peer** session
and checks the three things a lockstep netcode lives or dies on:

1. **Agreement.** Peer A and Peer B start from the same canonical world and exchange *only*
   their timestamped inputs — never state. Each assembles the input union in a *different*
   arrival order, steps the deterministic authority, and emits a witness chain. Identical
   inputs → identical per-tick witnesses and an identical final digest.
2. **Delivery robustness.** The same inputs delivered reordered or duplicated produce the
   same chain (exact-duplicate dedup + additive-impulse commutativity) — a lossy/reordering
   network is not a desync. A genuinely *new* input still changes the chain (dedup is real).
3. **Fault detection.** A dropped, modified, or mis-timed input desyncs, and the desync is
   **explained by the first mismatching witness** (which tick, and the two differing digests)
   rather than silently diverging.

This is the gated rung **N1** ([`tools/netcode/lockstep.py`](../tools/netcode/lockstep.py)),
`MEASURED (both placements)` — the Rust placement reproduces the transcript bit-for-bit — and it
is the floor of a four-rung stack, all both-placements and frozen in `spec/D12`: **N2** rollback
(a late-but-valid input rewinds to a canonical snapshot and *converges to this same chain*),
**N3** authenticated inputs (a Lamport-OTS envelope must verify before an input may enter the
transcript — `digest ≠ MAC` is answered with an actual signature), and **N4** authored worlds
(the `world_highway.json` scene below runs in this very loop). See
[`tools/netcode/README.md`](../tools/netcode/README.md) for the stack.

## Files

- [`prove_it.py`](prove_it.py) — the runnable, self-checking reproducibility proof (≈1 s, stdlib only).
- [`lockstep_demo.py`](lockstep_demo.py) — the two-peer deterministic-lockstep demonstration.
- [`world_highway.json`](world_highway.json) — a tiny authored `URDR-WORLD-3` scene (two
  vehicles closing on a static median), the kind [`urdr_designer.html`](../tools/editor/urdr_designer.html)
  exports.
