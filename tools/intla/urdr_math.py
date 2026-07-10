#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-math v0.1 — the FROZEN public API of the deterministic exact-integer math library.

Every function exported here satisfies three properties (the library discipline):
  * Deterministic       -- same inputs always produce the same outputs (no clock/RNG/float).
  * Pure                -- no hidden state, no side effects; inputs are not mutated.
  * Canonically testable -- validated against exact oracles / an independent implementation.

All arithmetic is i64-bounded; any overflow is a REFUSAL ('REFUSE'), never a wrapped or
approximate answer. Downstream subsystems (urdr-rigidity, urdr-physics, atlas algebra) depend on
THESE NAMES, never on how they are implemented. `urdr-core` (the sealed language) is unchanged.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intdiv_algorithm import floor_divmod                       # exact integer a = q*b + r
from bareiss_rank import bareiss_rank as rank                   # exact rank over Z
from matrix_det_null import bareiss_det as determinant          # exact determinant
from matrix_det_null import nullspace_witness as nullspace      # nonzero integer v with M v = 0
from matrix_ops import transpose, matmul                        # matrix basics (i64-refusal)
from number import gcd, extended_gcd, modinv                    # number theory

__version__ = "0.1"
__all__ = ["floor_divmod", "rank", "determinant", "nullspace", "transpose", "matmul",
           "gcd", "extended_gcd", "modinv", "__version__"]

if __name__ == "__main__":
    missing = [n for n in __all__ if n != "__version__" and not callable(globals().get(n))]
    print(f"urdr-math v{__version__} public API:", ", ".join(n for n in __all__ if n != "__version__"))
    print("all callable:", not missing, "" if not missing else f"MISSING {missing}")
    sys.exit(0 if not missing else 1)
