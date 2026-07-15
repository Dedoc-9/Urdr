<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `fixpoint_proto/` — proven numeric prototypes (Q32.32)

## Index

Faithful Python references for the D9 fixed-point operations — **not the language**, the
*proven targets* the Urðr encodings must reproduce.

| File | Operation | Method (division-free) |
|---|---|---|
| `mul_algorithm.py` | `mul(a,b) = ⌊a·b / 2³²⌋` | 16-bit-limb schoolbook product; limbs extracted by place-value folds; floor toward −∞; overflow refused. |
| `div_algorithm.py` | `div(a,b) = ⌊a·2³² / b⌋` | Restoring long division of the 95-bit dividend; overflow-free doubling; floor-corrected; div-by-zero + i64-overflow refused. |
| `floor_int_algorithm.py` | `floor_int(a) = ⌊a / 2³²⌋` | A single place-value `fdiv` by 2³²; floor toward −∞ for negatives; INT_MIN refused. |
| `sqrt_algorithm.py` | `sqrt(a) = isqrt(a·2³²)` | Bit-by-bit, each candidate tested by the **exact** `umul` limb-pair compare; guarded `umul` mirrors the Urðr refusal so the domain (`a < 2⁶²`) never overflows. |

## Whitepaper

The "prototype-first" half of the numeric discipline. Each intricate Urðr encoding is hard to
get right, so the algorithm is first proven here using **only the operations the Urðr core
actually has** — `+ − ×`, comparisons, folds; **no** `//`, `%`, `<<`, `>>`, no recursion — and
*then* encoded and checked against this prototype. The prototype is the target; the encoding is
the deliverable. Crucially, `algorithm proven ≠ Urðr measured`: passing here means the method
is correct, not that the language encoding is — that grade is earned separately in D9.

## Dev notes

- Each file is runnable and prints `BATTERY: ALL OK`:

  ```
  python3 tools/fixpoint_proto/mul_algorithm.py
  python3 tools/fixpoint_proto/div_algorithm.py
  python3 tools/fixpoint_proto/floor_int_algorithm.py
  python3 tools/fixpoint_proto/sqrt_algorithm.py
  ```

- Keep every prototype within the core-op subset — reaching for `//` or `>>` here defeats the
  purpose (the encoding cannot use them). Laws and per-op grades:
  [`../../spec/D9-numeric-substrate.md`](../../spec/D9-numeric-substrate.md).
