#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bearing_octant_gen — the program that chose `bearing`'s octant (D26 §2). PROVENANCE, NOT AUTHORITY.

    python studio/bearing_octant_gen.py > tools/terrain/bearing_octant.txt

For every k in 0..45000 it writes one line `p q`: the rational t_k = p/q of smallest denominator in the
interval [tan((theta_k - tau)/2), tan((theta_k + tau)/2)], theta_k = k millidegrees, tau = a quarter of a
millidegree. Integers only: pi by Machin's formula and sin/cos by their series, in fixed point at PREC bits
with every truncation bounded, so each endpoint is known to within 2^-SHRINK_BITS; the search runs on the
interval shrunk inward by that much, so the chosen fraction lies inside the true interval. The smallest-
denominator fraction of an interval is unique (the Stern-Brocot descent), so the output is a function of
the rule and these two constants — no float, no host dependence.

The gate never runs this file. It checks the committed octant by its own invariants (D26 F2: Pythagorean,
primitive, anchors, symmetries, strict order, pinned sha256); the angle bound this program aims at stays
DECLARED, because its endpoints are irrational and the gate does not evaluate them.
"""
from fractions import Fraction
import sys

K_MAX = 45000                     # the octant: 0 .. 45 degrees in millidegrees
QUARTERS = 4 * 360000             # half-angle unit: (4k -+ 1) * pi / QUARTERS = (k -+ 1/4) mdeg / 2
PREC = 200                        # fixed-point bits
SHRINK_BITS = 160                 # each endpoint is known to within 2^-SHRINK_BITS; the interval shrinks inward by it


def _atan_inv(x, one):
    """atan(1/x) * one, truncated per term; error < (terms + 1) ulps."""
    total, term, n, sign = 0, one // x, 1, 1
    x2 = x * x
    while term:
        total += sign * (term // n)
        term //= x2
        n += 2
        sign = -sign
    return total


def _pi(one):
    return 16 * _atan_inv(5, one) - 4 * _atan_inv(239, one)


def _sin_cos(num, den, one, pi):
    """sin and cos of num*pi/den (a small angle), fixed point; error of a few hundred ulps at most."""
    x = pi * num // den
    s, c = 0, 0
    term = x                     # x^1/1!
    n, sign = 1, 1
    while term:
        s += sign * term
        term = term * x // one * x // one // ((n + 1) * (n + 2))
        n += 2
        sign = -sign
    term = one                   # x^0/0!
    n, sign = 0, 1
    while term:
        c += sign * term
        term = term * x // one * x // one // ((n + 1) * (n + 2))
        n += 2
        sign = -sign
    return s, c


def _tan_bounds(num, den, one, pi):
    """(lo, hi) as Fractions bracketing tan(num*pi/den), each within 2^-SHRINK_BITS of it."""
    s, c = _sin_cos(num, den, one, pi)
    t = Fraction(s, c)
    eps = Fraction(1, 1 << SHRINK_BITS)
    return t - eps, t + eps


def simplest_between(lo, hi):
    """The fraction of smallest denominator in the closed interval [lo, hi], 0 <= lo <= hi: the classic
    continued-fraction descent (floor, then the reciprocal of the remainder), exact on Fractions."""
    n = lo.numerator // lo.denominator
    if n == lo:
        return Fraction(n)
    if n + 1 <= hi:
        return Fraction(n + 1)
    return n + 1 / simplest_between(1 / (hi - n), 1 / (lo - n))


def octant():
    one = 1 << PREC
    pi = _pi(one)
    out = []
    for k in range(K_MAX + 1):
        if k == 0:
            out.append((0, 1))
            continue
        lo_lo, lo_hi = _tan_bounds(4 * k - 1, QUARTERS, one, pi)
        hi_lo, hi_hi = _tan_bounds(4 * k + 1, QUARTERS, one, pi)
        t = simplest_between(lo_hi, hi_lo)          # the interval shrunk inward: inside the true one
        out.append((t.numerator, t.denominator))
    return out


def main():
    for p, q in octant():
        sys.stdout.write("%d %d\n" % (p, q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
