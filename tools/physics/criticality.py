# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-criticality — a deterministic branching-diffusion (reactor-kinetics) field.

A population field on a 1D lattice, evolved on the FROZEN Q32.32 backend (`field.FixedPoint`),
in the urdr-field family (advection-diffusion / Marangoni / loop). Three coupled pieces, the
reactor-physics reading of "keff = 2.0 × Galton board + Doppler":

  * TRANSPORT (the Galton board). The binomial left/right peg step IS a discrete diffusion
    kernel. Implemented in EXACT-CONSERVATIVE FLUX FORM (D = 1/4): per interior edge,
    `f = 1/4·(n[i] − n[i+1])`, then `n[i] -= f; n[i+1] += f`. What leaves one cell enters its
    neighbour, so total population is conserved EXACTLY regardless of rounding (the urdr-field
    "flux form: mass conserved exactly" discipline). Vacuum boundaries LEAK (1/4 of the edge
    cell escapes) — leakage is part of criticality; reflecting boundaries conserve.

  * MULTIPLICATION (keff). Each generation multiplies the population by the effective
    multiplication factor `keff` (a rational). `keff > 1` is SUPERCRITICAL — it grows
    geometrically, and under the bounded substrate it RAISES `FIELD-REFUSE` at the i64 ceiling
    rather than wrapping. `keff = 1` is critical (stationary); `keff < 1` is subcritical (decays).

  * DOPPLER (the regulator). The reactor negative-temperature feedback: as local density
    ("temperature") rises, effective keff falls. Here `k_eff(cell) = k0 · n_ref/(n_ref + n)` —
    a rational feedback (EXACT), driving `k_eff → 1` as `n` rises, so a supercritical `k0`
    self-limits to a BOUNDED steady state `n* = (k0 − 1)·n_ref` per cell. This is why
    `keff = 2.0` does not explode when Doppler is on: the feedback IS the stability.

Honest scope: 1D, one-group, a RATIONAL Doppler law (the physical Doppler defect ∝ √T is
irrational and would itself live in the bounded/refuse regime — DECLARED, not modelled here).
GRADE (D5): MEASURED (reference), bounded regime B (rounds honestly, refuses on overflow, never
wraps), deterministic; cross-placement DECLARED; NOT frozen. The witnessed properties: exact
transport conservation, the eigenvalue behaviour (k=1 stationary / k<1 decays / k>1 refuses),
the Galton distribution golden, and the Doppler-regulated steady-state golden — with the
non-vacuity defect that removing Doppler makes the supercritical field explode (FIELD-REFUSE)."""
import hashlib
import os as _os

from field import FixedPoint as FP, FieldError            # noqa: E402  frozen Q32.32 + FIELD-REFUSE

MAGIC = b"URDRKFF1"          # per-generation population-field digest
TRACE_MAGIC = b"URDRKFFT"    # whole-run trace digest
_HERE = _os.path.dirname(_os.path.abspath(__file__))


def _ser(a):
    return int(a).to_bytes(8, "big", signed=True)


def state_digest(n, gen):
    """SHA-256(MAGIC | W u32 BE | generation u32 BE | each cell as signed i64 BE)."""
    out = bytearray(MAGIC)
    out += len(n).to_bytes(4, "big")
    out += int(gen).to_bytes(4, "big")
    for x in n:
        out += _ser(x)
    return hashlib.sha256(bytes(out)).hexdigest()


def trace_digest(digests):
    """The whole-run witness = SHA-256 over the ordered per-generation digests."""
    h = hashlib.sha256()
    h.update(TRACE_MAGIC)
    for d in digests:
        h.update(d.encode())
    return h.hexdigest()


def total(n):
    """Exact total population (a running FixedPoint sum — the conserved quantity of transport)."""
    t = 0
    for x in n:
        t = FP.add(t, x)
    return t


# ---- the three coupled operators ----------------------------------------------------
def transport(n, reflect=False):
    """Exact-conservative Galton/diffusion step (flux form, D=1/4). Vacuum boundaries leak."""
    w = len(n)
    out = list(n)
    for i in range(w - 1):
        f = FP.mul_k(FP.sub(out[i], out[i + 1]), 1, 4)
        out[i] = FP.sub(out[i], f)
        out[i + 1] = FP.add(out[i + 1], f)
    if not reflect:
        out[0] = FP.sub(out[0], FP.mul_k(out[0], 1, 4))
        out[w - 1] = FP.sub(out[w - 1], FP.mul_k(out[w - 1], 1, 4))
    return out


def multiply(n, kn, kd):
    """Uniform multiplication by keff = kn/kd (production). Supercritical (>1) refuses at the bound."""
    return [FP.mul_k(x, kn, kd) for x in n]


def doppler(n, k0n, k0d, nref):
    """Doppler-regulated production: k_eff(cell) = (k0n/k0d)·nref/(nref + n), driving k_eff→1
    as density rises. `nref` is a Q32.32 word (the reference density)."""
    return [FP.mul_k(x, k0n * nref, k0d * (nref + x)) for x in n]


def step(n, k0n, k0d, reflect=False, doppler_on=False, nref=None):
    """One generation: transport, then production (Doppler-regulated or plain keff)."""
    n = transport(n, reflect)
    return doppler(n, k0n, k0d, nref) if doppler_on else multiply(n, k0n, k0d)


# ---- scenarios (pinned by the gate) -------------------------------------------------
def seed_field(w, value=1000, center=None):
    """A point source: `value` at the centre cell, zero elsewhere (the incident 'beam')."""
    n = [0] * w
    n[center if center is not None else w // 2] = FP.unit(value, 1)
    return n


def simulate(w, gens, k0n, k0d, reflect=False, doppler_on=False, nref=None, value=1000):
    """Run `gens` generations from a centred point source. Returns (states, digests) —
    `states` the per-generation population lists (display-only), `digests` the per-generation
    URDRKFF1 witnesses. Raises `FieldError('FIELD-REFUSE', …)` if the bounded substrate
    overflows (a supercritical excursion with no regulator)."""
    n = seed_field(w, value)
    states = [list(n)]
    digests = [state_digest(n, 0)]
    for g in range(1, gens + 1):
        n = step(n, k0n, k0d, reflect, doppler_on, nref)
        states.append(list(n))
        digests.append(state_digest(n, g))
    return states, digests


def galton_scene():
    """Pure transport (keff = 1) from a point source with vacuum leakage — the deterministic
    Galton board: an incident spike diffuses to the binomial spread, reproducibly."""
    return dict(w=21, gens=12, k0n=1, k0d=1, reflect=False, doppler_on=False, nref=None)


def regulated_scene():
    """Supercritical k0 = 2.0 with Doppler feedback (reflecting) — the self-limiting critical
    state: population converges to the bounded steady total and holds."""
    return dict(w=21, gens=120, k0n=2, k0d=1, reflect=True, doppler_on=True, nref=FP.unit(50, 1))


def unregulated_scene():
    """The DEFECT for the gate: the same supercritical k0 = 2.0 with NO Doppler — it explodes
    and RAISES FIELD-REFUSE at the i64 ceiling (Doppler is load-bearing)."""
    return dict(w=21, gens=120, k0n=2, k0d=1, reflect=True, doppler_on=False, nref=None)


def run_trace(scene):
    """The trace digest of a scenario dict (raises FieldError if the scene refuses)."""
    _states, digests = simulate(**scene)
    return trace_digest(digests)


def golden(name):
    path = _os.path.join(_HERE, "conformance_criticality.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FieldError("FIELD-REFUSE", f"no golden named {name!r}")
