# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics rung 5 -- BOUNDED fixed-point dynamics (the deterministic real-time path).

Rungs 1-4 are EXACT over ℚ: bit-perfect, but their denominators grow, so they REFUSE on any
long / iterated simulation (a gravity drop overflows i64 in a handful of steps; a joint
sim in ~2). This rung trades exactness for SCALE on the FROZEN Q32.32 substrate
(`field.FixedPoint`: radix 2^32, round-to-nearest ties-away -- every compiler/CPU rounds
identically). It is BOUNDED (never overflows for a bounded scene; REFUSES rather than wrap)
and DETERMINISTIC (bit-identical across placements), so it TIME-STEPS as long as you like
exactly where the exact rungs must refuse.

Two reference steppers, each the fixed-point port of an exact solver:
  * `run_stack`  -- a vertical contact stack that SETTLES under gravity via bounded
    sequential-impulse (PGS) + ground-up position projection + a sleep clamp. All contact
    normals are axis-aligned, so no square root is needed. (Fixed-point port of the exact
    contact LCP, rung 3.)
  * `run_swing`  -- an articulated pendulum that SWINGS under a distance constraint held
    with Baumgarte feedback on the SQUARED length (`d·d − L²`), so no sqrt appears and the
    value never leaves i64 -- removing the drift the exact joint solver could not sustain
    past two steps. (Fixed-point port of the exact articulated solver, rung 4.)

Each scene emits a per-tick canonical `URDRFPD1` state digest; the whole run is summarized by
a `URDRFPT1` TRACE digest (the gate's witness).

GRADE (honest, D5): the REPRODUCIBILITY of these steppers is MEASURED -- each scene's trace
digest is reproduced bit-for-bit and gated against a frozen golden (`conformance_fp.txt`),
with a NON-VACUOUS defect self-test (a wrong step -- no sleep clamp / no Baumgarte -- reddens
the gate). The FixedPoint SUBSTRATE these consume is already cross-placed (FIELDFP in
`urdr-physics-rs`). A SECOND independent placement of THESE STEPPERS is a DECLARED next rung;
until it lands, the steppers' own cross-placement is NOT yet MEASURED, only their single-
placement reproducibility. This is the honest complement to the exact rungs:
uniqueness-by-certificate is replaced by reproducibility-by-frozen-rounding."""
import hashlib

from field import FixedPoint as FP, ONE, _rdiv


def fp(v):
    return FP.unit(v, 1)                                   # integer → Q32.32


def fmul(a, b):
    return FP._g(_rdiv(a * b, ONE))                        # fixed × fixed (rounds; guards i64)


def fdiv(a, b):
    return FP._g(_rdiv(a * ONE, b))                        # fixed ÷ fixed (rounds; guards i64)


def state_digest(cols, magic=b"URDRFPD1"):
    """Canonical digest of a fixed-point state: each column's Q32.32 words, big-endian."""
    out = bytearray(magic)
    for arr in cols:
        for a in arr:
            out += FP.ser(a)
    return hashlib.sha256(bytes(out)).hexdigest()


def trace_digest(frames, magic=b"URDRFPT1"):
    """Digest of a whole run = SHA-256 over the ordered per-tick state digests."""
    h = hashlib.sha256()
    h.update(magic)
    for d in frames:
        h.update(d.encode())
    return h.hexdigest()


# -- settling contact stack (fixed-point port of the exact LCP) -----------------------
def run_stack(N=3, steps=240, K=20, R=20, H=300, sleep_clamp=True):
    """A vertical stack of N equal balls dropped onto a floor under gravity. Bounded PGS
    contacts + ground-up projection + (optional) sleep clamp bring it to rest. Returns
    (trace_digest, final velocities). `sleep_clamp=False` is the DEFECT variant used by the
    non-vacuity self-test -- it leaves residual jitter, so the trace differs."""
    Rf, ygf, twoR = fp(R), fp(H - 40), fp(2 * R)
    GDT, SLEEP = FP.unit(4, 10), FP.unit(5, 2)
    py = [FP.unit(50 + i * 44, 1) for i in range(N)]
    vy = [0] * N
    frames = []
    for _t in range(steps + 1):
        frames.append(state_digest((py, vy)))
        for i in range(N):
            vy[i] = FP.add(vy[i], GDT)
        for i in range(N):
            py[i] = FP.add(py[i], vy[i])
        order = sorted(range(N), key=lambda i: -py[i])          # bottom (max y) first
        lf, lb = {}, {}
        for _ in range(K):
            for i in order:                                     # floor: effmass = invm(1)
                if FP.add(py[i], Rf) > ygf and vy[i] > 0:
                    acc = lf.get(i, 0); newl = acc + vy[i]; lf[i] = newl
                    vy[i] = FP.sub(vy[i], newl - acc)
            for k in range(len(order) - 1):                     # ball-ball: effmass = 2
                lo, up = order[k], order[k + 1]
                if FP.sub(py[lo], py[up]) < twoR and FP.sub(vy[lo], vy[up]) < 0:
                    acc = lb.get((lo, up), 0)
                    dl = FP.mul_k(FP.sub(vy[up], vy[lo]), 1, 2)
                    newl = acc + dl; d = newl - acc; lb[(lo, up)] = newl
                    vy[up] = FP.sub(vy[up], d); vy[lo] = FP.add(vy[lo], d)
        for i in order:                                         # ground-up position projection
            if FP.add(py[i], Rf) > ygf:
                py[i] = FP.sub(ygf, Rf)
        for k in range(len(order) - 1):
            lo, up = order[k], order[k + 1]
            if FP.sub(py[lo], py[up]) < twoR:
                py[up] = FP.sub(py[lo], twoR)
        if sleep_clamp:
            for i in set(lf) | {u for (l, u) in lb}:
                if -SLEEP < vy[i] < SLEEP:
                    vy[i] = 0
    return trace_digest(frames), list(vy)


# -- articulated pendulum (fixed-point port of the exact joint solver) ----------------
def run_swing(steps=220, W=380, baumgarte=True):
    """A ball on a rigid rod swings under gravity. The distance constraint is held at the
    velocity level with Baumgarte feedback on the SQUARED length (no sqrt), which removes the
    drift the exact ℚ solver could not sustain. Returns (trace_digest, final position).
    `baumgarte=False` is the DEFECT variant -- the rod drifts, so the trace differs."""
    ax, ay = fp(W // 2), fp(60)
    px, py = FP.unit(W // 2 + 90, 1), fp(60)
    vx = vy = 0
    GDT = FP.unit(3, 10)
    L2_0 = None
    frames = []
    for _t in range(steps + 1):
        frames.append(state_digest(([px], [py], [vx], [vy])))
        vy = FP.add(vy, GDT)
        nx, ny = FP.sub(px, ax), FP.sub(py, ay)
        dd = FP.add(fmul(nx, nx), fmul(ny, ny))
        if L2_0 is None:
            L2_0 = dd
        jv = FP.add(fmul(nx, vx), fmul(ny, vy))
        if dd > 0:
            bias = FP.mul_k(FP.sub(dd, L2_0), 1, 6) if baumgarte else 0
            lam = fdiv(FP.sub(FP.sub(0, bias), jv), dd)
            vx = FP.add(vx, fmul(lam, nx)); vy = FP.add(vy, fmul(lam, ny))
        px = FP.add(px, vx); py = FP.add(py, vy)
    return trace_digest(frames), (px, py)
