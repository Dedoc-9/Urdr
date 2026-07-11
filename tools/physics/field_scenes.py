# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical field-transport corpus. Three FIELDFP (fixed-point, real-time path)
and one tiny FIELDQ (exact, scoped-small) scene — exercising both backends and
the backend-tag-in-identity rule. Module basename `field_scenes` is globally
unique across tools/ (the gate shares one sys.path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import field as FLD                                    # noqa: E402
from field import FixedPoint, Exact, ONE               # noqa: E402


def _fp(k, vx, vy, steps):
    w = h = 8
    g = [0] * (w * h)
    g[4 * w + 4] = ONE                                  # unit bump at the center
    for _ in range(steps):
        g = FLD.step(FixedPoint, g, w, h, k, vx, vy)
    return FixedPoint, g, w, h


def sc_diffuse():
    """Pure diffusion of a central heat bump (v=0), 100 steps."""
    return _fp((1, 8), (0, 1), (0, 1), 100)


def sc_advect():
    """Pure advection (k=0), velocity +x, 100 steps — the bump drifts and piles
    against the zero-flux wall (mass conserved)."""
    return _fp((0, 1), (1, 2), (0, 1), 100)


def sc_adv_diff():
    """Combined advection + diffusion, diagonal velocity, 100 steps. Parameters
    satisfy the monotonicity/CFL bound 4k+vx+vy ≤ 1 (here 1/4+1/4+1/4 = 3/4), so
    the field stays bounded and non-negative."""
    return _fp((1, 16), (1, 4), (1, 4), 100)


def sc_exactq():
    """A tiny 4x4 EXACT (FIELDQ) field, 3 steps — exact + mass-conserved, and it
    fits i64 (larger/longer would refuse). Demonstrates the pluggable backend and
    the distinct backend identity."""
    w = h = 4
    g = [Exact.unit(0, 1)] * (w * h)
    g[2 * w + 2] = Exact.unit(1, 1)
    for _ in range(3):
        g = FLD.step(Exact, g, w, h, (1, 8), (1, 2), (0, 1))
    return Exact, g, w, h


SCENES = {
    "diffuse": sc_diffuse,
    "advect": sc_advect,
    "adv_diff": sc_adv_diff,
    "exactq": sc_exactq,
}


def run(name):
    B, g, w, h = SCENES[name]()
    return FLD.digest(B, g, w, h)


if __name__ == "__main__":
    for name in sorted(SCENES):
        print(name, run(name))
