# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical articulated-constraint corpus -- each solved-system digest is a
witness. A scene is (vels, inv_mass, masses, rows). `masses[i] is None` marks a
STATIC body (an anchor/rail; inverse mass 0). Module basename `joint_scenes` is
globally unique across tools/ (the gate shares one sys.path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import articulated as J                                # noqa: E402
from vecq import vec                                   # noqa: E402
from rational import Z                                 # noqa: E402


def sc_rod():
    """Two bodies joined by a rigid rod; one moving. After the solve the rod
    length-rate is zero and both bodies share the along-rod velocity."""
    pa, pb = vec(0, 0), vec(2, 0)
    vels = [vec(1, 0), vec(0, 0)]
    inv = [Z(1), Z(1)]
    masses = [1, 1]
    rows = [J.distance_row(0, 1, pa, pb)]
    return vels, inv, masses, rows


def sc_pendulum():
    """A bob pinned to a STATIC anchor (2 equality rows); its velocity is driven
    to zero -- it hangs from the pin."""
    vels = [vec(0, 0), vec(3, 5)]
    inv = [Z(0), Z(1)]
    masses = [None, 1]
    rows = J.pin_rows(0, 1, 2)
    return vels, inv, masses, rows


def sc_chain3():
    """Three bodies in a line joined by two rods; the leftmost is struck. The
    coupled solve propagates the constraint exactly."""
    p = [vec(0, 0), vec(1, 0), vec(2, 0)]
    vels = [vec(2, 0), vec(0, 0), vec(0, 0)]
    inv = [Z(1), Z(1), Z(1)]
    masses = [1, 1, 1]
    rows = [J.distance_row(0, 1, p[0], p[1]),
            J.distance_row(1, 2, p[1], p[2])]
    return vels, inv, masses, rows


def sc_triangle():
    """Three bodies, three rods -- a rigid triangle. The constraint Jacobian IS
    the rigidity matrix; the solve holds every edge length rigid."""
    p = [vec(0, 0), vec(2, 0), vec(0, 2)]
    vels = [vec(1, 1), vec(0, 0), vec(0, 0)]
    inv = [Z(1), Z(1), Z(1)]
    masses = [1, 1, 1]
    rows = [J.distance_row(0, 1, p[0], p[1]),
            J.distance_row(1, 2, p[1], p[2]),
            J.distance_row(2, 0, p[2], p[0])]
    return vels, inv, masses, rows


SCENES = {
    "rod": sc_rod,
    "pendulum": sc_pendulum,
    "chain3": sc_chain3,
    "triangle": sc_triangle,
}


def run(name):
    vels, inv, _masses, rows = SCENES[name]()
    new, lam = J.solve(vels, inv, rows)
    return new, lam, rows


if __name__ == "__main__":
    for name in sorted(SCENES):
        new, lam, _rows = run(name)
        print(name, J.joint_digest(new, lam),
              "lambda=" + str([f"{q.n}/{q.d}" for q in lam]))
