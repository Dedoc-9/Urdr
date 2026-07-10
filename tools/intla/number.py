#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-math number theory: gcd, extended_gcd (Bezout), modular inverse. Deterministic,
integer-first, using the proven exact floor_divmod. i64-overflow = REFUSE. Run -> BATTERY: ALL OK."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intdiv_algorithm import floor_divmod
IMAX = (1 << 63) - 1


def gcd(a, b):
    a, b = (a if a >= 0 else -a), (b if b >= 0 else -b)
    while b != 0:
        _, r = floor_divmod(a, b)          # a,b >= 0 -> floor divmod is the euclidean step
        a, b = b, r
    return a


def extended_gcd(a, b):
    """(g, x, y) with a*x + b*y = g, g >= 0. REFUSE if a coefficient overflows i64."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q, _ = floor_divmod(old_r, r)
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    g, x, y = old_r, old_s, old_t
    if g < 0:
        g, x, y = -g, -x, -y
    if any(abs(w) > IMAX for w in (x, y)):
        return "REFUSE"
    return g, x, y


def modinv(a, m):
    """Inverse of a mod m (m > 1), or 'REFUSE' if gcd(a,m) != 1."""
    r = extended_gcd(a, m)
    if r == "REFUSE":
        return "REFUSE"
    g, x, _ = r
    if g != 1:
        return "REFUSE"
    _, inv = floor_divmod(x, m)            # normalize into [0, m)
    return inv


def _battery():
    bad = 0
    random.seed(21)
    for _ in range(40000):
        a = random.randint(-10**9, 10**9)
        b = random.randint(-10**9, 10**9)
        if gcd(a, b) != math.gcd(a, b):
            bad += 1
        eg = extended_gcd(a, b)
        if eg != "REFUSE":
            g, x, y = eg
            if g != math.gcd(a, b) or a * x + b * y != g:
                bad += 1
    for _ in range(20000):
        m = random.randint(2, 10**6)
        a = random.randint(1, m - 1)
        inv = modinv(a, m)
        if math.gcd(a, m) == 1:
            if inv == "REFUSE" or (a * inv) % m != 1:
                bad += 1
        else:
            if inv != "REFUSE":
                bad += 1
    print("number: gcd/extended_gcd/modinv", "ALL OK" if bad == 0 else f"{bad} bad")
    return bad == 0


if __name__ == "__main__":
    sys.exit(0 if _battery() else 1)
