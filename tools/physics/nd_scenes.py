# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical n-D physics corpus (2D & 3D) -- each post-step state digest is a
witness. Module basename is `nd_scenes` (globally unique across tools/ -- the
gate shares one sys.path). A scene is (bodies, forces, dt, restitution, walls)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dynamics_nd as D                                # noqa: E402
from dynamics_nd import Ball                           # noqa: E402
from vecq import vec, Vec                              # noqa: E402
from rational import Z                                 # noqa: E402


def sc_head2d():
    """2D head-on elastic collision along x (momentum vector + energy conserved)."""
    return ([Ball(vec(0, 0), Z(1), vec(2, 0), 3),
             Ball(vec(5, 0), Z(1), vec(-1, 0), 5)], Z(1), Z(1), ())


def sc_oblique2d():
    """2D oblique elastic collision (diagonal normal): the vector impulse and
    exact energy conservation with no square root."""
    return ([Ball(vec(0, 0), Z(1), vec(2, 1), 2),
             Ball(vec(3, 3), Z(1), vec(-1, -1), 4)], Z(1), Z(1), ())


def sc_inelastic2d():
    """2D oblique, restitution 0 (momentum conserved; energy strictly lost)."""
    return ([Ball(vec(0, 0), Z(1), vec(2, 1), 2),
             Ball(vec(3, 3), Z(1), vec(-1, -1), 4)], Z(1), Z(0), ())


def sc_oblique3d():
    """3D oblique elastic collision -- the SAME code, one more dimension."""
    return ([Ball(vec(0, 0, 0), Z(1), vec(1, 2, 3), 2),
             Ball(vec(2, 2, 2), Z(1), vec(-1, 0, -1), 3)], Z(1), Z(1), ())


def sc_wall2d():
    """2D ball toward an axis-aligned wall at x=5, fast enough to tunnel in one
    discrete step; exact CCD reflects it at the exact impact time instead."""
    return ([Ball(vec(0, 0), Z(0), vec(10, 0), 1)], Z(1), Z(1), ((0, Z(5)),))


SCENES = {
    "head2d": sc_head2d,
    "oblique2d": sc_oblique2d,
    "inelastic2d": sc_inelastic2d,
    "oblique3d": sc_oblique3d,
    "wall2d": sc_wall2d,
}


def run(name):
    bodies, dt, e, walls = SCENES[name]()
    forces = [Vec([Z(0)] * bodies[0].x.dim()) for _ in bodies]
    return D.step(bodies, forces, dt, e, walls)


if __name__ == "__main__":
    for name in sorted(SCENES):
        print(name, D.state_digest(run(name)))
