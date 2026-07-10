<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `fixpoint_proto/` — proven numeric prototypes (Q32.32)

Faithful Python references for the D9 fixed-point operations. **These are not the language.**
They exist so that each intricate Urðr encoding has a *proven target* to reproduce — the
"prototype-first" half of the discipline: prove the algorithm with only the operations the Urðr
core actually has (`+ − ×`, comparisons, folds — **no** `//`, `%`, `<<`, `>>`, no recursion),
*then* encode it and check it against the prototype. `algorithm proven ≠ Urðr measured`.

| File | Operation | Method (division-free) |
|---|---|---|
| `mul_algorithm.py` | `mul(a,b) = ⌊a·b / 2³²⌋` | 16-bit-limb schoolbook product; limbs extracted by place-value folds; floor toward −∞; overflow refused. |
| `div_algorithm.py` | `div(a,b) = ⌊a·2³² / b⌋` | Restoring long division of the 95-bit dividend; an overflow-free doubling step; floor-corrected; div-by-zero + i64-overflow refused. |
| `floor_int_algorithm.py` | `floor_int(a) = ⌊a / 2³²⌋` | A single place-value `fdiv` by 2³²; floor toward −∞ for negatives; INT_MIN refused. |
| `sqrt_algorithm.py` | `sqrt(a) = isqrt(a·2³²)` | Bit-by-bit, each candidate tested by the **exact** `umul` limb-pair compare; the guarded `umul` mirrors the Urðr refusal so the domain (`a < 2⁶²`) is where it never overflows. |

Each file is runnable and prints `BATTERY: ALL OK`:

```
python3 tools/fixpoint_proto/mul_algorithm.py
python3 tools/fixpoint_proto/div_algorithm.py
python3 tools/fixpoint_proto/floor_int_algorithm.py
python3 tools/fixpoint_proto/sqrt_algorithm.py
```

Laws and per-op grades: [`../../spec/D9-numeric-substrate.md`](../../spec/D9-numeric-substrate.md).
