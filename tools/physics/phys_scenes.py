# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical physics corpus -- each scene's post-step state digest is a witness.

NOTE the module name is `phys_scenes`, not `scenes`: the gate assembles ONE
sys.path across every tool dir, so a bare module basename must be globally unique
across tools/ (a `scenes` in two tools would collide via sys.modules — a bug the
render/physics pair actually hit). Keep tool module basenames unique.

A scene is (bodies, forces, dt, restitution). All coordinates are exact rationals
(no float), so the state digest after one deterministic step is a reproducible
witness under the same discipline as the frame digest (D11 §4) and the kernel
digest (D8)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dynamics as D                                  # noqa: E402
from dynamics import Body                             # noqa: E402
from rational import Z                                # noqa: E402


def sc_free():
    """A single free body drifts at constant velocity (momentum conserved)."""
    return ([Body(Z(0), Z(0), Z(3), 2)], [Z(0)], Z(1), Z(1))


def sc_gravity():
    """A body under a constant force, one semi-implicit Euler step."""
    return ([Body(Z(0), Z(0), Z(0), 2)], [Z(-2)], Z(1), Z(1))


def sc_elastic():
    """Two bodies, head-on, restitution 1 (energy conserved exactly)."""
    return ([Body(Z(0), Z(1), Z(2), 3), Body(Z(5), Z(1), Z(-1), 5)],
            [Z(0), Z(0)], Z(1), Z(1))


def sc_inelastic():
    """Same setup, restitution 0 (energy strictly decreases; rel-vel -> 0)."""
    return ([Body(Z(0), Z(1), Z(2), 3), Body(Z(5), Z(1), Z(-1), 5)],
            [Z(0), Z(0)], Z(1), Z(0))


def sc_ccd_tunnel():
    """A fast body that would skip a thin heavy wall in one discrete step; CCD
    catches the exact time-of-impact so it cannot tunnel."""
    return ([Body(Z(0), Z(0), Z(10), 1), Body(Z(5), Z(0), Z(0), 1000000)],
            [Z(0), Z(0)], Z(1), Z(1))


SCENES = {
    "free": sc_free,
    "gravity": sc_gravity,
    "elastic": sc_elastic,
    "inelastic": sc_inelastic,
    "ccd_tunnel": sc_ccd_tunnel,
}


def run(name):
    bodies, forces, dt, e = SCENES[name]()
    return D.step(bodies, forces, dt, e)


if __name__ == "__main__":
    for name in sorted(SCENES):
        print(name, D.state_digest(run(name)))
