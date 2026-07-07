<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D9 — Deterministic numeric substrate (Q32.32 fixed point)

Status: `DECLARED` — this document freezes the numeric LAWS before any implementation
is trusted (Milestone 5A). Each row of §6 goes `MEASURED` only when its falsifier is
green in the gate on a named host AND the fixture reproduces bit-identically through
BOTH placements (☉ reference and `urdr-core-rs`). `frozen ≠ implemented ≠ measured`.

## 0. Why (Milestone 5 — the physics substrate)

Physics needs numbers; the digest needs bit-exactness; D7/design-law-4 forbid floats
in the core. The resolution (manifold-engine brief §3): the witness substrate is
fixed-point integer arithmetic — deterministic on every platform **by construction**,
not by rounding-mode discipline. Everything later (collision, multiplayer convergence,
observer projections) inherits its trustworthiness from this layer. The contract:

```
same state + same inputs + same timestep  =  same digest
```

on every host and every placement. A number that two machines disagree about is not a
number in this system; it is a refusal.

## 1. Representation (no new value kind)

A **fix** is a plain Urðr `Int` `n` (i64, two's complement), interpreted as the
rational `n / 2^32` (Q32.32). There is NO new canonical form: a fix digests as the
`Int` it is (D1 §7, tag `i` + big-endian i64). The module is a Layer-2 *discipline*
over `Int` — exactly as `manifold_kernel` is a discipline over lists — and earns no
glyph (§20 default: composition).

- `one` = 2^32 = 4294967296. `from_int(k)` = `k · 2^32`.
- **Domain**: `n ∈ [−(2^63−1), 2^63−1]` — the value `n = −2^63` (INT_MIN) is
  **refused** as an operand (its magnitude is not representable; negation wraps).
  Value range ≈ (−2^31, 2^31), resolution 2^−32.
- **Ordering**: the representation is monotone, so the core comparisons
  `= ≠ < ≤ > ≥` are ALREADY correct on fix values. No wrappers; documented, falsified.

## 2. Rounding law (one rule, everywhere)

Every inexact operation rounds **toward −∞ (floor)**:

- `mul(a,b)` = `⌊ a·b / 2^32 ⌋`
- `div(a,b)` = `⌊ a·2^32 / b ⌋`
- `sqrt(a)`  = `⌊ 2^32·√(a/2^32) ⌋` = `isqrt(a·2^32)` (integer square root), `a ≥ 0`
- `floor_int(a)` = `⌊ a / 2^32 ⌋` (a plain Int)

Floor is total, sign-consistent, subdivision-friendly, and cheap to falsify (a
truncate-toward-zero defect diverges on the first negative operand). No other
rounding exists in the substrate. `one law ≠ one law per op`.

## 3. Refusal law (never silently wrong)

An operation whose exact result is not representable, or whose operand is outside
its domain, must **die** — `≟` breach → `URDR-ASSERT`. Specifically:

1. **Overflow** (result magnitude ≥ 2^63): refused. No wraparound-as-truth, no
   saturation. (The core's defined i64 wrap stays the *core's* law; the substrate's
   law is stricter, enforced by in-module range proofs.)
2. **Division by zero**: refused.
3. **sqrt of a negative**: refused.
4. **INT_MIN operand** (§1): refused.

`a wrong number that flows is worse than a program that dies`.

## 4. The operation pipeline (each op, uniformly)

```
operand domain proof (≟) → exact integer identity → range proof (≟) → plain Int out
```

The digest needs no help: outputs are core `Int`s. The exact integer identities are
computed **bit-serially** — the language has `+ − ×`, comparisons, `?`, `Σ`, `range`
and NO division/shift/recursion, so:

- `bits63(m)`: the 63 magnitude bits (high→low) by one fold over a precomputed
  descending powers-of-two list (a module constant) — subtract-compare per step.
- `mul`: fold over `bits63(|a|)` with accumulator `(hi, lo)` meaning
  `acc = hi·2^32 + lo`: each step doubles and conditionally adds `|b|` split as
  `bh·2^32 + bl`; the low-half carry is ∈ {0..3} (comparisons, no division); every
  intermediate is provably < 2^63; an `hi` escaping 2^31 sets a refusal flag.
  Result = `hi·2^32 + lo`, floor-corrected for sign using the exact remainder
  (dropped low 32 bits ≠ 0 ⇒ negative results subtract 1). **Algorithm PROVEN** (2026-07-07) by a
  faithful prototype using only `+ − ×`/comparisons/folds — `tools/fixpoint_proto/mul_algorithm.py`
  reproduces the exact `⌊a·b/2³²⌋` on a battery (positive, negative floor-toward-−∞, halves,
  overflow→refuse); the Urðr encoding must mirror it. `algorithm proven ≠ Urðr mul measured`.
- `div`: restoring long division of the 95-bit dividend `|a|·2^32` (the 63 bits of
  `|a|` followed by 32 zeros) by `|b|`, remainder always < |b| < 2^63; the doubling
  step `2r + bit` is computed as `(r−b) + r + bit` when it would overflow — exact in
  i64 for all `r < b`. Floor-corrected for sign by the final remainder.
- `sqrt`: `isqrt(a·2^32)` by bounded Newton on the bit-length-derived seed, finished
  by an exact candidate check (`c² ≤ N < (c+1)²` via `mul`-comparisons) — the floor
  proof is *verified*, not assumed from convergence.

Fuel: each op is O(63) fold steps (~5k ticks); a fixture of dozens of ops sits well
under the default 1,000,000 budget. Determinism is by construction: no host
operation other than i64 `+ − ×` and comparisons is ever consulted.

## 5. Falsifiers (red set — written before the module is trusted)

| Falsifier | Dies with | What it refutes |
|---|---|---|
| `fixpoint_overflow_wrong` — claims `mul(big, big)` commits a wrapped value | `URDR-ASSERT` | overflow ambiguity / wrap-as-truth |
| `fixpoint_rounding_wrong` — claims `div(−1, 2) = trunc` (0) instead of floor (−1·2^31 repr) | `URDR-ASSERT` | rounding divergence (trunc vs floor) |
| `fixpoint_div_zero_wrong` — claims `div(x, 0)` yields anything | `URDR-ASSERT` | division-by-zero sentinel values |
| `fixpoint_arithmetic` (accept) — algebraic identities: `mul(from_int(3), from_int(4)) = from_int(12)`, `div∘mul` round-trips with documented floor loss, sign laws, ordering, distributivity probes | one golden digest ×2, both placements | platform-dependent math; non-identical replay |
| cross-placement — every fixture above through ☉ AND `urdr_core.exe` | digest equality | the substrate being an accident of one evaluator |
| defect drill — a deliberately trunc-rounding / wrap-permitting module build must diverge or die | divergence caught | vacuous harness (L5) |

## 6. Grades (now; updated only by measurement)

| Claim | Maturity | Evidence |
|---|---|---|
| This contract (representation, rounding, refusals, op identities) | IMPLEMENTED (as spec) | DECLARED |
| `add/sub/neg/from_int` per §2–4 | IMPLEMENTED | **MEASURED** — `examples/fixpoint_arithmetic.urdr` (⊢ [30064771072,30064771072,0,4294967296,1]) + `rejected/fixpoint_overflow_wrong.urdr` (URDR-ASSERT); vendored `fixpoint` module; oracle-agree; D8 corpus v2 |
| `floor_int` per §2 (needs bit-serial ÷2³²) | SPECULATIVE — lands with `div` | N/A |
| `mul` bit-serial per §4 | SPECULATIVE — **algorithm proven** (`tools/fixpoint_proto/mul_algorithm.py`, battery green); Urðr encoding + cross-placement pending | N/A |
| `div` bit-serial per §4 | SPECULATIVE until it lands | N/A |
| `sqrt` per §2/§4 | SPECULATIVE (law frozen; lands after mul/div are MEASURED) | N/A |
| Cross-placement bit-identity on the fixtures | IMPLEMENTED | **MEASURED** (2026-07-07) — `urdr-core-rs` reproduced `fixpoint_arithmetic` and refused `fixpoint_overflow_wrong` inside ADMITTED 10/10, twice, on Windows/`rustc 1.96.1` |
| "Physics-ready substrate" | NOT CLAIMED — physics is Milestone 5B, after this ledger row is MEASURED | — |

## 7. D8 corpus extension (deliberate un-freeze)

Measured fixpoint fixtures join `tools/foreign_placement/conformance.txt` as
**corpus v2** — DONE and CROSS-VERIFIED: `fixpoint_arithmetic` (accept) + `fixpoint_overflow_wrong` (reject) are in `conformance.txt`, and `urdr-core-rs` reproduced them inside **ADMITTED 10/10 (twice)** on Windows/`rustc 1.96.1` (2026-07-07). The Stage-4 target grows, deliberately and recorded here: each new
vector is `MEASURED` from ☉ before it is frozen, and `urdr-core-rs` must reproduce
it (plus survive `--defect`) to stay ADMITTED. `a frozen target may grow; it may
never silently change`.

## 8. Does-not-show

Green here certifies: these identities, these refusals, on these fixtures, on the
named hosts, through the two placements. It does NOT show: physics correctness
(no physics exists yet), performance (no figures; any future figure names its host),
real-number semantics (Q32.32 is exact rational arithmetic with floor loss — the
loss is part of the law, not an approximation of ℝ), or safety of compositions the
fixtures do not exercise. `Nihil ultrā probātum`.
