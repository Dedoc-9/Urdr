<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D16 — The regional-authority contract (one simulation, partitioned in space)

Status: **MEASURED (reference); cross-placed (C99, self-verified); FREEZE pending the
Windows/rustc admission of the Rust placement.** The checkable core is gate-enforced
(`netcode_region`, five rows). A **second, independent placement** now exists and agrees:
`tools/netcode/worldregion_c/worldregion.c` — its own Q32.32 backend, its own SHA-256, the
N4/N4.1 tick, and the partition — was compiled and run in-session (`cc -O2 -std=c99`, gcc
11.4) and reproduces the `seam2` monolith, the `seam2` composed trace, and the
dropped-boundary divergence **bit-for-bit**. That single scene cross-places both N4.1
contact and D16 composition. `tools/netcode/worldregion_rs/worldregion.rs` is the Rust
placement (FP + SHA-256 reused verbatim from the admitted `worldstep_rs`); it is authored
and awaits admission on the named Windows host — the freeze vehicle. Until that lands the
contract is measured and cross-placed but **not frozen**, and the D13 §C8 glyph stays parked.

D13 §C8 ("region-scoped authority") was **rejected as premature** with a standing
condition: *re-open only after the D-series regional-authority contract exists and its
library realization has been measured against it.* This document is that contract; the
library is `tools/netcode/worldregion.py`; the measurement is the `netcode_region` gate
stage. The open Phase-3 question it answers — *do regional witnesses compose to the
global witness?* — is answered **yes, with no new witness class**: composition is the
frozen `URDRLST1`/`URDRLSTT` law recomputed over the reunified interiors.

## 1. The load-bearing invariant — the Seam Composition Theorem

> For **any** valid partition of an authoritative world into spatial regions, if each
> region evolves its interior by the frozen authority tick from its **admitted boundary
> conditions** alone, then the deterministic **reunification** of the regional interiors
> reproduces the monolithic `URDRLST1`/`URDRLSTT` witness chain **bit-for-bit**.
> Otherwise the engine produces a typed refusal, or the first divergence is localized to
> the exact tick at which the boundary failed.

This is the spatial mirror of D14 and D15. D14 converges many authoring modalities to
one canonical object; D15 fans one authoritative state to many renderers; **D16 cuts one
authoritative simulation into many regions and proves the cut leaves the witness
invariant.** All three boundaries are one-way and conformance-tested.

The engine's stated principle, made executable and gate-checked:

> Admissible boundary conditions necessarily determine the evolution of the interior
> state. The boundary is an active constraint, not merely a passive interface. Internal
> computation is the system's deterministic response to boundary conditions.

A region is a **one-way consumer of its boundary condition**. It reads ghosts; it never
reads — and can never write — a neighbour's interior. That ignorance is the guarantee, as
it is on the input side (a canon does not know which tool authored it) and the output
side (a renderer can only read).

## 2. The partition and the boundary condition

A world is cut by a strictly-increasing list of **integer x-seams** into `R = len+1`
regions. A body belongs to exactly one region by its centre-x (`< cut` goes left) — a
**total, disjoint cover**, so ownership is never ambiguous. Non-integer or non-monotone
seams are a malformed boundary and are `REGION-REFUSE`d before a single tick runs (the
D11/D14 integer-grid discipline, applied to the partition itself).

Each tick, each region:

1. **Integrates its interior** with the frozen `worldstep.step_tick` (N4/N4.1): owned
   inputs, gravity, integration, walls, statics — for its owned bodies. No coupling.
2. **Admits its boundary condition** — the read-only **ghosts**: every non-owned body
   that could come into contact with an owned body this tick. The ghost set is a
   conservative, exact-integer over-approximation (an axis-wise box expanded by this
   tick's maximum displacement), so it can never *under*-include a body a contact pair
   needs; over-inclusion is harmless because the frozen contact pass skips any pair with
   `dd >= (r_i+r_j)²`. A **complete** boundary is what makes composition exact.
3. **Resolves contact** over (owned ∪ ghosts), **writing only owned bodies**. A cross-seam
   pair is resolved by both regions independently — each computes the *identical* Q32.32
   impulse from the shared tick-start state and applies it to its own body — reproducing
   the monolith's single symmetric update.
4. **Reunifies**: every body is taken from its owner, in global index order, and witnessed
   by the frozen `URDRLST1` state law. A body whose centre crossed a seam is **handed off**
   — owned by its new region next tick. Handoff is bookkeeping about *who computes what*;
   the witness is a function of authoritative state alone, so it is partition-invariant by
   construction.

No boundary datum flows the other way: a region cannot relocate a body its neighbour
owns, nor depict a body count the authority does not have. Gameplay-affecting facts enter
a region only as admitted boundary conditions — never smuggled from a neighbour's interior.

## 3. What is enforced now

`verify.py` stage `netcode_region` (`tests/test_worldregion.py`, 10 falsifiers):

- `netcode-region:seam2` — the composed regional trace equals the monolith **and** the
  pinned golden (`conformance_region.txt`), deterministically twice;
- `netcode-region-invariance` — six different valid partitions (the trivial one region,
  four single-seam cuts, and a three-region cut) all compose to the one monolithic witness;
- `netcode-region-boundary` — dropping the ghost exchange makes cross-seam contact
  silently vanish, so the chain **diverges, localized to the exact contact tick** (the
  boundary is load-bearing, not decorative);
- `netcode-region-refusal` — a float / non-monotone / bool seam is `REGION-REFUSE`d before
  stepping; a valid partition is accepted;
- `netcode-region-nonvacuity` — the `seam2` scene really straddles the seam at contact
  (cross-seam contact is exercised) **and** a body really hands off across it.

The `seam2` scene: two equal bodies, wall- and (x-)gravity-free; body 0 (fast, +6) catches
body 1 (slow, +1); they collide **across** the seam at `x=191`, momentum exchanges per
N4.1, and afterward body 0 hands off. One scene, both the ghost-contact and the handoff —
the seam carries physics, not just bookkeeping.

## 4. The admission ladder for this layer

1. **State the falsifiable contract** (this document) — the standing D13 §C8 precondition. ✔
2. **Reference library measured against it** (`worldregion.py`, the `netcode_region`
   stage). ✔ — this is the "library realization measured" that D13 §C8 waited for.
3. **A second, independent placement** — **the C99 placement landed and self-verified**
   (`worldregion_c/`, gcc 11.4, in-session): its own FP + SHA-256 reproduce the seam2
   monolith, the seam2 composed digest, and the dropped-boundary divergence bit-for-bit.
   Python + C99 now agree on every seam2 digit, on two toolchains. The Rust placement
   (`worldregion_rs/`) is authored and awaits admission on the named Windows host.
4. **Freeze** the partition, boundary-condition, and composition laws once the Windows/rustc
   placement agrees (the house named-host admission), then generalize (multi-axis seams,
   multi-pair seam ordering, asynchronous regional advance with the composite/frame witness
   class D13 §C8 anticipated — introduced only if a test shows `URDRLST1` cannot carry the law).

## 5. Honest scope

This increment is **synchronous** (all regions advance in lockstep and reunify each tick),
**single-axis** (integer x-seams), and exact for scenes whose cross-seam contact is a
single pair per region per tick (the 2-body `seam2` scene). Multi-pair seam ordering, more
than one seam axis, asynchronous regional clocks, and a witness that verifies a region
*without* reunifying are declared successors, each following the same ladder. What is
proved is precise and small: **partitioning the complete N4.1 simulation does not change
its witness** — the property that lets one authoritative world be computed by many
authorities without its notion of truth fragmenting.

## See also

- `spec/D14-frontend-contract.md`, `spec/D15-view-contract.md` (the input- and output-side
  one-way contracts this mirrors)
- `spec/D13-glyph-probe.md` §C8 (the parked glyph and its re-open condition)
- `spec/D11-layer-contracts.md` (regional locality, the structural seed T16)
- `tools/netcode/worldregion.py` (the executable contract)
- `tools/world_host/regional_rigidity.py` (the *structural* regional-locality result this
  extends into the *dynamic* simulation)
