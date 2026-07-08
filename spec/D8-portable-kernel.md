<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D8 — Portable kernel contract (cross-language conformance)

Status: `MEASURED` — **target hit 2026-07-07**. This document freezes what an **independent**
execution kernel must reproduce to be admitted as a *placement* of Urðr's
geometry-of-execution model (D7) — so the semantics are provably not carried by the Python
interpreter alone. The contract and its reference vectors are `MEASURED` (the ☉ Python
reference's actual, gate-green output). The independent kernel's **convergence is now also
`MEASURED`**: `urdr-core-rs` (`tools/urdr_core_rs/urdr_core.rs` — one std-only Rust file,
hand-rolled SHA-256, no crates) reproduced every accept digest and every rejection code
**twice, identically**, with a deliberately-defective build caught 4/4 (§4 non-vacuity), on
ONE named host: Windows, `rustc 1.96.1` (stable-x86_64-pc-windows-gnu). Scope: the conformance
corpus — grown to **24** vectors (v2 = fixpoint foundation, v3 = division-free `mul`, v4 = `div`, v5 = `floor_int`+`sqrt`, v6 = observer atlas injectivity, v7 = general atlas algebra; v2+v3 re-
ADMITTED 12/12 twice on 2026-07-07, **v4/v5 Rust ADMITTED 20/20 twice, defect caught 9/9, 2026-07-07; v6 Rust ADMITTED 22/22 twice, defect caught 10/10, 2026-07-07; v7 reference-frozen, Rust ADMITTED 24/24 pending**) — that host; whole-corpus admission stays the SCOPED strengthening. `admitted ≠ trusted`.

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
actual output, green in `verify.py`. The independent kernel's convergence is `MEASURED`
(2026-07-07): `urdr-core-rs` was ADMITTED per §4 — 8/8 conformance vectors reproduced twice
identically, the `--defect` build caught 4/4, and 18 ☉-generated unit vectors green
(`rustc --test`, serial) — on Windows / `rustc 1.96.1` (stable-gnu). A second, independent
kernel agrees, so the portability claim is *made at exactly this scope*: these vectors, that
host. What this does NOT show: agreement beyond the frozen corpus (whole-corpus admission via
`tools/foreign_placement/foreign_oracle.py` is the SCOPED strengthening), correctness on
adversarial inputs, or performance. Falsifier kept live: any future mismatch is
`URDR-RUST-DIVERGENCE` — refused, not resolved. `Nihil ultrā probātum`.
