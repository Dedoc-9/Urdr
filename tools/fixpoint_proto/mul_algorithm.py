#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for the Urðr Q32.32 `mul` (D9 §4).

This is NOT part of the language. It is a *faithful prototype*: it computes
floor(a*b / 2^32) for Q32.32 fixed-point using ONLY operations Urðr's core has —
`+ - *` (i64), comparisons, and folds. NO `//`, `%`, `<<`, `>>`, no recursion.
Every intermediate is provably < 2^63 (no i64 wrap). It exists so the intricate
Urðr encoding has a proven target to reproduce, tested against the exact truth
`floor(a*b/2^32)`. The algorithm — not this file — is what the Urðr `mul` must
mirror. `algorithm proven ≠ Urðr mul measured`: the ledger keeps `mul`
SPECULATIVE until it runs in the language and agrees on both placements.

Run: `python3 tools/fixpoint_proto/mul_algorithm.py` — prints BATTERY: ALL OK.
"""
ONE = 1 << 32
IMAX = (1 << 63) - 1
POWERS = [1 << i for i in range(46, -1, -1)]  # 2^46 .. 2^0 (>= any quotient bit here)


def floordiv_pow(x, k):
    """(floor(x / 2^k), x mod 2^k) for x in [0, 2^63), overflow-safe.

    Build q bit by bit; the test is `p*2^k <= x - acc` — both sides < 2^63, so
    no i64 wrap. This is the division-by-a-power-of-two that Urðr lacks, done as
    a fold over descending powers (place values)."""
    W = 1 << k
    q = 0
    acc = 0
    for p in POWERS:
        pw = p * W
        if pw <= 0 or pw > IMAX:      # place value out of range for this weight
            continue
        if pw <= x - acc:            # <=> acc + pw <= x, computed without overflow
            q += p
            acc += pw
    return q, x - acc


def umul(A, B):
    """floor(A*B / 2^32) and (A*B mod 2^32) for A, B in [0, 2^63)."""
    def limbs16(X):
        a3, _ = floordiv_pow(X, 48); r = X - a3 * (1 << 48)
        a2, _ = floordiv_pow(r, 32); r = r - a2 * (1 << 32)
        a1, _ = floordiv_pow(r, 16); r = r - a1 * (1 << 16)
        return [r, a1, a2, a3]                       # [a0, a1, a2, a3], 16-bit each
    a, b = limbs16(A), limbs16(B)
    P = [0] * 7                                      # P_k = sum_{i+j=k} a_i b_j ; each < 2^34
    for i in range(4):
        for j in range(4):
            P[i + j] += a[i] * b[j]
    # A*B = sum P_k * 2^(16k). Normalize into base-2^16 limbs L (low->high) with carry.
    L, carry = [], 0
    for k in range(7):
        c, rem = floordiv_pow(P[k] + carry, 16)
        L.append(rem); carry = c
    while carry > 0:
        c, rem = floordiv_pow(carry, 16); L.append(rem); carry = c
    # floor(value / 2^32) drops limb positions 0,1 (each limb is 16 bits, 2^32 = 2^(16*2)).
    Q = 0
    for i in range(len(L) - 1, 1, -1):
        Q = Q * (1 << 16) + L[i]
    R = L[0] + L[1] * (1 << 16)                      # A*B mod 2^32
    return Q, R


def mul(a, b):
    """Q32.32 mul with the D9 refusal + floor(toward -inf) laws."""
    s = (1 if a >= 0 else -1) * (1 if b >= 0 else -1)
    A = a if a >= 0 else -a
    B = b if b >= 0 else -b
    Q, R = umul(A, B)
    if Q > IMAX:
        return "REFUSE"                              # overflow: die (URDR-ASSERT in Urðr)
    if s >= 0:
        return Q
    return -Q if R == 0 else -(Q + 1)                # floor toward -inf


def _truth(a, b):
    p = a * b
    return p >> 32 if p >= 0 else -((-p + ONE - 1) >> 32)


if __name__ == "__main__":
    tests = [
        (3 * ONE, 4 * ONE), (10 * ONE, 3 * ONE), (ONE, ONE), (0, 5 * ONE),
        (-3 * ONE, 4 * ONE), (3 * ONE, -4 * ONE), (-3 * ONE, -4 * ONE),
        (ONE // 2, ONE // 2), (-ONE // 2, ONE // 2), (7 * ONE + 123, 5 * ONE + 999),
        (12345678, 98765432), (-12345678, 98765432),
        (1234567890123, 45678), (2**40, 2**20), (2**31, 2**31),
    ]
    bad = 0
    for a, b in tests:
        got, exp = mul(a, b), _truth(a, b)
        ok = (got == exp)
        bad += (0 if ok else 1)
        print(f"  a={a} b={b}  got={got} exp={exp}  {'OK' if ok else 'MISMATCH'}")
    print("  overflow 2^62 * 2^62 ->", mul(1 << 62, 1 << 62))
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} MISMATCH")
