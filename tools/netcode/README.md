<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/netcode/` — the deterministic netcode stack (rungs N1–N4)

The property IEEE floats cannot promise across CPUs/GPUs/compilers, and the one this
engine is built to have: **peers that begin from the same canonical world and exchange
only inputs — never state — independently reproduce the same simulation, witness for
witness.** Four rungs deep, every one `MEASURED (both placements)` and frozen in
[`spec/D12`](../../spec/D12-versions.md); every claim below is a gate stage, not prose.

## The stack

| Rung | Module | What it proves | Gate stage |
|---|---|---|---|
| **N1** lockstep | [`lockstep.py`](lockstep.py) | Same canonical world + same logical input log → one `URDRLST1` witness chain, one `URDRLSTT` trace. Reordered/duplicated delivery absorbed (dedup + additive-impulse commutativity); a dropped/modified/tick-moved input desyncs and `first_desync` names the first mismatching tick. | `netcode_lockstep` |
| **N2** rollback | [`rollback.py`](rollback.py) | Canonical snapshots every `K` ticks (retain `H`); a late-but-valid input rewinds to the newest snapshot at-or-before its tick, replays, and **converges bit-for-bit to the canonical timeline** — the converged golden IS the N1 golden. Beyond the horizon: `ROLLBACK-REFUSE`, rejected whole. Same `(peer, seq)` with a different payload: `ROLLBACK-CONFLICT`. `K`/`H` are operational, never semantic. | `netcode_rollback` |
| **N3** authenticated inputs | [`authinput.py`](authinput.py) | A **Lamport one-time signature** (built from the same SHA-256 every placement hand-rolls) must verify against a pre-committed roster pin before an event enters the transcript — an actual signature, so a forging *peer* is caught, not just an outsider. Four forgery shapes each `AUTH-REFUSE`; the fully signed log reproduces the N1 golden unchanged (authentication decides *eligibility*, never state law). One keypair per `(peer, seq)` — the OTS one-time rule — is enforced structurally by N2's identity law. | `netcode_auth` |
| **N4** authored worlds | [`worldstep.py`](worldstep.py) | A frozen [`URDR-WORLD-3`](../../spec/D12-versions.md) export becomes the initial state of the same loop: static AABB obstacles (least-penetration resolution, fixed tie order), a **typed authoring boundary** (`WORLD-REFUSE` on non-integer coordinates — never a silent round), instance file order as world identity, and the anti-drift theorem: with no statics on the canonical arena, the N4 tick reproduces the frozen N1 chain **bit-for-bit**. | `netcode_world` |

## The separation (structural, not advisory)

**Authentication decides who may submit** (`AuthedPeer` — only a verified envelope
reaches the authority) · **the deterministic authority decides what results** (the
tick; no float, clock, RNG, or iteration-order anywhere) · **witnesses prove what
happened** (`URDRLST1`/`URDRLSTT`, unchanged since N1 and frozen). Every rung is a new
*consumer* of those laws; none of them edits a frozen module.

## Placements

Each rung has a std-only, single-file Rust placement (no crates, hand-rolled SHA-256,
`i128` intermediates), validated first by an independent C99 `__int128` port in a
sandbox and then **ADMITTED on Windows/`rustc`**:

- [`lockstep_rs/lockstep.rs`](lockstep_rs/lockstep.rs) — the `arena3` trace, 2/2 + defect.
- [`rollback_rs/rollback.rs`](rollback_rs/rollback.rs) — convergence at `K=4`(×2)/`K=8`, refusals typed, and the apply-at-head defect diverging to the **same digest** as the C99 port (`39326ff9…`).
- [`authinput_rs/authinput.rs`](authinput_rs/authinput.rs) — roster root + signed chain 2/2, refusals typed, and the tail-collision forgery found at the **same offset** as C99 (`dvx+423`).
- [`worldstep_rs/worldstep.rs`](worldstep_rs/worldstep.rs) — arena equivalence with frozen N1, the highway golden 2/2, and the no-statics defect at the shared anchor (`9c0ad7c5…`).

Where the placements agree on the *failure* digests too, the defect self-tests are
themselves cross-placed — the strongest form of "the gate can redden" this repo has.

## Conformance corpora (pinned in the D12 freeze manifest)

`conformance_netcode.txt` (arena3) · `conformance_rollback.txt` (arena3_late3 — equals
the N1 golden by construction) · `conformance_auth.txt` (roster3 + arena3_signed) ·
`conformance_world.txt` (highway; the no-statics defect diverges in all three
languages). Falsifiers: `tests/test_lockstep.py`, `test_rollback.py`,
`test_authinput.py`, `test_worldstep.py`. Runnable: `demo/lockstep_demo.py`.

## Honest scope

Bounded fixed-point (regime B of [`D11 §4b`](../../spec/D11-layer-contracts.md)):
reproducible-by-frozen-rounding, refuses on overflow, not exact. N3 pins the
*mechanism* (verification gates admission) on fixture keys from published seeds —
operational key secrecy/distribution and cross-session replay protection are out of
scope and not claimed. N4's runtime is cross-placed on the mapped canonical scene;
its JSON loader is reference-gated; instance mass is loaded but inert until body-body
contact arrives as a versioned successor. Remaining `DECLARED`: interest management,
N2/N3 composition over authored worlds, body-body contact in N4.
