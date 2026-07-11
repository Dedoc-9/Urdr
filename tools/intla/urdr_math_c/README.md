<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `urdr_math_c/` — a THIRD-runtime placement of the exact-integer math spine

A single-file, standard-library-only **C99** re-implementation of `urdr-math` and
the two atlas certificates. It shares no code with the Python reference *or* the
Rust placement (`../urdr_math_rs/`); it is trusted only in so far as it reproduces
the same conformance corpus bit-for-bit.

Where `urdr_math_rs` proves *two-runtime* agreement (Python + Rust), this file
takes the mathematical spine to **three-runtime** agreement — a third language
(C), a third compiler (gcc/clang), and — as measured — a second operating system
(Linux). Reproducing the 20 exact-math digests is the strongest form of the
project's claim: the rank/determinant/floor_divmod primitives, the general-*n*
injectivity verdict **and its exact nullspace collision witness**, and the exact
reconstruction solver are identical across three independent implementations.

## What it reproduces

The 20 digests in [`../conformance_math.txt`](../conformance_math.txt) — the
SHA-256 of the canonically-serialized result of `rank`, `determinant`,
`floor_divmod` (each with its i64-overflow / `b=0` REFUSE encoded as a status
byte), the injectivity verdict + nullspace witness, and reconstruction state /
typed refusal. Refusal is encoded **in** the result, so every corpus row is a
digest match; any mismatch is `URDR-MATH-DIVERGENCE`.

## Build & run

```
cc -O2 -std=c99 -o urdr_math_c urdr_math.c    # gcc or clang (needs __int128; not MSVC)
./urdr_math_c            # prints: URDR-MATH-C: ADMITTED (20/20 digests)
./urdr_math_c            # run TWICE — determinism
./urdr_math_c --defect   # RED FIRST: every digest MUST diverge (exit 0 = caught)
```

**ADMITTED twice + defect caught ⇒ a third placement agrees.** Measured on Linux
(gcc 11.4, `x86_64`): `ADMITTED (20/20)` twice, `defect caught (20/20)`. The
`--defect` build corrupts the digest `MAGIC` (`URDRMTH1` → `URDRMTHX`), so every
scene must diverge; a build that still matches has a dead gate.

Portability note: the wide multiplies use `__int128` (a gcc/clang extension), so
this file builds with gcc or clang. MSVC has no 128-bit integer type; an
i64-checked portable variant is a small follow-up if MSVC is the only toolchain.
