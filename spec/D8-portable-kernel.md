<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D8 — Portable kernel contract (cross-language conformance)

Status: `DECLARED`. This document freezes what an **independent** execution kernel must
reproduce to be admitted as a *placement* of Urðr's geometry-of-execution model (D7) — so the
semantics are provably not carried by the Python interpreter alone. The contract and its
reference vectors are `MEASURED` (they are the ☉ Python reference's actual, gate-green output);
an independent kernel's **convergence** is `SPECULATIVE / N/A` until built and run on a host
with a toolchain. This build sandbox has **no `rustc`/`cargo` and no root to install one** —
so the convergence claim is *withheld*, not asserted. `target frozen ≠ target hit`.

## 0. Why (Stage 4)

Stage 4 asks whether the execution model survives contact with a lower-level substrate. An
independent kernel that reproduces the reference digests bit-for-bit turns "a language with
interesting semantics" into "a portable execution model." The risk it removes: that the model
is an accident of one evaluator. `change is cheap; a certified transition is the scarce
resource` — and a *second* certifier that agrees is the proof the certification is real.

## 1. The minimal kernel contract (five obligations)

An independent kernel must implement exactly these, and nothing more:

1. **Digest identity** — `canon → SHA-256` (D1 §7), the byte grammar of §2. Identity is content.
2. **Immutable state transition** — a step produces a NEW value; no in-place mutation.
3. **Witness verification** — `ᛞ` mints `Grounded` only from a passing verifier; the ladder
   refuses unearned `MEASURED`.
4. **Deterministic replay** — `(initial state, schedule) → one final digest`, on any host.
5. **Transport rejection** — an invalid transition (a `≟` failure) dies with the exact code
   (`URDR-ASSERT`), never a silent resolution.

## 2. The digest algorithm (reproduce byte-for-byte)

`canon(v) → bytes`, then `SHA-256`. From `urdr/canon.py` (D1 §7):

- `Int n`   → `b"i"` + `int64` big-endian (`struct >q`).
- `Sym s`   → `b"y"` + `varint(len(utf8))` + utf8 bytes.
- `List`    → `b"l"` + `varint(count)` + concat of `canon(item)`.
- `Store`   → `b"s"` + `varint(count)` + fields **sorted by key**, each `canon(Sym key)+canon(val)`.
- `Grounded`, `λ`, `Digest`, `Conflict` — see `urdr/canon.py` for the full grammar.

`varint` is LEB128 (7 bits/byte, high bit = continue). **Every mapping is sorted**; host
iteration order is never observed (that is what makes the digest portable). `digest ≠ MAC`.

## 3. Conformance vectors (the frozen target)

`tools/foreign_placement/conformance.txt` is the machine-readable target. Accepted fixtures
must yield the exact digest; rejected fixtures must die with the exact code. The four accepted
fixtures were chosen to span the five obligations:

- `manifold_runtime`      — transport-under-contract + deterministic replay + witness + projection;
- `frequency_invariance`  — temporal reparameterization (rate ≠ identity);
- `parallel_runtime`      — order-invariance of commuting transitions + race exposure;
- `speculative_runtime`   — the possible/actual boundary (a hypothesis is not committed reality).

The four rejections (`manifold_transport_wrong`, `frequency_aliasing_wrong`,
`race_condition_wrong`, `speculation_wrong`) all die `URDR-ASSERT` and exercise obligation 5.

## 4. Pass criterion

An independent kernel is **ADMITTED** as a placement iff it reproduces EVERY accepted digest
AND EVERY rejection code in the conformance vector, AND a *deliberately defective* build of it
is caught (non-vacuity — a harness that cannot redden proves nothing, LESSONS L5). Any mismatch
is `URDR-RUST-DIVERGENCE` (Rust instance) / `URDR-PLACEMENT-DIVERGENCE` (general). The mechanism
already exists: `tools/foreign_placement/` (the differential oracle §14b generalized to any
substrate — no foreign code trusted, only agreement). This contract supplies its frozen inputs.

## 5. Grade

The contract (§1–2) and the vectors (§3) are `MEASURED`: they are the ☉ Python reference's
actual output, green in `verify.py`. An independent kernel's convergence is `SPECULATIVE / N/A`
— it requires an implementation (e.g. `urdr-core-rs`) built and run on a host with a toolchain,
which the current build sandbox lacks (`no rustc/cargo, no root`). This document is the
**target**; hitting it is Stage 4's remaining, unmeasured step. `Nihil ultrā probātum` applies
to Stage 4 itself: the portability claim is not made until a second kernel is run and agrees.
