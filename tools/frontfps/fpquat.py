#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpquat — the Q32.32 rotation substrate (frontfps Stage 2, URDRFPQ1).

Quaternion operations on the FROZEN FIELDFP fixed-point laws (`tools/physics/
field.py`): radix ONE = 2^32, round-to-nearest ties-away division `_rdiv`, i64
refusal ceiling. Nothing here invents arithmetic — every rounding point reuses
`_rdiv`, and every op is a pinned integer recipe a placement reproduces verbatim
(reproducibility-by-frozen-rounding, the rung-5 philosophy applied to rotation).

Ops (all inputs Q32.32 raw i64, admission bound |raw| ≤ COMP_MAX = 2^61 so every
intermediate provably fits a signed 128-bit integer in every placement):

  fqmul(a,b)        fixed multiply — ONE rounding: _rdiv(a·b, ONE)
  qconj(q)          exact negation of the vector part
  qnorm2(q)         w²+x²+y²+z² summed EXACTLY, then ONE rounding
  qdot(p,q)         mixed products summed exactly, then ONE rounding
  qmul(p,q)         Hamilton product — each component: 4 exact products,
                    exact signed sum, ONE rounding (never 4 roundings)
  rsqrt(x)          reciprocal square root — the frozen integer recipe
                    isqrt(2^96 // x): Newton integer isqrt with final
                    adjustment; NO iteration count to tune, NO float ever;
                    result within 2 ulp of 2^48/√x (proved by inequality,
                    not sampled: r²·x ≤ 2^96 < (r+2)²·x)
  qnormalize(q)     componentwise fqmul(c, rsqrt(qnorm2(q)))
  vrotate(q,v)      v + w·t + u×t with t = 2(u×v); each cross component and
                    each w·t component takes ONE rounding, in the written order
  qnlerp(p,q,t)     shortest-path (qdot < 0 ⇒ negate q, exact) normalized lerp:
                    per component ONE rounding of p·(ONE−t) + q·t, then
                    qnormalize; t ∈ [0, ONE] refused outside — nlerp needs no
                    trigonometry, which is why it is Stage 2 and slerp is not

Refusals are total and typed (`FPQ-REFUSE`): non-integer input, |raw| beyond
COMP_MAX, i64 overflow on any result, rsqrt of x ≤ 0, normalize of a zero/
degenerate quaternion, nlerp t outside [0, ONE]. No wrap, no clamp, no guess.

THE DEFECTS SHIP IN-MODULE (gate non-vacuity): `battery_digest_defect_truncdiv`
(floor division instead of the frozen round-to-nearest — the same law the field
stage proves) and `battery_digest_defect_wrap64` (quaternion products summed in
wrapping 64-bit arithmetic — the porting hazard this repo has actually hit:
the rigidity port note reads 'a naive i64 multiply wraps and diverges'; the
battery's large quaternion exists precisely to force that wrap).

GRADE (Stage 2, reference placement): maturity IMPLEMENTED; evidence MEASURED via
the `frontfps_quat` gate stage + `tests/test_fpquat.py` (battery golden ×2, the
rsqrt inequality law, normalize/rotate bounds, refusal canaries, both defects
diverging). Cross-placement: C99 placement in `fpquat_c/` (self-verified where a
gcc host exists); Rust placement in `fpquat_rs/` SPECULATIVE until a named host
prints ADMITTED twice with the defect caught. `does_not_show`: anything about
angles, slerp, or animation — that is Stage 3; and no real-time performance claim.
Falsifier: any independent implementation of this docstring disagreeing with the
pinned battery digest.
"""
import hashlib
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PHYS = os.path.join(os.path.dirname(_HERE), "physics")
if _PHYS not in sys.path:
    sys.path.insert(0, _PHYS)

from field import ONE, _rdiv  # the FROZEN substrate laws (FIELDFP)  # noqa: E402

IMAX = (1 << 63) - 1
COMP_MAX = 1 << 61          # op-input admission bound (i128 headroom, proved in docstring)
MAGIC = b"URDRFPQ1"


class FpqError(Exception):
    def __init__(self, message):
        super().__init__(f"FPQ-REFUSE: {message}")
        self.code = "FPQ-REFUSE"


def _fg(v):
    if v > IMAX or v < -IMAX:
        raise FpqError(f"i64 overflow ({v})")
    return v


def _fin(v, what):
    if not isinstance(v, int) or isinstance(v, bool):
        raise FpqError(f"{what}={v!r} is not an integer raw Q32.32 word")
    if v > COMP_MAX or v < -COMP_MAX:
        raise FpqError(f"{what}={v} beyond COMP_MAX=±2^61 (admission bound)")
    return v


def _quat(q, what):
    if not (isinstance(q, tuple) and len(q) == 4):
        raise FpqError(f"{what} is not a (w,x,y,z) tuple")
    return tuple(_fin(c, f"{what}[{i}]") for i, c in enumerate(q))


def _vec(v, what):
    if not (isinstance(v, tuple) and len(v) == 3):
        raise FpqError(f"{what} is not an (x,y,z) tuple")
    return tuple(_fin(c, f"{what}[{i}]") for i, c in enumerate(v))


# ---- the frozen integer isqrt (Newton + final adjustment) ----------------------------
def _isqrt_newton(n):
    """Exact floor integer sqrt by Newton's method — THE recipe every placement
    ports (u128 arithmetic suffices for every admitted input). Equality with the
    mathematical isqrt is a falsifier, not a hope (tests assert == math.isqrt)."""
    if n < 0:
        raise FpqError(f"isqrt of negative ({n})")
    if n < 2:
        return n
    r = 1 << ((n.bit_length() + 1) // 2)
    while True:
        nr = (r + n // r) // 2
        if nr >= r:
            break
        r = nr
    # belt-and-braces adjustment: provably unreachable for THIS stop rule, kept
    # so a mis-ported Newton variant still lands exactly on floor(√n)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r


def _w64(v):
    """Two's-complement i64 wrap — the arithmetic a careless port gets for free.
    Exists ONLY for the defect below; the real ops never wrap, they refuse."""
    return ((v + (1 << 63)) & ((1 << 64) - 1)) - (1 << 63)


# ---- ops (every rounding point is _rdiv; every recipe is the spec) --------------------
def fqmul(a, b, _div=_rdiv):
    return _fg(_div(_fin(a, "a") * _fin(b, "b"), ONE))


def qconj(q):
    w, x, y, z = _quat(q, "q")
    return (w, -x, -y, -z)


def qnorm2(q, _div=_rdiv):
    w, x, y, z = _quat(q, "q")
    return _fg(_div(w * w + x * x + y * y + z * z, ONE))


def qdot(p, q, _div=_rdiv):
    pw, px, py, pz = _quat(p, "p")
    qw, qx, qy, qz = _quat(q, "q")
    return _fg(_div(pw * qw + px * qx + py * qy + pz * qz, ONE))


def qmul(p, q, _div=_rdiv):
    pw, px, py, pz = _quat(p, "p")
    qw, qx, qy, qz = _quat(q, "q")
    return (_fg(_div(pw * qw - px * qx - py * qy - pz * qz, ONE)),
            _fg(_div(pw * qx + px * qw + py * qz - pz * qy, ONE)),
            _fg(_div(pw * qy - px * qz + py * qw + pz * qx, ONE)),
            _fg(_div(pw * qz + px * qy - py * qx + pz * qw, ONE)))


def rsqrt(x):
    _fin(x, "x")
    if x <= 0:
        raise FpqError(f"rsqrt domain: x={x} ≤ 0")
    return _fg(_isqrt_newton((1 << 96) // x))


def qnormalize(q, _div=_rdiv):
    n2 = qnorm2(q, _div)
    if n2 <= 0:
        raise FpqError(f"normalize of zero/degenerate quaternion (norm2={n2})")
    r = rsqrt(n2)
    w, x, y, z = q
    return (_fg(_div(w * r, ONE)), _fg(_div(x * r, ONE)),
            _fg(_div(y * r, ONE)), _fg(_div(z * r, ONE)))


def vrotate(q, v, _div=_rdiv):
    """v' = v + w·t + u×t, t = 2(u×v) — the written rounding order IS the spec."""
    w, ux, uy, uz = _quat(q, "q")
    vx, vy, vz = _vec(v, "v")
    tx = _fg(2 * _div(uy * vz - uz * vy, ONE))
    ty = _fg(2 * _div(uz * vx - ux * vz, ONE))
    tz = _fg(2 * _div(ux * vy - uy * vx, ONE))
    return (_fg(vx + _div(w * tx, ONE) + _div(uy * tz - uz * ty, ONE)),
            _fg(vy + _div(w * ty, ONE) + _div(uz * tx - ux * tz, ONE)),
            _fg(vz + _div(w * tz, ONE) + _div(ux * ty - uy * tx, ONE)))


def qnlerp(p, q, t, _div=_rdiv):
    _fin(t, "t")
    if not (0 <= t <= ONE):
        raise FpqError(f"nlerp t={t} outside [0, ONE] — refused, never clamped")
    pq = _quat(p, "p")
    qq = _quat(q, "q")
    if qdot(pq, qq, _div) < 0:                     # shortest path, exact negation
        qq = tuple(-c for c in qq)
    li = ONE - t
    blend = tuple(_fg(_div(pc * li + qc * t, ONE)) for pc, qc in zip(pq, qq))
    return qnormalize(blend, _div)


# ---- the pinned battery (the corpus is a digest of these results) ---------------------
H = ONE // 2
Q3 = 3 * ONE // 4
T3 = ONE // 3

QUATS = ((ONE, 0, 0, 0),
         (ONE, H, 0, 0),
         (ONE, H, Q3, -T3),
         (3 * ONE, -2 * ONE, ONE, H))

VECS = ((ONE, 0, 0),
        (0, ONE, 0),
        (H, Q3, -ONE),
        (5 * ONE, -3 * ONE, 2 * ONE + 12345))

RSQRT_IN = (1, 2, ONE // 4, H, ONE, 2 * ONE, 3 * ONE, 10 * ONE,
            (1 << 48) + 7919, COMP_MAX)

NLERP_T = (0, ONE // 4, H, ONE)


def _ser(a):
    return int(a).to_bytes(8, "big", signed=True)      # FIELDFP serialization


def _battery(_div=_rdiv):
    """The fixed op battery. Returns ordered (tag, [raw…]) rows — the corpus."""
    rows = []
    for x in RSQRT_IN:
        rows.append(("rsqrt", [rsqrt(x)]))
    for q in QUATS:
        rows.append(("norm2", [qnorm2(q, _div)]))
    for p in QUATS:
        for q in QUATS:
            rows.append(("qmul", list(qmul(p, q, _div))))
    units = []
    for q in QUATS:
        u = qnormalize(q, _div)
        units.append(u)
        rows.append(("normalize", list(u)))
    for u in units:
        for v in VECS:
            rows.append(("rotate", list(vrotate(u, v, _div))))
    for i in range(len(QUATS)):
        p, q = QUATS[i], QUATS[(i + 1) % len(QUATS)]
        for t in NLERP_T:
            rows.append(("nlerp", list(qnlerp(p, q, t, _div))))
    return rows


def battery_digest(_div=_rdiv):
    h = hashlib.sha256()
    h.update(MAGIC)
    for tag, vals in _battery(_div):
        h.update(tag.encode("ascii"))
        for v in vals:
            h.update(_ser(v))
    return h.hexdigest()


def battery_digest_defect_truncdiv():
    """Floor division instead of the frozen round-to-nearest — MUST diverge
    (the same law the field stage proves: truncation ≠ _rdiv)."""
    def flo(p, d):
        return p // d
    return battery_digest(_div=flo)


def battery_digest_defect_wrap64():
    """THE PORT DEFECT actually observed in this repo's history (rigidity port
    note: 'a naive i64 multiply wraps and diverges'): quaternion products and
    norm sums computed in wrapping 64-bit arithmetic instead of 128-bit. MUST
    diverge from the golden — the battery's large quaternion exists to force it."""
    def qnorm2_w(q):
        w, x, y, z = q
        s = _w64(_w64(_w64(w * w) + _w64(x * x)) + _w64(_w64(y * y) + _w64(z * z)))
        return _rdiv(s, ONE)

    def qmul_w(p, q):
        pw, px, py, pz = p
        qw, qx, qy, qz = q

        def m(a, b):
            return _w64(a * b)
        return (_rdiv(_w64(_w64(m(pw, qw) - m(px, qx)) - _w64(m(py, qy) + m(pz, qz))), ONE),
                _rdiv(_w64(_w64(m(pw, qx) + m(px, qw)) + _w64(m(py, qz) - m(pz, qy))), ONE),
                _rdiv(_w64(_w64(m(pw, qy) - m(px, qz)) + _w64(m(py, qw) + m(pz, qx))), ONE),
                _rdiv(_w64(_w64(m(pw, qz) + m(px, qy)) - _w64(m(py, qx) - m(pz, qw))), ONE))

    h = hashlib.sha256()
    h.update(MAGIC)
    for x in RSQRT_IN:
        h.update(b"rsqrt")
        h.update(_ser(rsqrt(x)))
    for q in QUATS:
        h.update(b"norm2")
        h.update(_ser(_w64(qnorm2_w(q))))
    for p in QUATS:
        for q in QUATS:
            h.update(b"qmul")
            for v in qmul_w(p, q):
                h.update(_ser(_w64(v)))
    units = [qnormalize(q) for q in QUATS]
    for u in units:
        h.update(b"normalize")
        for c in u:
            h.update(_ser(c))
    for u in units:
        for v in VECS:
            h.update(b"rotate")
            for c in vrotate(u, v):
                h.update(_ser(c))
    for i in range(len(QUATS)):
        p, q = QUATS[i], QUATS[(i + 1) % len(QUATS)]
        for t in NLERP_T:
            h.update(b"nlerp")
            for c in qnlerp(p, q, t):
                h.update(_ser(c))
    return h.hexdigest()


if __name__ == "__main__":
    d = battery_digest()
    rows = _battery()
    print(f"URDRFPQ1 battery: {len(rows)} rows, digest {d}")
    print("defect truncdiv diverges:", battery_digest_defect_truncdiv() != d)
    print("defect wrap64 diverges:", battery_digest_defect_wrap64() != d)
    print("isqrt ≡ math.isqrt spot:", all(_isqrt_newton(n) == math.isqrt(n)
                                          for n in (0, 1, 2, 3, 4, 5, 24, 25, 26,
                                                    (1 << 96) // ONE, (1 << 96) // 3)))
