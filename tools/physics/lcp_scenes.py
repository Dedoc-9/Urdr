# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical n-contact LCP corpus -- each certified solution digest is a witness.

A scene is (vels, inv_mass, masses, contacts). `masses[i] is None` marks a STATIC
body (a floor/wall; inverse mass 0). Module basename `lcp_scenes` is globally
unique across tools/ (the gate shares one sys.path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contact_lcp as L                                # noqa: E402
from contact_lcp import Contact                        # noqa: E402
from vecq import vec                                   # noqa: E402
from rational import Q, Z                              # noqa: E402


def _stack(n):
    """n balls (mass 1) resting on a static floor, each with downward velocity -1
    (one gravity step). 1D. Contacts: floor-b0, b0-b1, ... The exact impulses
    propagate: lambda = [n, n-1, ..., 1] (the bottom carries the whole stack)."""
    vels = [vec(0)] + [vec(-1)] * n                    # body 0 = floor (static)
    inv = [Z(0)] + [Z(1)] * n
    masses = [None] + [1] * n
    up = vec(1)
    contacts = [Contact(0, 1, up)]
    for i in range(1, n):
        contacts.append(Contact(i, i + 1, up))
    return vels, inv, masses, contacts


def sc_rest2():
    return _stack(2)


def sc_rest3():
    return _stack(3)


def sc_separating():
    """Two stacked balls already moving apart -> no impulse (lambda = 0)."""
    vels = [vec(0), vec(1), vec(3)]                     # floor still, balls rising, b2 faster
    inv = [Z(0), Z(1), Z(1)]
    masses = [None, 1, 1]
    up = vec(1)
    return vels, inv, masses, [Contact(0, 1, up), Contact(1, 2, up)]


def sc_corner2d():
    """A 2D ball driven into a right-angle corner (two axis-aligned walls); both
    contacts are active at once. lambda = [1,1]; the ball stops exactly."""
    vels = [vec(0, 0), vec(-1, -1)]                     # body 0 = walls anchor (static), 1 = ball
    inv = [Z(0), Z(1)]
    masses = [None, 1]
    contacts = [Contact(0, 1, vec(1, 0)), Contact(0, 1, vec(0, 1))]
    return vels, inv, masses, contacts


SCENES = {
    "rest2": sc_rest2,
    "rest3": sc_rest3,
    "separating": sc_separating,
    "corner2d": sc_corner2d,
}


def run(name):
    vels, inv, masses, contacts = SCENES[name]()
    _new, lam, w = L.resolve(vels, inv, contacts)
    return lam, w


if __name__ == "__main__":
    for name in sorted(SCENES):
        lam, w = run(name)
        print(name, L.lcp_digest(lam, w),
              "lambda=" + str([f"{q.n}/{q.d}" for q in lam]))
