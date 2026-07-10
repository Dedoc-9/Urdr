<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Roadmap — a deterministic game / simulation physics engine (honest, bounded)

This document is the architectural compass for the engine ambition. It is written to bound the
promise, not inflate it. Nothing here is `MEASURED`; it is a design contract. Where it and a spec
disagree, the spec wins; grades live only in [`../spec/D5-ledger.md`](../spec/D5-ledger.md).

## 1. What Urðr uniquely provides (and what it does not)

**Provides — the deterministic authority + certification layer.** A shared world state that is
bit-identical across placements (D8), evolves through **witnessed, non-forking** transitions
(Milestone 6.5), and whose structural admissibility (rigidity → Connelly superstability, D5) is
*certified over ℤ*, not float-estimated. This is the multiplayer / replay / lockstep / anti-cheat
spine, and it is the genuinely novel contribution.

**Does not provide — real-time GPU rendering or per-frame exact computation.** Those are
conventional engineering bounded by two hard truths, below. No amount of kernel work removes them.

## 2. The Hybrid Execution Model (the load-bearing decision)

Exact integer linear algebra cannot run at 60 fps. Therefore:

- **Fast path (every frame):** the deterministic **Q32.32 fixed-point** substrate (D9) runs the
  simulation at speed. Bit-identical by construction across hosts/placements; no float, no host
  rounding.
- **Audit path (selective):** `urdr-math` (exact `rank`/`det`/`nullspace`/Bareiss, D5) is invoked
  **as an arbiter**, never per frame — at checkpoints, on disputed transitions, for anti-cheat, and
  for offline structural certification (rigidity / superstability). The exact oracle certifies; it
  does not simulate.

`fixed-point simulates; exact algebra arbitrates`.

## 3. The Pixels-vs-State boundary (the Deterministic Rendering Theorem)

`Frame_t = (R ∘ T)(S_{t-1}, Δt)`: if both `T` (transition) and `R` (renderer) are deterministic,
identical state ⟹ identical pixels, and `digest(Frame_t) = H(R(S_t))` is reproducible evidence.
**But** real GPU pipelines are *not* bit-identical across hardware/drivers (floating point, shader
optimization, rounding). Therefore:

- The **native GPU pipeline is a non-authoritative, ambient projection** — an observer (D10 §1),
  never a source of authority; pixels never feed back into the simulation.
- Cross-platform **visual** bit-identity requires a **constrained fixed-point software rasterizer**
  (built on the Q32.32 substrate). Without it, the guarantee is identical *state*, not identical
  *pixels*. A deterministic software renderer is future host-track work.

## 4. Sandbox scope (what is gate-able here vs. what needs local native builds)

- **Gate-able in this repo** (the reference / verification tier, Python + the ☉ gate + cross-placed
  `urdr-core-rs`): the language core, `urdr-math`, `urdr-rigidity`, `urdr-physics`, the world-host
  reference (`tools/world_host/`), and every conformance vector.
- **NOT gate-able here** (requires native compilation on local machines): the Rust runtime host,
  networking, persistence, GPU rendering, and real-time performance. These are graded by their own
  integration tests on the target platform, never by the URDR gate. (The authoring sandbox has no
  `rustc` and no GPU; `urdr-core-rs` is already compiled + run on the named Windows host.)

## 5. The three tracks

| Track | What it is | Priority toward a *playable* engine |
|---|---|---|
| **1. Multi-actor structural evolution** (`urdr-physics × world_host`) | many actors propose structural mutations; the deterministic scheduler canonicalizes them into one non-forking, rigidity-certified transition history | **critical path — buildable + gate-able here** |
| **2. Total Connelly gate witness** | lift the *whole* superstability verdict (PSD + rank + no affine flex) into a cross-placed `MEASURED` fixture | rigor / completeness — parallel, gate-able |
| **3. Bignum substrate** | arbitrary-precision integers so dense/large exact certifications don't overflow i64 | large-scale *oracle*, NOT the real-time path — defer |

The dependency spine stays: **Research proposes · `urdr-math` computes · `urdr-core` certifies ·
applications consume**. The engine is the application layer; it consumes certified transitions and
never re-derives authority.

## 6. Track 1 data contract (the multi-actor mutation proposal)

```
Proposal { actor: Int,  parent: Digest,  mutation: [op, args…] }
intent digest = ᛝ(canon([actor, parent, mutation]))
```

- Canonical order = **sort by intent digest** (the `weave` rule): a pure function of the proposal
  multiset, so arrival order cannot change the committed history.
- `parent` binds a proposal to the base state the actor observed; a proposal against a stale world
  is refused (provenance binding, Milestone 6.5).
- Each committed transition retains the full proposal, so sequencing never erases the actor's
  cryptographic intent.
- A tick yields ONE new authoritative digest (non-forking); a proposal that is a no-op
  (`URDR-DELTA-UNEARNED`) or makes the structure inadmissible (loss of rigidity) becomes a
  **deterministic structural conflict** (`↯`) — refused identically on every host.

`Nihil ultrā probātum.`
