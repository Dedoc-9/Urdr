#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for exact integer floor-divmod (integer-linear-algebra ladder, rung 1).

floor_divmod(a,b) = (q, r) with a = q*b + r, q = floor(a/b), and r in [0, |b|) with sign of b
(Python's // and %). Faithful: restoring long division over the 63 magnitude bits, only
`+ - *`/comparisons/folds -- NO `//`, `%`, `<<`, `>>`, no recursion. The doubling step never
overflows because q = floor(a/b) satisfies |q| <= |a| <= 2^63-1 (unlike the Q32.32 `div`, whose
95-bit dividend can overflow), so no in-fold guard is needed. Refuses b=0 and INT_MIN operands.

Note on novelty (honest): a RANGE-LIMITED integer divide already composes from the measured
substrate -- a//b = floor_int(div(from_int(a), from_int(b))) for |a|,|b| < 2^31. This op is the
FULL-i64-range direct version the linear-algebra ladder (Bareiss elimination, whose pivots grow)
actually needs. ASCII name only -- no glyph (design law 5). Run -> BATTERY: ALL OK.
"""
IMAX = (1 << 63) - 1


def _bits(m):                      # 63 magnitude bits of m in [0, 2^63), high -> low
    out, r = [], m
    for k in range(62, -1, -1):
        p = 1 << k
        if p <= r:
            out.append(1); r -= p
        else:
            out.append(0)
    return out


def _udivmod(mag_a, mag_b):        # mag_a>=0, mag_b>0 : (q, r), mag_a = q*mag_b + r, 0<=r<mag_b
    q = r = 0
    for bit in _bits(mag_a):
        bmr = mag_b - r - bit      # in [0, mag_b): mag_b - r > 0, minus bit
        if r >= bmr:               # <=> 2r + bit >= mag_b
            r = r - bmr; q = q * 2 + 1
        else:
            r = r + r + bit; q = q * 2   # 2r + bit < mag_b < 2^63, no wrap
    return q, r


def floor_divmod(a, b):
    if b == 0:
        return "REFUSE"            # division by zero
    if a < -IMAX or b < -IMAX:
        return "REFUSE"            # INT_MIN operand (magnitude unrepresentable)
    sa = 1 if a >= 0 else -1
    sb = 1 if b >= 0 else -1
    qm, rm = _udivmod(a if a >= 0 else -a, b if b >= 0 else -b)
    q = qm if sa * sb >= 0 else (-qm if rm == 0 else -(qm + 1))
    r = a - q * b                  # exact remainder, sign of b, in [0, |b|)
    return q, r


if __name__ == "__main__":
    import random
    tests = [(7, 2), (-7, 2), (7, -2), (-7, -2), (6, 3), (-6, 3), (0, 5), (1, 1),
             (IMAX, 1), (IMAX, IMAX), (-IMAX, 3), (123456789, 987), (2, 7), (-2, 7),
             (10**15, 7), (-(10**15), 7), (10**15, -7)]
    random.seed(5)
    for _ in range(60000):
        tests.append((random.randint(-IMAX, IMAX), random.choice([-1, 1]) * random.randint(1, IMAX)))
    bad = 0
    for a, b in tests:
        g = floor_divmod(a, b)
        e = (a // b, a % b)        # Python floor divmod = the exact truth
        if g != e:
            bad += 1
            if bad <= 6:
                print(f"  MISMATCH a={a} b={b} got={g} exp={e}")
    print("  b=0 ->", floor_divmod(5, 0), " INT_MIN ->", floor_divmod(-(1 << 63), 3))
    print(f"cases={len(tests)}  BATTERY:", "ALL OK" if bad == 0 else f"{bad} MISMATCH")
