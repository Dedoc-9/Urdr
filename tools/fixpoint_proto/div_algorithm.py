#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for the Urðr Q32.32 `div` (D9 §2/§4).

Faithful prototype: computes floor(a * 2^32 / b) for Q32.32 fixed-point using
ONLY operations Urðr's core has — `+ - *`, comparisons, folds. NO `//`, `%`,
`<<`, `>>`, no recursion. Restoring long division of the 95-bit dividend
`|a| * 2^32` (the 63 bits of |a| followed by 32 zeros) by |b|; the doubling
step `2r + bit` is never formed directly — the test `r >= b - r - bit` and the
update `r - (b - r - bit)` keep every intermediate in [0, b) < 2^63 (no i64
wrap). Refuses division by zero, and any result whose magnitude >= 2^63.

`algorithm proven != Urðr div measured`: the ledger keeps `div` SPECULATIVE
until it runs in the language and agrees on both placements.

Run: `python3 tools/fixpoint_proto/div_algorithm.py` -> BATTERY: ALL OK.
"""
ONE = 1 << 32
IMAX = (1 << 63) - 1


def bits_of(a):
    """The 63 magnitude bits of a in [0, 2^63), high to low, by subtract-compare."""
    out = []
    r = a
    for m in range(62, -1, -1):
        p = 1 << m
        if p <= r:
            out.append(1); r -= p
        else:
            out.append(0)
    return out


def divmod95(mag_a, b):
    """floor(mag_a * 2^32 / b) and remainder, restoring long division, overflow-free."""
    r = 0
    q = 0
    for bit in bits_of(mag_a) + [0] * 32:          # dividend = mag_a followed by 32 zero bits
        bmr = b - r - bit                          # in [0, b): b - r > 0 (r < b), minus bit
        if r >= bmr:                               # <=> 2r + bit >= b
            r = r - bmr                            # = 2r + bit - b, in [0, b)
            q = q * 2 + 1
        else:
            r = r + r + bit                        # safe: 2r + bit < b < 2^63 in this branch
            q = q * 2
    return q, r


def div(a, b):
    """Q32.32 div with the D9 refusal + floor(toward -inf) laws."""
    if b == 0:
        return "REFUSE"                            # division by zero
    s = (1 if a >= 0 else -1) * (1 if b >= 0 else -1)
    q, r = divmod95(a if a >= 0 else -a, b if b >= 0 else -b)
    if q > IMAX:
        return "REFUSE"                            # result not representable in i64
    if s >= 0:
        return q
    return -q if r == 0 else -(q + 1)              # floor toward -inf


def _truth(a, b):
    if b == 0:
        return "REFUSE"
    q = (a * ONE) // b                             # python // is floor toward -inf for ints
    return q if -(1 << 63) <= q <= IMAX else "REFUSE"


if __name__ == "__main__":
    tests = [
        (6 * ONE, 2 * ONE), (1 * ONE, 3 * ONE), (-1 * ONE, 3 * ONE),
        (7 * ONE, 2 * ONE), (-7 * ONE, 2 * ONE), (7 * ONE, -2 * ONE),
        (ONE, ONE), (0, 5 * ONE), (10 * ONE, 4 * ONE), (-10 * ONE, 4 * ONE),
        (123456789, 987), (2**40, 2**8),           # last: result 2^64 -> REFUSE
    ]
    bad = 0
    for a, b in tests:
        got, exp = div(a, b), _truth(a, b)
        ok = (got == exp)
        bad += (0 if ok else 1)
        print(f"  {a}/{b}: got={got} exp={exp}  {'OK' if ok else 'MISMATCH'}")
    print("  div by zero:", div(5 * ONE, 0))
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} MISMATCH")
