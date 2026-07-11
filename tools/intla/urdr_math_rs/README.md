<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `urdr_math_rs/` — independent Rust placement of the exact-integer math spine

A single-file, `std`-only second placement (no cargo, no crates, hand-rolled
SHA-256) of **urdr-math** — the frozen exact-integer linear-algebra library
(`../urdr_math.py`) — and the two atlas certificates built on it
(`../atlas_injective.py`, `../atlas_reconstruct.py`). It shares no code with the
Python reference; it is trusted only in so far as it reproduces the conformance
corpus bit-for-bit.

## What it reproduces

The digests in [`../conformance_math.txt`](../conformance_math.txt) — the
SHA-256 of the canonically-serialized RESULT of each fixed fixture:

| op | what | refuse path |
|---|---|---|
| `rank` | fraction-free Bareiss rank over ℤ | i64 overflow → REFUSE |
| `det` | fraction-free Bareiss determinant | i64 overflow → REFUSE |
| `floor_divmod` | exact integer floor divmod | `b=0` / INT_MIN → REFUSE |
| injectivity | verdict `rank==n` + exact nullspace collision witness | — |
| reconstruction | Cramer over `det` on an independent subsystem; witness `M·num = den·y` | forged → INCONSISTENT; deficient → NOT_INJECTIVE |

Refusal is encoded **in** the serialized result (a status byte), so every corpus
row is a digest match; any mismatch is `URDR-MATH-DIVERGENCE`.

## Build & run (on a conforming host)

```
rustc -O urdr_math.rs -o urdr_math.exe
.\urdr_math.exe            # prints: URDR-MATH-RS: ADMITTED (20/20 digests)
.\urdr_math.exe            # run TWICE — determinism
.\urdr_math.exe --defect   # RED FIRST: every digest MUST diverge (exit 0 = caught)
```

**ADMITTED twice + defect caught ⇒ urdr-math cross-placement MEASURED**, which
lifts the general-n injectivity certificate and the exact reconstruction solver
from reference-proven to cross-placed. Scope: integer agreement on the stated
corpus — **not** universal correctness. The `--defect` build corrupts the digest
`MAGIC`, so every scene must diverge; a build that still matches has a dead gate.

## Regenerating the corpus

The goldens are the Python reference: `python3 ../math_scenes.py` prints them;
`../conformance_math.txt` pins them; `verify.py`'s `math_conformance` stage keeps
the reference honest to the pin. If the corpus changes, update the `GOLDEN`
array in `urdr_math.rs` to match.
